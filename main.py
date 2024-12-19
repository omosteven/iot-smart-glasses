import cv2
import wave
import pyaudio
import threading
import os

# Configuration for audio
AUDIO_FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
AUDIO_FILENAME = "real_time_audio.wav"
VIDEO_FILENAME = "real_time_video.avi"
TEMP_VIDEO_FILENAME = "temp_video.avi"

def audio_recording():
    p = pyaudio.PyAudio()
    stream = p.open(format=AUDIO_FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    frames = []
    with wave.open(AUDIO_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(AUDIO_FORMAT))
        wf.setframerate(RATE)
        print("Audio recording started...")
        try:
            while not stop_event.is_set():
                data = stream.read(CHUNK)
                frames.append(data)

                # Append data to file in real time
                wf.writeframes(data)
        except Exception as e:
            print(f"Error in audio recording: {e}")
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()
            print("Audio recording stopped.")


def video_recording():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open video stream.")
        return

    # Video properties
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    fps = 20.0

    # Video writer
    out = cv2.VideoWriter(TEMP_VIDEO_FILENAME, cv2.VideoWriter_fourcc(*'XVID'), fps, (frame_width, frame_height))

    print("Video recording started...")
    try:
        while not stop_event.is_set():
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to capture frame.")
                break

            out.write(frame)
            cv2.imshow('Recording Video', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                stop_event.set()
                break
    except Exception as e:
        print(f"Error in video recording: {e}")
    finally:
        cap.release()
        out.release()
        cv2.destroyAllWindows()
        # Finalize the video
        os.rename(TEMP_VIDEO_FILENAME, VIDEO_FILENAME)
        print("Video recording stopped.")

if __name__ == "__main__":
    stop_event = threading.Event()

    # Start audio recording in a separate thread
    audio_thread = threading.Thread(target=audio_recording)
    audio_thread.start()

    # Start video recording
    video_recording()

    # Wait for audio thread to finish
    audio_thread.join()

    print("Recording complete. Files saved:")
    print(f"- Audio: {AUDIO_FILENAME}")
    print(f"- Video: {VIDEO_FILENAME}")
