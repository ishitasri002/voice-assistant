
import shlex
import sqlite3
import subprocess
from flask import Flask, jsonify, render_template, request
import pyautogui
import pyttsx3
import speech_recognition as sr
import time 
import os
import pywhatkit as kit
import re



app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

def speak(text):
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)  # Use the first available voice
    engine.setProperty('rate', 175) 
    print(text) # Adjust the speaking rate (words per minute)
    engine.say(text)
    engine.runAndWait()

def recognize_speech():
    r = sr.Recognizer()

    with sr.Microphone() as source:
        print('Listening...')
        r.adjust_for_ambient_noise(source)  # Adjust the recognizer sensitivity to ambient noise
        audio = r.listen(source, 10,6)  # Listen to the user's input

    try:
        print('Recognizing...')
        text = r.recognize_google(audio)  # Recognize the user's speech using Google Speech Recognition
        print('Recognized text:', text)  # Print the recognized text to the terminal
        return text
    except sr.UnknownValueError:
        return "Sorry, I couldn't understand what you said"
    except sr.RequestError as e:
        return f"Sorry, an error occurred during speech recognition: {e}"
    
def openCommand(query):
    ASSISTANT_NAME = "voice assistant" 

    query = query.lower()  # Convert to lowercase
    query = query.replace(ASSISTANT_NAME, "").strip()  # Remove assistant name and leading/trailing spaces
    query = query.replace("open", "").strip()  # Remove "open" keyword and leading/trailing spaces

    if query != "":
        speak("Opening " + query)
        os.system('start ' + query)  # Use 'start' command to open files/applications
    else:
        speak("Application or file not found")
        print("No application or file specified in the command.")

def PlayYoutube(query):
    search_term = extract_yt_term(query)
    speak("Playing " + search_term + " on YouTube")
    kit.playonyt(search_term)


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




@app.route('/takecommand', methods=['POST'])
def take_command():
    text = recognize_speech()
    speak(text) 
    time.sleep(1) # Speak the recognized text
    return jsonify({'text': text})


@app.route('/allCommands', methods=['POST'])
def all_commands():
    try:
        query = recognize_speech()
        print(query)
        if "open" in query:
            openCommand(query)
        elif "on YouTube":
            PlayYoutube(query)
        elif "send message" in query or "phone call" in query or "video call" in query:
            from engine.helper import findContact, whatsApp
            flag = ""
            contact_no, name = findContact(query)
            if(contact_no != 0):

                if "send message" in query:
                    flag = 'message'
                    speak("what message to send")
                    query = take_command()
                    
                elif "phone call" in query:
                    flag = 'call'
                else:
                    flag = 'video call'
                    
                whatsApp(contact_no, query, flag, name)
        else:
            print("ni karuga")
            
    except:
        print("ni karuga")


      

    return jsonify({'query': query})


if __name__ == "__main__":
    app.run(debug=True)
