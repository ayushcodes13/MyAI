from googlesearch import search
from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values
import yfinance as yf  # Install this library using pip if not already installed.

# Load environment variables
env_vars = dotenv_values(".env")

Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

client = Groq(api_key=GroqAPIKey)

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***"""

# Function to load or create chat log
def load_chat_log():
    try:
        with open(r"Data\ChatLog.json", "r") as f:
            return load(f)
    except FileNotFoundError:
        with open(r"Data\ChatLog.json", "w") as f:
            dump([], f)
        return []

messages = load_chat_log()

# Function to modify the answer
def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

# Function to fetch real-time stock prices
def get_stock_price(stock_name):
    try:
        stock = yf.Ticker(stock_name)
        current_price = stock.info['regularMarketPrice']
        currency = stock.info['currency']
        return f"The current stock price of {stock_name} is {current_price} {currency}."
    except Exception as e:
        return f"Unable to fetch the stock price for {stock_name}. Error: {e}"

# Real-time information function
def Information():
    current_date_time = datetime.datetime.now()
    return f"""Use this real-time information if needed:
Day: {current_date_time.strftime("%A")}
Date: {current_date_time.strftime("%d %B %Y")}
Time: {current_date_time.strftime("%H:%M:%S")}"""

# Real-time Search Engine
def RealtimeSearchEngine(prompt):
    global messages

    if "stock price" in prompt.lower():
        # Extract stock name from the prompt
        stock_name = prompt.split("of")[-1].strip()
        return get_stock_price(stock_name)
    
    # Use Groq for general queries
    try:
        messages.append({"role": "user", "content": prompt})
        SystemChatBot = [{"role": "system", "content": System}, {"role": "system", "content": Information()}]

        # Generate AI-based responses
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + messages,
            temperature=0.7,
            max_tokens=2048,
        )

        Answer = completion.choices[0].message.content
        messages.append({"role": "assistant", "content": Answer})

        # Save updated messages
        with open(r"Data\ChatLog.json", "w") as f:
            dump(messages, f, indent=4)
        return AnswerModifier(Answer)

    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred. Please try again later."

# Main loop
if __name__ == "__main__":
    print("Welcome to the Jarvis AI Chatbot!")
    print("Type your queries below. Type 'exit' or 'quit' to end the chat.")
    
    while True:
        prompt = input("Enter your query: ").strip()
        if prompt.lower() in ['exit', 'quit']:
            print("Ending the chat.")
            break
        elif not prompt:
            print("Please enter a valid query.")
        else:
            response = RealtimeSearchEngine(prompt)
            print(f"Jarvis: {response}")
