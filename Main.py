from PyQt5.QtWidgets import QApplication
from Frontend.GUI import (
    MainWindow,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus
)

from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os
import sys

env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")  # Fixed typo: Changed `egt` to `get`
DefaultMessage = f'''{Username} : Hello {Assistantname}, How are you?
{Assistantname} : Welcome {Username} . I am doing well. How may I help you?'''
subprocesses = []  # Fixed typo: Changed `subprocess` to `subprocesses`
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]

def ShowDefaultChatIfNoChats():
    File = open(r'Data\ChatLog.json', "r", encoding='utf-8')
    if len(File.read()) < 5:
        with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:  # Fixed typo: 'Databse' to 'Database'
            file.write("")
        with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as file:
            file.write(DefaultMessage)

def ReadChatLogJson():
    with open(r'Data\ChatLog.json', 'r', encoding='utf-8') as file:
        chatLog_data = json.load(file)
    return chatLog_data

def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatLog = ""
    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatLog += f"User: {entry['content']}\n"  # Fixed variable name: Changed `formatted_chatlog` to `formatted_chatLog`
        elif entry["role"] == "assistant":
            formatted_chatLog += f"Assistant: {entry['content']}\n"
    formatted_chatLog = formatted_chatLog.replace("User", Username + " ")
    formatted_chatLog = formatted_chatLog.replace("Assistant", Assistantname + " ")
    with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatLog))

def ShowChatOnGUI():
    File = open(TempDirectoryPath('Database.data'), "r", encoding='utf-8')
    Data = File.read()
    if len(str(Data)) > 0:
        lines = Data.split('\n')
        result = '\n'.join(lines)
        File.close()
        File = open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8')  # Fixed indentation
        File.write(result)  # Added missing write operation
        File.close()

def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ShowChatOnGUI()

InitialExecution()

def MainExecution():
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""

    SetAssistantStatus("Listening...")
    Query = SpeechRecognition()
    ShowTextToScreen(f"{Username}: {Query}")
    SetAssistantStatus("Thinking...")
    Decision = FirstLayerDMM(Query)

    print("")
    print(f"Decision: {Decision}")
    print("")

    G = any([i for i in Decision if i.startswith("general")])
    R = any([i for i in Decision if i.startswith("realtime")])

    Merged_query = " and ".join(
        [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
    )

    for queries in Decision:
        if TaskExecution == False:
            if any(queries.startswith(func) for func in Functions):
                 
                run(Automation(list(Decision)))

    if ImageExecution:
        with open(r"Frontend\Files\ImageGeneration.data", "w") as file:
            file.write(f"{ImageGenerationQuery},True")
        try:
            p1 = subprocess.Popen(['python', r'Backend\ImageGeneration.py'],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  stdin=subprocess.PIPE, shell=False)
            subprocesses.append(p1)  # Fixed typo: Changed `subprocess` to `subprocesses`
        except Exception as e:
            print(f"Error starting ImageGeneration.py: {e}")

    if G and R or R:
        SetAssistantStatus("Searching...")
        Answer = RealtimeSearchEngine(QueryModifier(Merged_query))  # Fixed typo: Changed `Mearged_query` to `Merged_query`
        ShowTextToScreen(f"{Assistantname}: {Answer}")
        SetAssistantStatus("Answering...")
        TextToSpeech(Answer)
        return True 
    
    else:
        for Queries in Decision:
            if "general" in Queries:
                SetAssistantStatus("Thinking...")
                QueryFinal = Queries.replace("general", "")
                Answer = ChatBot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname}: {Answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)
                return True
            elif "realtime" in Queries:
                SetAssistantStatus("Searching...")
                QueryFinal = Queries.replace("realtime", "")
                Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname}: {Answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)
                return True
            elif "exit" in Queries:
                QueryFinal = "Okay, Bye!"
                Answer = ChatBot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname}: {Answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)  #Changed 
                SetAssistantStatus("Answering...")
                os._exit(1)  # Changed `os.exit` to `os._exit`
                

def FirstThread():
    while True:
        CurrentStatus = GetMicrophoneStatus()
        if CurrentStatus == "True":
            MainExecution()
        else:
            AIStatus = GetAssistantStatus()
            if "Available..." in AIStatus:  # Fixed typo: Changed "Availabe..." to "Available..."
                sleep(0.1)
            else:
                SetAssistantStatus("Available...")  # Fixed typo: Changed "Availabe..." to "Available..."

def SecondThread():
    # Create the QApplication instance  
    app = QApplication(sys.argv)
    
    # Initialize and show the MainWindow (or GUI class)
    window = MainWindow()
    window.show()  # Assuming MainWindow has a show() method
    
    # Start the application's event loop
    sys.exit(app.exec_())  # Ensures the program doesn't exit immediately

if __name__ == "__main__":
    thread2 = threading.Thread(target=FirstThread, daemon=True)
    thread2.start()
    SecondThread()
