import whisper
import pyaudio
import numpy as np
import webrtcvad
import torchaudio
import time

class STT:
    def __init__(self, signals, model_name="base"):
        self.signals = signals
        self.model = whisper.load_model(model_name)  # Load the specified Whisper model
        self.vad = webrtcvad.Vad(1)  # Less aggressive VAD mode to avoid cutting off speech

    def stream_transcribe(self):
        chunk_size = 2048  # Increase chunk size to give more time for response
        sample_format = pyaudio.paInt16  # 16 bits per sample
        channels = 1
        fs = 16000  # Record at 16000 samples per second
        silence_timeout = 0.3  # Time in seconds to wait before considering the speech finished

        p = pyaudio.PyAudio()

        stream = p.open(format=sample_format,
                        channels=channels,
                        rate=fs,
                        frames_per_buffer=chunk_size,
                        input=True)

        print("Listening...")

        audio_buffer = []
        last_speech_time = time.time()

        while True:
            audio_data = stream.read(chunk_size)

            # Convert buffer to raw PCM bytes for VAD
            is_speech = False
            for i in range(0, len(audio_data), 320):  # 320 bytes = 20ms of audio at 16000Hz
                frame = audio_data[i:i+320]
                if len(frame) == 320:  # Ensure it's exactly 20ms
                    is_speech = self.vad.is_speech(frame, fs)
                    if is_speech:
                        last_speech_time = time.time()  # Reset the timer when speech is detected
                        break

            if is_speech:
                audio_buffer.append(np.frombuffer(audio_data, dtype=np.int16))
            else:
                # Check if enough silence has passed since last speech detection
                if time.time() - last_speech_time > silence_timeout and audio_buffer:
                    print("Speech Finished")
                    break

        stream.stop_stream()
        stream.close()
        p.terminate()

        # Convert the buffered audio to a numpy array and process
        if not audio_buffer:
            print("No audio captured.")
            return ""

        audio_buffer = np.hstack(audio_buffer)

        # Convert to floating point and normalize
        audio_buffer = audio_buffer.astype(np.float32) / 32768.0

        # Use Whisper to transcribe the buffered audio
        result = self.model.transcribe(audio_buffer)
        return result.get("text", "").strip()
