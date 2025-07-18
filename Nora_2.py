import tkinter as tk
from tkinter import ttk
import webbrowser
import requests
import pyttsx3
import pyautogui
import psutil
import os
import speech_recognition as sr
import threading
from datetime import datetime
import re
import subprocess
# ------------------- CONFIG -------------------
GROQ_API_KEY = "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"  
GROQ_MODEL = "llama3-8b-8192"
# ----------------------------------------------

class NoraInterface:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("N.O.R.A Interface")
        self.root.geometry("1200x700")
        self.root.config(bg="#000000")
        
        # Initialize TTS engine
        self.engine = pyttsx3.init()
        self.is_listening = False
        
        self.setup_ui()
        
    def setup_ui(self):
        # ======= Top Label =======
        title = tk.Label(self.root, text="N.O.R.A", 
                        font=("Orbitron", 26), fg="#00ffe0", bg="#000000")
        title.pack(pady=10)
        
        # ======= Status Frame =======
        status_frame = tk.Frame(self.root, bg="#000000")
        status_frame.pack(pady=5)
        
        self.status_label = tk.Label(status_frame, text="Status: Ready", 
                                   fg="#00ff00", bg="#000000", font=("Consolas", 12))
        self.status_label.pack()
        
        # ======= Info Frame =======
        info_frame = tk.Frame(self.root, bg="#000000")
        info_frame.pack(pady=20)
        
        # Response Box
        response_label = tk.Label(info_frame, text="Assistant Response:", 
                                fg="#00ffe0", bg="#000000", font=("Consolas", 14))
        response_label.grid(row=0, column=0, sticky='w')
        
        self.response_text = tk.Text(info_frame, height=12, width=100, 
                                   bg="#0d0d0d", fg="#00ffcc", font=("Consolas", 11), 
                                   borderwidth=2, relief="solid")
        self.response_text.grid(row=1, column=0, padx=10, pady=10)
        
        # Add scrollbar
        scrollbar = tk.Scrollbar(info_frame, command=self.response_text.yview)
        scrollbar.grid(row=1, column=1, sticky='ns')
        self.response_text.config(yscrollcommand=scrollbar.set)
        
        # ======= Command Input Box =======
        command_label = tk.Label(self.root, text="Enter Command:", 
                                fg="#00ffe0", bg="#000000", font=("Consolas", 14))
        command_label.pack()
        
        self.command_entry = tk.Entry(self.root, width=80, font=("Consolas", 14), 
                                    bg="#111111", fg="#ffffff", insertbackground='white')
        self.command_entry.pack(pady=10)
        self.command_entry.bind('<Return>', lambda event: self.run_command())
        
        # ======= Control Buttons =======
        button_frame = tk.Frame(self.root, bg="#000000")
        button_frame.pack(pady=10)
        
        # Execute Button
        execute_btn = tk.Button(button_frame, text="Execute", command=self.run_command, 
                              bg="#00ffe0", fg="black", font=("Consolas", 13), width=12)
        execute_btn.grid(row=0, column=0, padx=5)
        
        # Voice Input Button
        self.voice_btn = tk.Button(button_frame, text="🎙️ Voice Input", 
                                 command=self.toggle_voice_input, 
                                 bg="#ff6b00", fg="white", font=("Consolas", 13), width=15)
        self.voice_btn.grid(row=0, column=1, padx=5)
        
        # Clear Button
        clear_btn = tk.Button(button_frame, text="Clear", command=self.clear_response, 
                            bg="#ff0040", fg="white", font=("Consolas", 13), width=12)
        clear_btn.grid(row=0, column=2, padx=5)
        
        # Mute/Unmute Button
        self.mute_btn = tk.Button(button_frame, text="🔊 Mute", command=self.toggle_mute, 
                                bg="#4000ff", fg="white", font=("Consolas", 13), width=12)
        self.mute_btn.grid(row=0, column=3, padx=5)
        
        self.is_muted = False
        # Welcome message
        self.log_message("NORA", "Hello! I am NORA. How can I help you today?")
        self.speak("Hello! I am NORA. How can I help you today?")
    
    def log_message(self, sender, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.response_text.insert(tk.END, f"[{timestamp}] {sender}: {message}\n")
        self.response_text.see(tk.END)
        self.root.update()
    
    def clean_text_for_speech(self, text):
        """Clean text for TTS by removing markdown formatting and other symbols"""
        # Remove markdown bold/italic formatting
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # **bold** -> bold
        text = re.sub(r'\*([^*]+)\*', r'\1', text)      # *italic* -> italic
        text = re.sub(r'_([^_]+)_', r'\1', text)        # _underline_ -> underline
        text = re.sub(r'__([^_]+)__', r'\1', text)      # __bold__ -> bold
        
        # Remove markdown headers
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        
        # Remove markdown links [text](url) -> text
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        
        # Remove markdown code blocks and inline code
        text = re.sub(r'```[^`]*```', '', text, flags=re.DOTALL)
        text = re.sub(r'`([^`]+)`', r'\1', text)
        
        # Remove bullet points and list markers
        text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
        
        # Remove extra whitespace and clean up
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def speak(self, text):
        if not self.is_muted:
            def speak_thread():
                # Clean the text before speaking
                clean_text = self.clean_text_for_speech(text)
                self.engine.say(clean_text)
                self.engine.runAndWait()
            threading.Thread(target=speak_thread, daemon=True).start()
    
    def toggle_mute(self):
        self.is_muted = not self.is_muted
        if self.is_muted:
            self.mute_btn.config(text="🔇 Unmute")
        else:
            self.mute_btn.config(text="🔊 Mute")
    
    def clear_response(self):
        self.response_text.delete(1.0, tk.END)
    
    def listen_voice(self):
        recognizer = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                self.status_label.config(text="Status: Listening...", fg="#ffff00")
                self.root.update()
                
                recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)
                
                self.status_label.config(text="Status: Processing...", fg="#ff8000")
                self.root.update()
                
                command = recognizer.recognize_google(audio)
                self.log_message("USER", f"Voice: {command}")
                
                self.status_label.config(text="Status: Ready", fg="#00ff00")
                return command
                
        except sr.UnknownValueError:
            self.log_message("SYSTEM", "Could not understand audio")
            self.status_label.config(text="Status: Ready", fg="#00ff00")
            return ""
        except sr.RequestError as e:
            self.log_message("SYSTEM", f"Recognition service error: {str(e)}")
            self.status_label.config(text="Status: Ready", fg="#00ff00")
            return ""
        except sr.WaitTimeoutError:
            self.log_message("SYSTEM", "Listening timed out")
            self.status_label.config(text="Status: Ready", fg="#00ff00")
            return ""
        except Exception as e:
            self.log_message("SYSTEM", f"Voice recognition error: {str(e)}")
            self.status_label.config(text="Status: Ready", fg="#00ff00")
            return ""
    
    def toggle_voice_input(self):
        if not self.is_listening:
            self.is_listening = True
            self.voice_btn.config(text="⏹️ Stop Listening", bg="#ff0000")
            threading.Thread(target=self.voice_input_loop, daemon=True).start()
        else:
            self.is_listening = False
            self.voice_btn.config(text="🎙️ Voice Input", bg="#ff6b00")
    
    def voice_input_loop(self):
        while self.is_listening:
            command = self.listen_voice()
            if command.strip():
                # Update the command entry with the voice input
                self.root.after(0, lambda: self.command_entry.delete(0, tk.END))
                self.root.after(0, lambda: self.command_entry.insert(0, command))
                # Process the command
                self.root.after(0, lambda: self.process_command(command))
    
    def ask_groq(self, prompt):
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
            response = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                                   headers=headers, json=body)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error contacting Groq API: {str(e)}"
    
    def execute_command(self, command):
        command = command.lower().strip()
        
        # Greeting commands
        if any(word in command for word in ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]):
            return "Hi there! How can I assist you today?"
        
        # Open applications
        elif any(phrase in command for phrase in ["open notepad", "launch notepad", "start notepad"]):
            try:
                os.system("notepad")
                return "Opening Notepad."
            except Exception as e:
                return f"Error opening Notepad: {str(e)}"
        
        elif any(phrase in command for phrase in ["open camera", "launch camera", "start camera"]):
            try:
                os.system("start microsoft.windows.camera:")
                return "Opening Camera."
            except Exception as e:
                return f"Error opening Camera: {str(e)}"
        
        elif any(phrase in command for phrase in ["open calculator", "launch calculator", "start calculator"]):
            try:
                os.system("calc")
                return "Opening Calculator."
            except Exception as e:
                return f"Error opening Calculator: {str(e)}"
        
        # Additional applications
        elif any(phrase in command for phrase in ["open chrome", "launch chrome", "start chrome"]):
            try:
                os.system("start chrome")
                return "Opening Chrome browser."
            except Exception as e:
                return f"Error opening Chrome: {str(e)}"
        
        elif any(phrase in command for phrase in ["open word", "launch word", "start word"]):
            try:
                os.system("start winword")
                return "Opening Microsoft Word."
            except Exception as e:
                return f"Error opening Word: {str(e)}"
        
        elif any(phrase in command for phrase in ["open excel", "launch excel", "start excel"]):
            try:
                os.system("start excel")
                return "Opening Microsoft Excel."
            except Exception as e:
                return f"Error opening Excel: {str(e)}"
        
        elif any(phrase in command for phrase in ["open file explorer", "open explorer", "launch explorer"]):
            try:
                os.system("start explorer")
                return "Opening File Explorer."
            except Exception as e:
                return f"Error opening File Explorer: {str(e)}"
        
        elif any(phrase in command for phrase in ["open task manager", "launch task manager", "start task manager"]):
            try:
                os.system("taskmgr")
                return "Opening Task Manager."
            except Exception as e:
                return f"Error opening Task Manager: {str(e)}"
        
        elif "control panel" in command:
            try:
              subprocess.Popen("control")
              return "Opening Control Panel."
            except Exception as e:
              return f"Failed to open Control Panel: {e}"
            except Exception as e:
                return f"Error opening Control Panel: {str(e)}"
        
        # System commands
        elif any(phrase in command for phrase in ["take screenshot", "screenshot", "capture screen"]):
            try:
                pyautogui.screenshot("screenshot.png")
                return "Screenshot taken and saved as screenshot.png"
            except Exception as e:
                return f"Error taking screenshot: {str(e)}"
        
        elif any(phrase in command for phrase in ["battery", "battery status", "battery level"]):
            try:
                battery = psutil.sensors_battery()
                if battery:
                    plugged = "plugged in" if battery.power_plugged else "not plugged in"
                    return f"Battery is at {battery.percent}% and {plugged}"
                else:
                    return "Sorry, could not get battery information."
            except Exception as e:
                return f"Error getting battery info: {str(e)}"
        
        # Time and date
        elif any(phrase in command for phrase in ["time?", "what time is it", "current time"]):
            current_time = datetime.now().strftime("%H:%M:%S")
            return f"Current time is {current_time}"
        
        elif any(phrase in command for phrase in ["date", "what date is it", "current date", "today's date"]):
            current_date = datetime.now().strftime("%Y-%m-%d")
            return f"Today's date is {current_date}"
        
        # Maps and directions
        elif any(phrase in command for phrase in ["map", "direction", "navigate to", "show me the way to"]):
            # Extract location from command
            place = command
            for phrase in ["show me the direction to", "navigate to", "show me the way to", "map of", "directions to"]:
                place = place.replace(phrase, "").strip()
            
            if place:
                try:
                    url = f"https://www.google.com/maps/dir/?api=1&destination={place.replace(' ', '+')}"
                    webbrowser.open(url)
                    return f"Opened Google Maps for: {place}"
                except Exception as e:
                    return f"Error opening maps: {str(e)}"
            else:
                return "Please specify a location for the map."
        
        # Search commands
        elif any(phrase in command for phrase in ["search for", "google", "look up"]):
            search_query = command
            for phrase in ["search for", "google", "look up"]:
                search_query = search_query.replace(phrase, "").strip()
            
            if search_query:
                try:
                    url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
                    webbrowser.open(url)
                    return f"Searching Google for: {search_query}"
                except Exception as e:
                    return f"Error opening search: {str(e)}"
            else:
                return "Please specify what you want to search for."
        
        # Exit commands
        elif any(phrase in command for phrase in ["exit", "quit", "bye", "goodbye", "shut down", "close"]):
            self.speak("Goodbye! Have a nice day.")
            self.root.after(1000, self.root.destroy)  # Delay to allow speech to finish
            return "Goodbye! Have a nice day."
        
        return None
    
    def process_command(self, command):
        if not command.strip():
            return
            
        self.log_message("USER", command)
        
        # Try local command first
        local_response = self.execute_command(command)
        if local_response:
            self.log_message("NORA", local_response)
            self.speak(local_response)
        else:
            # Use Groq API for general queries
            self.status_label.config(text="Status: Thinking...", fg="#ff8000")
            self.root.update()
            
            response = self.ask_groq(command)
            self.log_message("NORA", response)
            self.speak(response)
            
            self.status_label.config(text="Status: Ready", fg="#00ff00")
    
    def run_command(self):
        cmd = self.command_entry.get().strip()
        if cmd:
            self.command_entry.delete(0, tk.END)
            self.process_command(cmd)
    
    def run(self):
        self.root.mainloop()

# ======= Main Execution =======
if __name__ == "__main__":
    app = NoraInterface()
    app.run()
