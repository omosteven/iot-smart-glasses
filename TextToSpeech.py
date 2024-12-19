import pyttsx3

class TextToSpeech:
    def __init__(self, rate: int = 200, voice: str = None):
        self.engine = pyttsx3.init()
        self.set_rate(rate)
        if voice:
            self.set_voice(voice)

    def set_rate(self, rate: int):
        self.engine.setProperty('rate', rate)

    def set_voice(self, voice: str):
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[0].id)

    def speak(self, text: str):
        self.engine.say(text)
        self.engine.runAndWait()

    def save_to_file(self, text: str, file_path: str):
        self.engine.save_to_file(text, file_path)
        self.engine.runAndWait()

if __name__ == "__main__":
    tts = TextToSpeech(rate=250, voice='Victoria')
    tts.speak("Hello, this is a fast text-to-speech conversion example!")
    # tts.save_to_file("This is saved as an audio file.", "output.mp3")
