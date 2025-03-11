import sounddevice as sd
import speech_recognition as sr

# Parameters
duration = 7  # seconds
sample_rate = 44100

def record_audio(): 
    # Record audio
    print("What to schedule?")
    audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
    sd.wait()  # Wait until recording is finished

    # Convert to bytes
    audio_bytes = audio_data.tobytes()

    # Initialize recognizer
    recognizer = sr.Recognizer()

    # Convert speech to text
    try:
        audio = sr.AudioData(audio_bytes, sample_rate, 2)
        text = recognizer.recognize_google(audio)  # Use Google API
        return text 
    except sr.UnknownValueError:
        print("Sorry, could not understand the audio.")
    except sr.RequestError:
        print("Could not request results. Check your internet connection.")