import sqlite3
import re
import shlex
import subprocess
import time
import pyautogui
import pyttsx3
# Assuming speak function is defined in main.py

def speak(text):
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)  # Use the first available voice
    engine.setProperty('rate', 175) 
    print(text) # Adjust the speaking rate (words per minute)
    engine.say(text)
    engine.runAndWait()

def extract_yt_term(command):
    pattern = r'play\s+(.*?)\s+on\s+youtube'
    match = re.search(pattern, command, re.IGNORECASE)
    return match.group(1) if match else None 

def remove_words(input_string, words_to_remove):
    words = input_string.split()
    filtered_words = [word for word in words if word.lower() not in words_to_remove]
    return ' '.join(filtered_words)

def findContact(query):
    ASSISTANT_NAME = "voice assistant"
    words_to_remove = [ASSISTANT_NAME, 'make', 'a', 'to', 'phone', 'call', 'send', 'message', 'whatsapp', 'video']
    query = remove_words(query, words_to_remove).strip().lower()

    try:
        con = sqlite3.connect("voiceAssistant.db")
        cursor = con.cursor()

        cursor.execute("SELECT mobile_no FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", ('%' + query + '%', query + '%'))
        results = cursor.fetchall()

        if results:
            mobile_number_str = str(results[0][0])
            if not mobile_number_str.startswith('+91'):
                mobile_number_str = '+91' + mobile_number_str
            return mobile_number_str, query
        else:
            speak('Contact not found in contacts')
            return None, None

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        speak('An error occurred while accessing contacts')
        return None, None

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'con' in locals():
            con.close()

def whatsApp(mobile_no, message, flag, name):
    try:
        if flag == 'message':
            target_tab = 12
            jarvis_message = f"Message sent successfully to {name}"
        elif flag == 'call':
            target_tab = 7
            message = ''
            jarvis_message = f"Calling {name}"
        else:
            target_tab = 6
            message = ''
            jarvis_message = f"Starting video call with {name}"

        # Encode the message for URL
        encoded_message = shlex.quote(message)

        # Construct the URL
        whatsapp_url = f"whatsapp://send?phone={mobile_no}&text={encoded_message}"

        # Construct the full command
        full_command = f'start "" "{whatsapp_url}"'

        # Open WhatsApp with the constructed URL using cmd.exe
        subprocess.run(full_command, shell=True)
        time.sleep(5)
        subprocess.run(full_command, shell=True)
        
        pyautogui.hotkey('ctrl', 'f')
        for i in range(1, target_tab):
            pyautogui.hotkey('tab')
        
        pyautogui.hotkey('enter')
        speak(jarvis_message)

    except Exception as e:
        print(f"Error in WhatsApp function: {e}")
        speak('An error occurred while sending WhatsApp message')
