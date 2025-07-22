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
import json
import hashlib

# ------------------- CONFIG -------------------
GROQ_API_KEY = "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"  
GROQ_MODEL = "llama3-8b-8192"

# Add your image generation API key here (choose one of these services)
OPENAI_API_KEY = "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"  # For DALL-E
STABILITY_API_KEY = "sk-r82g2W6XRfBKHJ2GZYFJx0MNi65DRc0Y5rFEejsG1KvwV4pD"  # For Stable Diffusion
HUGGINGFACE_API_KEY = "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"  # For Hugging Face models

USERS_FILE = "users.json"
# ----------------------------------------------

# ---------------- User Manager ---------------- #
class UserManager:
    def __init__(self):
        self.users_file = USERS_FILE
        self.ensure_users_file()

    def ensure_users_file(self):
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w') as f:
                json.dump({}, f)

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def load_users(self):
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except:
            return {}

    def save_users(self, users):
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=2)

    def register_user(self, username, name, phone, password):
        users = self.load_users()
        if username in users:
            return False, "Username already exists!"

        users[username] = {
            "name": name,
            "phone": phone,
            "password": self.hash_password(password),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.save_users(users)
        return True, "Registration successful!"

    def login_user(self, username, password):
        users = self.load_users()
        if username not in users:
            return False, "Username not found!"
        if users[username]["password"] != self.hash_password(password):
            return False, "Incorrect password!"
        return True, users[username]

# ---------------- Login Window ---------------- #
class LoginWindow:
    def __init__(self, callback):
        self.callback = callback
        self.user_manager = UserManager()
        self.root = tk.Tk()
        self.root.title("NORA - Login")
        self.root.geometry("500x600")
        self.root.configure(bg="#000000")
        self.root.resizable(False, False)

        # Center the window
        self.root.geometry("+{}+{}".format(
            (self.root.winfo_screenwidth() // 2) - 250,
            (self.root.winfo_screenheight() // 2) - 300
        ))

        self.main_frame = tk.Frame(self.root, bg="#000000")
        self.main_frame.pack(expand=True, fill="both", padx=30, pady=20)
        self.setup_ui()

    def setup_ui(self):
        title = tk.Label(self.root, text="N.O.R.A", font=("Orbitron", 32, "bold"),
                         fg="#00ffe0", bg="#000000")
        title.pack(pady=30)

        subtitle = tk.Label(self.root, text="Neural Operations & Response Assistant",
                            font=("Consolas", 12), fg="#00ffcc", bg="#000000")
        subtitle.pack(pady=(0, 20))

        self.show_login_form()

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_login_form(self):
        self.clear_frame()

        tk.Label(self.main_frame, text="Login to NORA",
                 font=("Consolas", 18, "bold"), fg="#00ffe0", bg="#000000").pack(pady=20)

        tk.Label(self.main_frame, text="Username:", font=("Consolas", 12),
                 fg="#00ffcc", bg="#000000").pack(pady=(5, 2))
        self.login_username = tk.Entry(self.main_frame, font=("Consolas", 12),
                                       bg="#111111", fg="#ffffff", insertbackground='white')
        self.login_username.pack(pady=(0, 10))

        tk.Label(self.main_frame, text="Password:", font=("Consolas", 12),
                 fg="#00ffcc", bg="#000000").pack(pady=(5, 2))
        self.login_password = tk.Entry(self.main_frame, font=("Consolas", 12),
                                       bg="#111111", fg="#ffffff", show="*", insertbackground='white')
        self.login_password.pack(pady=(0, 20))

        # Bind Enter key to login
        self.login_username.bind('<Return>', lambda event: self.login())
        self.login_password.bind('<Return>', lambda event: self.login())

        tk.Button(self.main_frame, text="Login", command=self.login,
                  bg="#00ffe0", fg="black", font=("Consolas", 14, "bold"),
                  width=20, height=2).pack(pady=10)

        tk.Button(self.main_frame, text="New User? Register",
                  command=self.show_register_form,
                  bg="#ff6b00", fg="white", font=("Consolas", 12),
                  width=20).pack(pady=5)

        self.login_username.focus()

    def show_register_form(self):
        self.clear_frame()

        tk.Label(self.main_frame, text="Register for NORA",
                 font=("Consolas", 18, "bold"), fg="#00ffe0", bg="#000000").pack(pady=20)

        # Full Name
        tk.Label(self.main_frame, text="Full Name:", font=("Consolas", 12),
                 fg="#00ffcc", bg="#000000").pack(pady=(5, 2))
        self.reg_name = tk.Entry(self.main_frame, font=("Consolas", 12),
                                 bg="#111111", fg="#ffffff", insertbackground='white')
        self.reg_name.pack(pady=(0, 10))

        # Phone Number
        tk.Label(self.main_frame, text="Phone Number:", font=("Consolas", 12),
                 fg="#00ffcc", bg="#000000").pack(pady=(5, 2))
        self.reg_phone = tk.Entry(self.main_frame, font=("Consolas", 12),
                                  bg="#111111", fg="#ffffff", insertbackground='white')
        self.reg_phone.pack(pady=(0, 10))

        # Username
        tk.Label(self.main_frame, text="Username:", font=("Consolas", 12),
                 fg="#00ffcc", bg="#000000").pack(pady=(5, 2))
        self.reg_username = tk.Entry(self.main_frame, font=("Consolas", 12),
                                     bg="#111111", fg="#ffffff", insertbackground='white')
        self.reg_username.pack(pady=(0, 10))

        # Password
        tk.Label(self.main_frame, text="Password:", font=("Consolas", 12),
                 fg="#00ffcc", bg="#000000").pack(pady=(5, 2))
        self.reg_password = tk.Entry(self.main_frame, font=("Consolas", 12),
                                     bg="#111111", fg="#ffffff", show="*", insertbackground='white')
        self.reg_password.pack(pady=(0, 10))

        # Confirm Password
        tk.Label(self.main_frame, text="Confirm Password:", font=("Consolas", 12),
                 fg="#00ffcc", bg="#000000").pack(pady=(5, 2))
        self.reg_confirm = tk.Entry(self.main_frame, font=("Consolas", 12),
                                    bg="#111111", fg="#ffffff", show="*", insertbackground='white')
        self.reg_confirm.pack(pady=(0, 20))

        # Register Button
        tk.Button(self.main_frame, text="Register", command=self.register,
                  bg="#00ff80", fg="black", font=("Consolas", 14, "bold"),
                  width=20, height=2).pack(pady=10)

        # Back to Login Button
        tk.Button(self.main_frame, text="Back to Login", command=self.show_login_form,
                  bg="#4000ff", fg="white", font=("Consolas", 12),
                  width=20).pack(pady=5)

        self.reg_name.focus()

    def validate_registration(self):
        name = self.reg_name.get().strip()
        phone = self.reg_phone.get().strip()
        username = self.reg_username.get().strip()
        password = self.reg_password.get().strip()
        confirm = self.reg_confirm.get().strip()

        if not all([name, phone, username, password, confirm]):
            return False, "All fields are required!"

        if len(name) < 2:
            return False, "Name must be at least 2 characters!"
        if len(phone) < 10 or not phone.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            return False, "Invalid phone number!"
        if len(username) < 3:
            return False, "Username must be at least 3 characters!"
        if len(password) < 6:
            return False, "Password must be at least 6 characters!"
        if password != confirm:
            return False, "Passwords do not match!"

        return True, "Valid"

    def register(self):
        valid, message = self.validate_registration()
        if not valid:
            messagebox.showerror("Registration Error", message)
            return

        name = self.reg_name.get().strip()
        phone = self.reg_phone.get().strip()
        username = self.reg_username.get().strip()
        password = self.reg_password.get().strip()

        success, message = self.user_manager.register_user(username, name, phone, password)

        if success:
            messagebox.showinfo("Success", message)
            self.show_login_form()
            self.root.after(100, lambda: self.login_username.insert(0, username))
        else:
            messagebox.showerror("Error", message)

    def login(self):
        username = self.login_username.get().strip()
        password = self.login_password.get().strip()

        if not username or not password:
            messagebox.showerror("Login Error", "Please enter both username and password!")
            return

        success, user = self.user_manager.login_user(username, password)
        if success:
            messagebox.showinfo("Login Success", f"Welcome back, {user['name']}!")
            self.root.destroy()
            self.callback(user)
        else:
            messagebox.showerror("Login Failed", user)

    def run(self):
        self.root.mainloop()

# ---------------- Main NORA Interface ---------------- #
class NoraInterface:
    def __init__(self, user_info):
        self.user_info = user_info
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
        # ======= Top Section with Title and User Info =======
        top_frame = tk.Frame(self.root, bg="#000000")
        top_frame.pack(pady=10, fill="x")
        
        title = tk.Label(top_frame, text="N.O.R.A", 
                        font=("Orbitron", 26), fg="#00ffe0", bg="#000000")
        title.pack()
        
        # User info and logout
        user_frame = tk.Frame(top_frame, bg="#000000")
        user_frame.pack(pady=5)
        
        user_label = tk.Label(user_frame, text=f"Welcome, {self.user_info['name']}", 
                             font=("Consolas", 12), fg="#00ffcc", bg="#000000")
        user_label.pack(side="left")
        
        logout_btn = tk.Button(user_frame, text="Logout", command=self.logout,
                              bg="#ff4444", fg="white", font=("Consolas", 10), width=10)
        logout_btn.pack(side="right", padx=(20, 0))
        
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
        
        # Create text widget with scrollbar
        text_frame = tk.Frame(left_frame, bg="#000000")
        text_frame.pack(fill="both", expand=True, pady=10)
        
        self.response_text = tk.Text(text_frame, height=15, width=80, 
                                   bg="#0d0d0d", fg="#00ffcc", font=("Consolas", 11), 
                                   borderwidth=2, relief="solid")
        self.response_text.pack(side="left", fill="both", expand=True)
        
        # Add scrollbar for text
        scrollbar = tk.Scrollbar(text_frame, command=self.response_text.yview)
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
        self.log_message("NORA", f"Hello {self.user_info['name']}! I am NORA. How can I help you today? I can also generate images for you!")
        self.speak(f"Hello {self.user_info['name']}! I am NORA. How can I help you today? I can also generate images for you!")
    
    def logout(self):
        """Handle logout functionality"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.root.destroy()
            # Restart the login window
            LoginWindow(launch_nora_interface).run()
    
    def log_message(self, sender, message):
        self.response_text.insert(tk.END, f"{sender}: {message}\n")
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
        with sr.Microphone() as source:
            self.status_label.config(text="Status: Listening...", fg="#ff8000")
            self.voice_btn.config(text="🛑 Stop Listening")
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                command = recognizer.recognize_google(audio)
                self.command_entry.delete(0, tk.END)
                self.command_entry.insert(0, command)
                self.run_command()
            except sr.WaitTimeoutError:
                self.log_message("NORA", "Listening timed out. Try again.")
                self.speak("Listening timed out. Try again.")
            except sr.UnknownValueError:
                self.log_message("NORA", "Sorry, I didn't catch that.")
                self.speak("Sorry, I didn't catch that.")
            except Exception as e:
                self.log_message("SYSTEM", f"Voice input error: {str(e)}")
                self.speak("Voice input error occurred.")
            finally:
                self.status_label.config(text="Status: Ready", fg="#00ff00")
                self.voice_btn.config(text="🎙️ Voice Input")
                self.is_listening = False

    def toggle_voice_input(self):
        if not self.is_listening:
            self.is_listening = True
            threading.Thread(target=self.listen_voice, daemon=True).start()
        else:
            self.is_listening = False
            self.status_label.config(text="Status: Ready", fg="#00ff00")
            self.voice_btn.config(text="🎙️ Voice Input")

    def process_local_command(self, command):
        """Process local commands before sending to AI"""
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
        
        return None  # Return None if no local command was processed

    def run_command(self):
        command = self.command_entry.get().strip()
        if not command:
            self.log_message("NORA", "Please enter a command.")
            self.speak("Please enter a command.")
            return

        self.log_message("USER", command)
        self.status_label.config(text="Status: Processing...", fg="#ff8000")
        self.root.update()
        
        # First try to process as local command
        local_response = self.process_local_command(command)
        
        if local_response:
            # Local command was processed
            self.log_message("NORA", local_response)
            self.speak(local_response)
            self.status_label.config(text="Status: Ready", fg="#00ff00")
            self.command_entry.delete(0, tk.END)  # Clear the command entry
        else:
            # No local command found, send to AI
            self.status_label.config(text="Status: Thinking...", fg="#ff8000")
            def query_ai():
                try:
                    headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {GROQ_API_KEY}"
                    }
                    data = {
                        "model": GROQ_MODEL,
                        "messages": [
                            {"role": "system", "content": "You are NORA, a helpful AI assistant."},
                            {"role": "user", "content": command}
                        ]
                    }
                    response = requests.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers=headers,
                        json=data,
                        timeout=60
                    )

                    if response.status_code == 200:
                        result = response.json()
                        reply = result['choices'][0]['message']['content']
                        self.root.after(0, lambda: self.log_message("NORA", reply))
                        self.root.after(0, lambda: self.speak(reply))
                        self.root.after(0, lambda: self.command_entry.delete(0, tk.END))
                    else:
                        self.root.after(0, lambda: self.log_message("NORA", "Failed to get response."))
                        self.root.after(0, lambda: self.speak("Sorry, I couldn't process that."))
                except Exception as e:
                    self.root.after(0, lambda: self.log_message("SYSTEM", f"Error: {str(e)}"))
                    self.root.after(0, lambda: self.speak("An error occurred."))
                finally:
                    self.root.after(0, lambda: self.status_label.config(text="Status: Ready", fg="#00ff00"))

            threading.Thread(target=query_ai, daemon=True).start()
    
    def run(self):
        self.root.mainloop()

# ---------------- Launcher ---------------- #
def launch_nora_interface(user_info):
    NoraInterface(user_info).run()

# Start the application
if __name__ == "__main__":
    LoginWindow(launch_nora_interface).run()
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
import json
import hashlib

# ------------------- CONFIG -------------------
GROQ_API_KEY = "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"  
GROQ_MODEL = "llama3-8b-8192"

# Add your image generation API key here (choose one of these services)
OPENAI_API_KEY = "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"  # For DALL-E
STABILITY_API_KEY = "sk-r82g2W6XRfBKHJ2GZYFJx0MNi65DRc0Y5rFEejsG1KvwV4pD"  # For Stable Diffusion
HUGGINGFACE_API_KEY = "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"  # For Hugging Face models

USERS_FILE = "users.json"
# ----------------------------------------------

# ---------------- User Manager ---------------- #
class UserManager:
    def __init__(self):
        self.users_file = USERS_FILE
        self.ensure_users_file()

    def ensure_users_file(self):
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w') as f:
                json.dump({}, f)

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def load_users(self):
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except:
            return {}

    def save_users(self, users):
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=2)

    def register_user(self, username, name, phone, password):
        users = self.load_users()
        if username in users:
            return False, "Username already exists!"

        users[username] = {
            "name": name,
            "phone": phone,
            "password": self.hash_password(password),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.save_users(users)
        return True, "Registration successful!"

    def login_user(self, username, password):
        users = self.load_users()
        if username not in users:
            return False, "Username not found!"
        if users[username]["password"] != self.hash_password(password):
            return False, "Incorrect password!"
        return True, users[username]

# ---------------- Login Window ---------------- #
class LoginWindow:
    def __init__(self, callback):
        self.callback = callback
        self.user_manager = UserManager()
        self.root = tk.Tk()
        self.root.title("NORA - Login")
        self.root.geometry("500x600")
        self.root.configure(bg="#000000")
        self.root.resizable(False, False)

        # Center the window
        self.root.geometry("+{}+{}".format(
            (self.root.winfo_screenwidth() // 2) - 250,
            (self.root.winfo_screenheight() // 2) - 300
        ))

        self.main_frame = tk.Frame(self.root, bg="#000000")
        self.main_frame.pack(expand=True, fill="both", padx=30, pady=20)
        self.setup_ui()

    def setup_ui(self):
        title = tk.Label(self.root, text="N.O.R.A", font=("Orbitron", 32, "bold"),
                         fg="#00ffe0", bg="#000000")
        title.pack(pady=30)

        subtitle = tk.Label(self.root, text="Neural Operations & Response Assistant",
                            font=("Consolas", 12), fg="#00ffcc", bg="#000000")
        subtitle.pack(pady=(0, 20))

        self.show_login_form()

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_login_form(self):
        self.clear_frame()

        tk.Label(self.main_frame, text="Login to NORA",
                 font=("Consolas", 18, "bold"), fg="#00ffe0", bg="#000000").pack(pady=20)

        tk.Label(self.main_frame, text="Username:", font=("Consolas", 12),
                 fg="#00ffcc", bg="#000000").pack(pady=(5, 2))
        self.login_username = tk.Entry(self.main_frame, font=("Consolas", 12),
                                       bg="#111111", fg="#ffffff", insertbackground='white')
        self.login_username.pack(pady=(0, 10))

        tk.Label(self.main_frame, text="Password:", font=("Consolas", 12),
                 fg="#00ffcc", bg="#000000").pack(pady=(5, 2))
        self.login_password = tk.Entry(self.main_frame, font=("Consolas", 12),
                                       bg="#111111", fg="#ffffff", show="*", insertbackground='white')
        self.login_password.pack(pady=(0, 20))

        # Bind Enter key to login
        self.login_username.bind('<Return>', lambda event: self.login())
        self.login_password.bind('<Return>', lambda event: self.login())

        tk.Button(self.main_frame, text="Login", command=self.login,
                  bg="#00ffe0", fg="black", font=("Consolas", 14, "bold"),
                  width=20, height=2).pack(pady=10)

        tk.Button(self.main_frame, text="New User? Register",
                  command=self.show_register_form,
                  bg="#ff6b00", fg="white", font=("Consolas", 12),
                  width=20).pack(pady=5)

        self.login_username.focus()

    def show_register_form(self):
        self.clear_frame()

        tk.Label(self.main_frame, text="Register for NORA",
                 font=("Consolas", 18, "bold"), fg="#00ffe0", bg="#000000").pack(pady=20)

        # Full Name
        tk.Label(self.main_frame, text="Full Name:", font=("Consolas", 12),
                 fg="#00ffcc", bg="#000000").pack(pady=(5, 2))
        self.reg_name = tk.Entry(self.main_frame, font=("Consolas", 12),
                                 bg="#111111", fg="#ffffff", insertbackground='white')
        self.reg_name.pack(pady=(0, 10))

        # Phone Number
        tk.Label(self.main_frame, text="Phone Number:", font=("Consolas", 12),
                 fg="#00ffcc", bg="#000000").pack(pady=(5, 2))
        self.reg_phone = tk.Entry(self.main_frame, font=("Consolas", 12),
                                  bg="#111111", fg="#ffffff", insertbackground='white')
        self.reg_phone.pack(pady=(0, 10))

        # Username
        tk.Label(self.main_frame, text="Username:", font=("Consolas", 12),
                 fg="#00ffcc", bg="#000000").pack(pady=(5, 2))
        self.reg_username = tk.Entry(self.main_frame, font=("Consolas", 12),
                                     bg="#111111", fg="#ffffff", insertbackground='white')
        self.reg_username.pack(pady=(0, 10))

        # Password
        tk.Label(self.main_frame, text="Password:", font=("Consolas", 12),
                 fg="#00ffcc", bg="#000000").pack(pady=(5, 2))
        self.reg_password = tk.Entry(self.main_frame, font=("Consolas", 12),
                                     bg="#111111", fg="#ffffff", show="*", insertbackground='white')
        self.reg_password.pack(pady=(0, 10))

        # Confirm Password
        tk.Label(self.main_frame, text="Confirm Password:", font=("Consolas", 12),
                 fg="#00ffcc", bg="#000000").pack(pady=(5, 2))
        self.reg_confirm = tk.Entry(self.main_frame, font=("Consolas", 12),
                                    bg="#111111", fg="#ffffff", show="*", insertbackground='white')
        self.reg_confirm.pack(pady=(0, 20))

        # Register Button
        tk.Button(self.main_frame, text="Register", command=self.register,
                  bg="#00ff80", fg="black", font=("Consolas", 14, "bold"),
                  width=20, height=2).pack(pady=10)

        # Back to Login Button
        tk.Button(self.main_frame, text="Back to Login", command=self.show_login_form,
                  bg="#4000ff", fg="white", font=("Consolas", 12),
                  width=20).pack(pady=5)

        self.reg_name.focus()

    def validate_registration(self):
        name = self.reg_name.get().strip()
        phone = self.reg_phone.get().strip()
        username = self.reg_username.get().strip()
        password = self.reg_password.get().strip()
        confirm = self.reg_confirm.get().strip()

        if not all([name, phone, username, password, confirm]):
            return False, "All fields are required!"

        if len(name) < 2:
            return False, "Name must be at least 2 characters!"
        if len(phone) < 10 or not phone.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            return False, "Invalid phone number!"
        if len(username) < 3:
            return False, "Username must be at least 3 characters!"
        if len(password) < 6:
            return False, "Password must be at least 6 characters!"
        if password != confirm:
            return False, "Passwords do not match!"

        return True, "Valid"

    def register(self):
        valid, message = self.validate_registration()
        if not valid:
            messagebox.showerror("Registration Error", message)
            return

        name = self.reg_name.get().strip()
        phone = self.reg_phone.get().strip()
        username = self.reg_username.get().strip()
        password = self.reg_password.get().strip()

        success, message = self.user_manager.register_user(username, name, phone, password)

        if success:
            messagebox.showinfo("Success", message)
            self.show_login_form()
            self.root.after(100, lambda: self.login_username.insert(0, username))
        else:
            messagebox.showerror("Error", message)

    def login(self):
        username = self.login_username.get().strip()
        password = self.login_password.get().strip()

        if not username or not password:
            messagebox.showerror("Login Error", "Please enter both username and password!")
            return

        success, user = self.user_manager.login_user(username, password)
        if success:
            messagebox.showinfo("Login Success", f"Welcome back, {user['name']}!")
            self.root.destroy()
            self.callback(user)
        else:
            messagebox.showerror("Login Failed", user)

    def run(self):
        self.root.mainloop()

# ---------------- Main NORA Interface ---------------- #
class NoraInterface:
    def __init__(self, user_info):
        self.user_info = user_info
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
        # ======= Top Section with Title and User Info =======
        top_frame = tk.Frame(self.root, bg="#000000")
        top_frame.pack(pady=10, fill="x")
        
        title = tk.Label(top_frame, text="N.O.R.A", 
                        font=("Orbitron", 26), fg="#00ffe0", bg="#000000")
        title.pack()
        
        # User info and logout
        user_frame = tk.Frame(top_frame, bg="#000000")
        user_frame.pack(pady=5)
        
        user_label = tk.Label(user_frame, text=f"Welcome, {self.user_info['name']}", 
                             font=("Consolas", 12), fg="#00ffcc", bg="#000000")
        user_label.pack(side="left")
        
        logout_btn = tk.Button(user_frame, text="Logout", command=self.logout,
                              bg="#ff4444", fg="white", font=("Consolas", 10), width=10)
        logout_btn.pack(side="right", padx=(20, 0))
        
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
        
        # Create text widget with scrollbar
        text_frame = tk.Frame(left_frame, bg="#000000")
        text_frame.pack(fill="both", expand=True, pady=10)
        
        self.response_text = tk.Text(text_frame, height=15, width=80, 
                                   bg="#0d0d0d", fg="#00ffcc", font=("Consolas", 11), 
                                   borderwidth=2, relief="solid")
        self.response_text.pack(side="left", fill="both", expand=True)
        
        # Add scrollbar for text
        scrollbar = tk.Scrollbar(text_frame, command=self.response_text.yview)
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
        self.log_message("NORA", f"Hello {self.user_info['name']}! I am NORA. How can I help you today?")
        self.speak(f"Hello {self.user_info['name']}! I am NORA. How can I help you today?")
    
    def logout(self):
        """Handle logout functionality"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.root.destroy()
            # Restart the login window
            LoginWindow(launch_nora_interface).run()
    
    def log_message(self, sender, message):
        self.response_text.insert(tk.END, f"{sender}: {message}\n")
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
        with sr.Microphone() as source:
            self.status_label.config(text="Status: Listening...", fg="#ff8000")
            self.voice_btn.config(text="🛑 Stop Listening")
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                command = recognizer.recognize_google(audio)
                self.command_entry.delete(0, tk.END)
                self.command_entry.insert(0, command)
                self.run_command()
            except sr.WaitTimeoutError:
                self.log_message("NORA", "Listening timed out. Try again.")
                self.speak("Listening timed out. Try again.")
            except sr.UnknownValueError:
                self.log_message("NORA", "Sorry, I didn't catch that.")
                self.speak("Sorry, I didn't catch that.")
            except Exception as e:
                self.log_message("SYSTEM", f"Voice input error: {str(e)}")
                self.speak("Voice input error occurred.")
            finally:
                self.status_label.config(text="Status: Ready", fg="#00ff00")
                self.voice_btn.config(text="🎙️ Voice Input")
                self.is_listening = False

    def toggle_voice_input(self):
        if not self.is_listening:
            self.is_listening = True
            threading.Thread(target=self.listen_voice, daemon=True).start()
        else:
            self.is_listening = False
            self.status_label.config(text="Status: Ready", fg="#00ff00")
            self.voice_btn.config(text="🎙️ Voice Input")

    def process_local_command(self, command):
        """Process local commands before sending to AI"""
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
        
        return None  # Return None if no local command was processed

    def run_command(self):
        command = self.command_entry.get().strip()
        if not command:
            self.log_message("NORA", "Please enter a command.")
            self.speak("Please enter a command.")
            return

        self.log_message("USER", command)
        self.status_label.config(text="Status: Processing...", fg="#ff8000")
        self.root.update()
        
        # First try to process as local command
        local_response = self.process_local_command(command)
        
        if local_response:
            # Local command was processed
            self.log_message("NORA", local_response)
            self.speak(local_response)
            self.status_label.config(text="Status: Ready", fg="#00ff00")
            self.command_entry.delete(0, tk.END)  # Clear the command entry
        else:
            # No local command found, send to AI
            self.status_label.config(text="Status: Thinking...", fg="#ff8000")
            def query_ai():
                try:
                    headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {GROQ_API_KEY}"
                    }
                    data = {
                        "model": GROQ_MODEL,
                        "messages": [
                            {"role": "system", "content": "You are NORA, a helpful AI assistant."},
                            {"role": "user", "content": command}
                        ]
                    }
                    response = requests.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers=headers,
                        json=data,
                        timeout=60
                    )

                    if response.status_code == 200:
                        result = response.json()
                        reply = result['choices'][0]['message']['content']
                        self.root.after(0, lambda: self.log_message("NORA", reply))
                        self.root.after(0, lambda: self.speak(reply))
                        self.root.after(0, lambda: self.command_entry.delete(0, tk.END))
                    else:
                        self.root.after(0, lambda: self.log_message("NORA", "Failed to get response."))
                        self.root.after(0, lambda: self.speak("Sorry, I couldn't process that."))
                except Exception as e:
                    self.root.after(0, lambda: self.log_message("SYSTEM", f"Error: {str(e)}"))
                    self.root.after(0, lambda: self.speak("An error occurred."))
                finally:
                    self.root.after(0, lambda: self.status_label.config(text="Status: Ready", fg="#00ff00"))

            threading.Thread(target=query_ai, daemon=True).start()
    
    def run(self):
        self.root.mainloop()

# ---------------- Launcher ---------------- #
def launch_nora_interface(user_info):
    NoraInterface(user_info).run()

# Start the application
if __name__ == "__main__":
    LoginWindow(launch_nora_interface).run()
