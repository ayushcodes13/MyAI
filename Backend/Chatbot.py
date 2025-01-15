from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values(".env")

Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize Groq client
client = Groq(api_key=GroqAPIKey)

# Define system behavior
System = f"""
Hello, I am {Username}. You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question. ***
*** Reply in only English, even if the question is in Hindi, reply in English. ***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

SystemChatBot = [
    {"role": "system", "content": System}
]

# Load chat history or initialize it
try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
except FileNotFoundError:
    messages = []
    with open(r"Data\ChatLog.json", "w") as f:
        dump(messages, f)

# Function to get real-time information
def RealtimeInformation():
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")

    data = f"Please use this real-time information if needed.\n"
    data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
    data += f"Time: {hour} hours : {minute} minutes : {second} seconds"
    return data

# Function to modify and clean the response
def AnswerModifier(Answer):
    lines = Answer.split("\n")
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = "\n".join(non_empty_lines)
    return modified_answer

# Function to process user queries
def ChatBot(Query):
    """ This function sends the user's query to the chatbot and returns the AI's response. """
    try:
        with open(r"Data\ChatLog.json", "r") as f:
            messages = load(f)

        # Append user query to chat history
        messages.append({"role": "user", "content": f"{Query}"})

        # Send query to the model
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": RealtimeInformation()}] + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        # Collect response from model
        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        # Clean the response
        Answer = Answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})

        # Save updated chat history
        with open(r"Data\ChatLog.json", "w") as f:
            dump(messages, f, indent=4)

        return AnswerModifier(Answer)

    except Exception as e:
        print(f"Error: {e}")
        with open(r"Data\ChatLog.json", "w") as f:
            dump([], f, indent=4)
        return "Sorry, something went wrong. Please try again."

# Main program loop
if __name__ == "__main__":
    print("Welcome to the Jarvis AI Chatbot!")
    print("Type your questions below. Type 'exit' or 'quit' to end the chat.")

    while True:
        try:
            user_input = input("Enter Your Question: ").strip()

            # Handle empty input
            if not user_input:
                print("Please enter a valid question.")
                continue

            # Handle exit commands
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("Goodbye!")
                break

            # Call the ChatBot function
            response = ChatBot(user_input)
            print(f"Jarvis AI: {response}")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
