import pyttsx3

engine = pyttsx3.init()

def speak_text(text: str):
    # Optimize for speed and efficiency
    engine.setProperty('rate', 150)  # Adjust speed (default is ~200)
    engine.setProperty('volume', 1.0)  # Set volume to max
    
    # Choose a lightweight voice
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)  # Select the first available voice

    engine.say(text)
    engine.runAndWait()

# Example usage

