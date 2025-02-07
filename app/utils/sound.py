import pyttsx3
import time
import subprocess

engine = pyttsx3.init()

# Set up engine properties once (prevents re-initialization overhead)
engine.setProperty('rate', 130)  # Slower speed for clarity (Default is ~200)
engine.setProperty('volume', 1.0)  # Max volume

# Try selecting a clearer voice
voices = engine.getProperty('voices')
if voices:
    engine.setProperty('voice', voices[0].id)  # Pick the first available voice

def speak_text(text: str):
    if not text.strip():
        return  # Avoid speaking empty text
    
    engine.say(text)
    engine.runAndWait()
    
    # Add a short pause to ensure the text is fully spoken
    time.sleep(0.5)

def text_to_speech(text):
    """Convert text to speech using Piper."""
    command = ["piper", "--model", "/usr/share/piper/en_US-lessac.onnx", "--text", text]
    subprocess.run(command)

if __name__ == "__main__":
    text_to_speech("Hello, I am your assistant. How can I help you?")
    
# speak_text("Hello World")