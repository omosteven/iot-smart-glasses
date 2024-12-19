import cv2
import wave
import pyaudio
import threading
import subprocess
import os

class AudioVideoRecorder:
    def __init__(self):
        self.audio_format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.chunk = 1024
        self.audio_filename = "real_time_audio.wav"
        self.temp_video_filename = "temp_video.avi"
        self.final_output_filename = "final_output.mp4"
        self.stop_event = threading.Event()

    def record_audio(self):
        """Record audio in real time."""
        p = pyaudio.PyAudio()
        stream = p.open(format=self.audio_format,
                        channels=self.channels,
                        rate=self.rate,
                        input=True,
                        frames_per_buffer=self.chunk)

        print("Audio recording started...")
        with wave.open(self.audio_filename, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(p.get_sample_size(self.audio_format))
            wf.setframerate(self.rate)
            try:
                while not self.stop_event.is_set():
                    data = stream.read(self.chunk)
                    wf.writeframes(data)
            except Exception as e:
                print(f"Error in audio recording: {e}")
            finally:
                stream.stop_stream()
                stream.close()
                p.terminate()
                print("Audio recording stopped.")

    def record_video_with_ffmpeg(self):
        """Record video with FFmpeg, including audio."""
        print("Starting video recording with FFmpeg...")
        command = [
            "/usr/local/bin/ffmpeg", #FFMPEG path on the local machine
            "-f", "avfoundation",  # For macOS; use "dshow" on Windows
            "-framerate", "30",
            "-i", "0:0",           # Adjust the input device for video and audio
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-c:a", "aac",
            self.final_output_filename
        ]
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error in FFmpeg recording: {e}")

    def start_recording(self):
        """Start audio and video recording."""
        ffmpeg_thread = threading.Thread(target=self.record_video_with_ffmpeg)
        ffmpeg_thread.start()

        try:
            ffmpeg_thread.join()
        except KeyboardInterrupt:
            self.stop_event.set()
            print("Recording interrupted by user.")

        print("Recording completed.")

if __name__ == "__main__":
    recorder = AudioVideoRecorder()
    recorder.start_recording()