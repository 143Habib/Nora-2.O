import tkinter as tk
from tkinter import ttk, messagebox
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
from PIL import Image, ImageTk
import io
import base64

# ------------------- CONFIG -------------------
GROQ_API_KEY = "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"  
GROQ_MODEL = "llama3-8b-8192"

# Add your image generation API key here 
OPENAI_API_KEY = "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"  # For DALL-E
STABILITY_API_KEY = "sk-Q7VR50R8lspjkXB9WhDVgMfFr15lIoLiuAI9zhbhAEPs8Ocl"  # For Stable Diffusion
HUGGINGFACE_API_KEY = "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"  # For Hugging Face models
# ----------------------------------------------

class NoraInterface:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("N.O.R.A Interface")
        self.root.geometry("1400x800")  # Made wider for image display
        self.root.config(bg="#000000")
        
        # Initialize TTS engine
        self.engine = pyttsx3.init()
        self.is_listening = False
        self.current_image = None
        
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
        
        # ======= Main Content Frame =======
        main_frame = tk.Frame(self.root, bg="#000000")
        main_frame.pack(pady=20, fill="both", expand=True)
        
        # ======= Left Side - Text Response =======
        left_frame = tk.Frame(main_frame, bg="#000000")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Response Box
        response_label = tk.Label(left_frame, text="Assistant Response:", 
                                fg="#00ffe0", bg="#000000", font=("Consolas", 14))
        response_label.pack(anchor="w")
        
        self.response_text = tk.Text(left_frame, height=15, width=80, 
                                   bg="#0d0d0d", fg="#00ffcc", font=("Consolas", 11), 
                                   borderwidth=2, relief="solid")
        self.response_text.pack(pady=10, fill="both", expand=True)
        
        # Add scrollbar for text
        scrollbar = tk.Scrollbar(left_frame, command=self.response_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.response_text.config(yscrollcommand=scrollbar.set)
        
        # ======= Right Side - Image Display =======
        right_frame = tk.Frame(main_frame, bg="#000000")
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Image Box
        image_label = tk.Label(right_frame, text="Generated Images:", 
                             fg="#00ffe0", bg="#000000", font=("Consolas", 14))
        image_label.pack(anchor="w")
        
        # Image display area
        self.image_frame = tk.Frame(right_frame, bg="#0d0d0d", borderwidth=2, relief="solid")
        self.image_frame.pack(pady=10, fill="both", expand=True)
        
        self.image_label = tk.Label(self.image_frame, text="No image generated yet", 
                                  fg="#00ffcc", bg="#0d0d0d", font=("Consolas", 12))
        self.image_label.pack(expand=True)
        
        # Image control buttons
        img_button_frame = tk.Frame(right_frame, bg="#000000")
        img_button_frame.pack(pady=5)
        
        save_img_btn = tk.Button(img_button_frame, text="Save Image", 
                               command=self.save_current_image, 
                               bg="#00ff80", fg="black", font=("Consolas", 11), width=12)
        save_img_btn.pack(side="left", padx=5)
        
        clear_img_btn = tk.Button(img_button_frame, text="Clear Image", 
                                command=self.clear_image, 
                                bg="#ff4080", fg="white", font=("Consolas", 11), width=12)
        clear_img_btn.pack(side="left", padx=5)
        
        # ======= Command Input Box =======
        command_label = tk.Label(self.root, text="Enter Command:", 
                                fg="#00ffe0", bg="#000000", font=("Consolas", 14))
        command_label.pack()
        
        self.command_entry = tk.Entry(self.root, width=100, font=("Consolas", 14), 
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
        
        # Generate Image Button
        generate_img_btn = tk.Button(button_frame, text="🎨 Generate Image", 
                                   command=self.generate_image_from_entry, 
                                   bg="#ff8000", fg="white", font=("Consolas", 13), width=15)
        generate_img_btn.grid(row=0, column=4, padx=5)
        
        self.is_muted = False
        # Welcome message
        self.log_message("NORA", "Hello! I am NORA. How can I help you today? I can also generate images for you!")
        self.speak("Hello! I am NORA. How can I help you today? I can also generate images for you!")
    
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
    
    def clear_image(self):
        self.image_label.configure(image="", text="No image generated yet")
        self.current_image = None
    
    def save_current_image(self):
        if self.current_image:
            filename = f"nora_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            self.current_image.save(filename)
            self.log_message("NORA", f"Image saved as {filename}")
            self.speak(f"Image saved as {filename}")
        else:
            self.log_message("NORA", "No image to save")
            self.speak("No image to save")
    
    def generate_image_from_entry(self):
        """Generate image from the current text in the command entry"""
        prompt = self.command_entry.get().strip()
        if prompt:
            self.generate_image(prompt)
        else:
            self.log_message("NORA", "Please enter a description for the image")
            self.speak("Please enter a description for the image")
    
    def generate_image_openai(self, prompt):
        """Generate image using OpenAI DALL-E API"""
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPENAI_API_KEY}"
            }
            
            data = {
                "model": "dall-e-3",
                "prompt": prompt,
                "n": 1,
                "size": "1024x1024",
                "response_format": "b64_json"
            }
            
            response = requests.post(
                "https://api.openai.com/v1/images/generations",
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                image_data = base64.b64decode(result['data'][0]['b64_json'])
                return Image.open(io.BytesIO(image_data))
            else:
                return None
                
        except Exception as e:
            self.log_message("SYSTEM", f"OpenAI API error: {str(e)}")
            return None
    
    def generate_image_stability(self, prompt):
        """Generate image using Stability AI API"""
        try:
            url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
            
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {STABILITY_API_KEY}",
            }
            
            data = {
                "text_prompts": [
                    {
                        "text": prompt,
                        "weight": 1
                    }
                ],
                "cfg_scale": 7,
                "height": 1024,
                "width": 1024,
                "steps": 20,
                "samples": 1,
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                image_data = base64.b64decode(result['artifacts'][0]['base64'])
                return Image.open(io.BytesIO(image_data))
            else:
                return None
                
        except Exception as e:
            self.log_message("SYSTEM", f"Stability AI API error: {str(e)}")
            return None
    
    def generate_image_huggingface(self, prompt):
        """Generate image using Hugging Face API"""
        try:
            API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
            headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
            
            data = {"inputs": prompt}
            
            response = requests.post(API_URL, headers=headers, json=data, timeout=60)
            
            if response.status_code == 200:
                return Image.open(io.BytesIO(response.content))
            else:
                return None
                
        except Exception as e:
            self.log_message("SYSTEM", f"Hugging Face API error: {str(e)}")
            return None
    
    def generate_image(self, prompt):
        """Main image generation function"""
        self.log_message("USER", f"Generate image: {prompt}")
        self.status_label.config(text="Status: Generating image...", fg="#ff8000")
        self.root.update()
        
        def generate_thread():
            try:
                image = None
                
                # Try different APIs in order of preference
                if OPENAI_API_KEY != "your_openai_api_key_here":
                    image = self.generate_image_openai(prompt)
                
                if not image and STABILITY_API_KEY != "your_stability_api_key_here":
                    image = self.generate_image_stability(prompt)
                
                if not image and HUGGINGFACE_API_KEY != "your_huggingface_api_key_here":
                    image = self.generate_image_huggingface(prompt)
                
                if image:
                    # Resize image to fit display area
                    display_size = (400, 400)
                    image.thumbnail(display_size, Image.Resampling.LANCZOS)
                    
                    # Convert to PhotoImage for display
                    photo = ImageTk.PhotoImage(image)
                    
                    # Update UI in main thread
                    self.root.after(0, lambda: self.display_image(photo, image))
                    self.root.after(0, lambda: self.log_message("NORA", f"Image generated successfully for: {prompt}"))
                    self.root.after(0, lambda: self.speak("Image generated successfully"))
                else:
                    self.root.after(0, lambda: self.log_message("NORA", "Failed to generate image. Please check your API keys."))
                    self.root.after(0, lambda: self.speak("Failed to generate image. Please check your API keys."))
                
            except Exception as e:
                self.root.after(0, lambda: self.log_message("SYSTEM", f"Image generation error: {str(e)}"))
                self.root.after(0, lambda: self.speak("Image generation failed"))
            
            finally:
                self.root.after(0, lambda: self.status_label.config(text="Status: Ready", fg="#00ff00"))
        
        threading.Thread(target=generate_thread, daemon=True).start()
    
    def display_image(self, photo, original_image):
        """Display the generated image in the UI"""
        self.image_label.configure(image=photo, text="")
        self.image_label.image = photo  # Keep a reference
        self.current_image = original_image
    
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
        
        # Image generation commands
        if any(phrase in command for phrase in ["generate image", "create image", "make image", "draw image", "generate picture", "create picture", "make picture"]):
            # Extract the description from the command
            image_prompt = command
            for phrase in ["generate image of", "create image of", "make image of", "draw image of", "generate picture of", "create picture of", "make picture of", "generate image", "create image", "make image", "draw image", "generate picture", "create picture", "make picture"]:
                image_prompt = image_prompt.replace(phrase, "").strip()
            
            if image_prompt:
                self.generate_image(image_prompt)
                return f"Generating image: {image_prompt}"
            else:
                return "Please specify what image you want me to generate."
        
        # Greeting commands
        elif any(word in command for word in ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]):
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
