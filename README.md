# Nora 2.O - Voice & Text Based AI Assistant

Nora 2.O is a Python-based AI assistant that can interact with users through both text and voice. Powered by the Groq LLaMA model API, Nora can understand and respond to natural language input, open basic applications, and perform system-level tasks like taking screenshots or checking battery status.

## Features

* Text Command Input: Type your queries and receive intelligent responses.
* Voice Recognition: Speak to Nora and get responses in real-time.
* Text-to-Speech: Nora replies with both spoken words and printed text.
* System Controls:

  * Open Notepad
  * Open Calculator
  * Take Screenshots
  * Check Battery Percentage
* Fallback to Groq LLaMA for natural language queries.

## Requirements

Before running the assistant, install the following Python packages:

```
pip install requests pyttsx3 pyautogui psutil SpeechRecognition pyaudio
```

If you face issues installing pyaudio, use:

```
pip install pipwin
pipwin install pyaudio
```

## Usage

1. Save the script to a Python file (e.g., `nora.py`).
2. Run the script:

```
python nora.py
```

3. Choose input mode:

   * Type `T` to give commands via text.
   * Type `L` to speak your commands.

## Configuration

Update your Groq API key and model name in the script:

```
GROQ_API_KEY = "your_api_key_here"
GROQ_MODEL = "llama3-8b-8192"
```

## Notes

* Ensure your microphone is enabled for voice input.
* The assistant handles basic command execution locally. If a command is unknown, it will query the Groq API for a response.

## License

This project is for personal or educational use. Please comply with Groq's API usage policies.


