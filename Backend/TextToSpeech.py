import pygame 
import random
import asyncio
import edge_tts
import os
from dotenv import dotenv_values

env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice")

async def TextToAudioFile(text) -> None:
    file_path = r"Data\speech.mp3" 
    
    if os.path.exists(file_path):
        os.remove(file_path)
        
    communicate = edge_tts.Communicate(text, AssistantVoice , pitch='+5Hz' , rate='+13%')
    await communicate.save(r'Data\speech.mp3')
        
def TTS(Text, func=lambda r=None: True):
    while True:
        try:
            asyncio.run(TextToAudioFile(Text))
            
            pygame.mixer.init()
            pygame.mixer.music.load(r"Data\speech.mp3")
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                if func() == False:
                    break
                pygame.time.Clock().tick(10)
                
            return True 
        
        except Exception as e:
            print(f"Error in TTS: {e}")
            
        finally:
            try:
                func(False)
                pygame.mixer.music.stop()
                pygame.mixer.quit()
                
            except Exception as e:
                print(f"Error in finally block: {e}")
                
def TextToSpeech(Text, func=lambda r=None: True):
    Data = str(Text).split(".")
    
    responses = [
        "Do you want me to read the rest of the chats sent by me on my own mam?",
        "The rest of the text is now on the chat screen, mam, please check it.",
        "You can see the rest of the text on the chat screen, mam.",
        "The remaining part of the text is now on the chat screen, mam.",
        "Mam, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, mam.",
        "Mam, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, mam.",
        "The next part of the text is on the chat screen, mam.",
        "Mam, please check the chat screen for more information.",
        "There's more text on the chat screen for you, mam.",
        "Mam, take a look at the chat screen for additional text.",
        "You'll find more to read on the chat screen, mam.",
        "Mam, check the chat screen for the rest of the text.",
        "The chat screen has the rest of the text, mam.",
        "There's more to see on the chat screen, mam, please look.",
        "Mam, the chat screen holds the continuation of the text.",
        "You'll find the complete answer on the chat screen, kindly check it out mam.",
        "Please review the chat screen for the rest of the text, mam.",
        "mam, look at the chat screen for the complete answer."
    ]
    
    if len(Data) > 4 and len(Text) >= 250:
        TTS("".join(Data[:2]) + "." + random.choice(responses), func)
    else:
        TTS(Text, func)
        
if __name__ == "__main__":
    while True:
        TextToSpeech(input("Enter the text: "))
