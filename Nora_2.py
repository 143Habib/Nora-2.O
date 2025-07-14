import requests
import pyttsx3
import pyautogui
import psutil
import os
import speech_recognition as sr
# ------------------- CONFIG -------------------
GROQ_API_KEY = "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"  
GROQ_MODEL = "llama3-8b-8192"
# ----------------------------------------------

engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    return input("Type your command here: ")
def listen2():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙️ Listening...")
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
            command = recognizer.recognize_google(audio)
            print("🗣️ You said:", command)
            return command
        except sr.UnknownValueError:
            print("⚠️ Could not understand audio.")
            speak("Sorry, I didn't catch that.")
            return ""
        except sr.RequestError:
            print("⚠️ Could not request results.")
            speak("There was a problem with the recognition service.")
            return ""
        except sr.WaitTimeoutError:
            print("⌛ Listening timed out.")
            speak("I didn't hear anything.")
            return ""
def ask_groq(prompt):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }
    body = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=body)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error contacting Groq API: {str(e)}"

def execute_command(command):
    command = command.lower()
    if command in ["hi", "hello", "hey"]:
        return "Hi there!"
    elif "open notepad" in command:
        os.system("notepad")
        return "Opening Notepad."
    elif "open calculator" in command:
        os.system("calc")
        return "Opening Calculator."
    elif "screenshot" in command:
        pyautogui.screenshot("screenshot.png")
        return "Screenshot taken."
    elif "battery" in command:
        battery = psutil.sensors_battery()
        if battery:
            return f"Battery is at {battery.percent}%"
        else:
            return "Sorry, could not get battery information."
    elif command in ["exit", "quit", "bye", "goodbye"]:
        speak("Goodbye! Have a nice day.")
        exit(0)
    return None

def main():
    print("Hello,I am Nora.How can I help You?")
    speak("Hello.....I am Nora.....How can I help You?")
    print("How would you like to give your command?")
    y = input("Type 'T' to write or 'L' to speak: ")
    if y=='T':
        while True:
         user_input1 = listen()
         local_response = execute_command(user_input1)
         if local_response:
            print("Nora:", local_response)
            speak(local_response)
         else:
            response = ask_groq(user_input1)
            print("Nora:", response)
            speak(response)
    else:
        while True:
         user_input = listen2()
         if not user_input.strip():
            continue
         local_response = execute_command(user_input)
         if local_response:
            speak(local_response)
         else:
            print("Let me think...")
            speak("Let me think...")
            response = ask_groq(user_input)
            print("Nora:",response)
            speak(response)

if __name__ == "__main__":
    main()
