# NORA 2.O - Voice & Text Based AI Assistant

NORA 2.O is a sophisticated Python-based AI assistant featuring a modern GUI interface that combines local system control with cloud-based AI intelligence through the Groq LLaMA API. The assistant provides seamless interaction through both text input and voice commands with real-time speech synthesis.

## Features

### Core Interface
- Modern GUI: Dark-themed interface with cyberpunk-style design using Tkinter
- Dual Input Methods: Type commands or use voice input with microphone toggle
- Real-time Response Display: Scrollable text area showing conversation history with timestamps
- Status Indicators: Visual feedback for listening, processing, and ready states
- Audio Controls: Mute/unmute toggle for speech synthesis

### Voice Capabilities
- Speech Recognition: Google Speech Recognition API for voice-to-text conversion
- Text-to-Speech: pyttsx3 engine with markdown formatting cleanup
- Continuous Listening: Toggle-based voice input with visual feedback
- Smart Text Processing: Automatic removal of markdown formatting for natural speech

### System Integration
- Application Launching:
  - Notepad, Calculator, Camera
  - Chrome browser, Microsoft Word, Excel
  - File Explorer, Task Manager, Control Panel
- System Information:
  - Battery status and percentage
  - Current time and date
  - Screenshot capture functionality
- Web Integration:
  - Google Maps navigation
  - Web search functionality
  - Automatic URL opening

### AI Intelligence
- Groq LLaMA Integration: Fallback to cloud-based AI for complex queries
- Local Command Processing: Instant response for system commands
- Natural Language Understanding: Handles various phrasings for the same commands
- Context-Aware Responses: Intelligent greeting and conversation management

## Installation

### Prerequisites
Install the required Python packages:

```bash
pip install tkinter requests pyttsx3 pyautogui psutil SpeechRecognition pyaudio
```

### For Windows users with pyaudio issues:
```bash
pip install pipwin
pipwin install pyaudio
```

## Configuration

### API Setup
Update your Groq API credentials in the script:

```python
GROQ_API_KEY = "your_groq_api_key_here"
GROQ_MODEL = "llama3-8b-8192"
```

### Getting a Groq API Key
1. Visit [Groq Console](https://console.groq.com/)
2. Create an account or sign in
3. Navigate to API Keys section
4. Generate a new API key
5. Replace the placeholder in the code

## Usage

### Starting the Application
1. Save the code as `nora.py`
2. Run the script:
   ```bash
   python nora.py
   ```
3. The GUI will launch with NORA ready to assist

### Interaction Methods

#### Text Commands
- Type your command in the input field
- Press Enter or click "Execute"
- View responses in the main display area

#### Voice Commands
- Click "🎙️ Voice Input" to start listening
- Speak your command clearly
- Click "⏹️ Stop Listening" to end voice input
- Commands are automatically processed after recognition

### Supported Commands

#### System Applications
- "Open notepad" - Launches Windows Notepad
- "Open calculator" - Opens Calculator app
- "Open camera" - Starts Windows Camera
- "Open chrome" - Launches Chrome browser
- "Open word/excel" - Opens Microsoft Office applications
- "Open file explorer" - Opens Windows Explorer
- "Open task manager" - Launches Task Manager
- "Control panel" - Opens Windows Control Panel

#### System Information
- "Battery status" - Shows battery percentage and charging status
- "What time is it" - Displays current time
- "What date is it" - Shows today's date
- "Take screenshot" - Captures and saves screen image

#### Web Services
- "Search for [query]" - Opens Google search
- "Navigate to [location]" - Opens Google Maps directions
- "Map of [location]" - Shows location on Google Maps

#### General Queries
- Any other input is processed through the Groq LLaMA API
- Natural language conversations supported
- Context-aware responses

## Interface Controls

### Main Buttons
- Execute: Process typed commands
- 🎙️ Voice Input: Toggle voice recognition
- Clear: Clear the response display
- 🔊 Mute: Toggle text-to-speech audio

### Status Indicators
- Green "Ready": System ready for input
- Yellow "Listening": Voice input active
- Orange "Processing": Command being processed
- Orange "Thinking": AI generating response

## Technical Architecture

### Voice Processing Pipeline
1. Microphone input capture
2. Ambient noise adjustment
3. Google Speech API recognition
4. Command processing and routing
5. Response generation and speech synthesis

### Command Routing System
1. Local command pattern matching
2. System-level command execution
3. Groq API fallback for unknown queries
4. Response formatting and display

### Error Handling
- Graceful handling of API timeouts
- Voice recognition error recovery
- System command failure reporting
- Network connectivity issues management

## Customization

### Adding New Commands
Extend the `execute_command` method with new command patterns:

```python
elif "your command" in command:
    try:
        # Your command logic here
        return "Command executed successfully"
    except Exception as e:
        return f"Error: {str(e)}"
```

### Modifying UI Theme
Update colors and fonts in the `setup_ui` method:
- Background colors: `bg="#000000"`
- Text colors: `fg="#00ffe0"`
- Fonts: `font=("Orbitron", 26)`

## Troubleshooting

### Common Issues
- Microphone not working: Check system permissions and default audio device
- Commands not recognized: Ensure clear speech and proper microphone setup
- API errors: Verify Groq API key and internet connection
- Application launch failures: Check if target applications are installed

### Performance Tips
- Use specific command phrases for better recognition
- Speak clearly and at moderate pace for voice input
- Keep the GUI responsive by avoiding blocking operations
- Monitor system resources for optimal performance

## Security Considerations

- Store API keys securely (consider environment variables)
- Be cautious with system command execution
- Validate user input for security
- Consider rate limiting for API calls

## License

This project is designed for personal and educational use. Please comply with:
- Groq API usage policies and rate limits
- Google Speech Recognition service terms
- Local system security guidelines
- Open source library licenses

## Future Enhancements

Potential improvements could include:
- Plugin system for custom commands
- Database integration for conversation history
- Multi-language support
- Advanced voice commands with wake words
- Integration with more cloud AI services
- Mobile companion app connectivity
