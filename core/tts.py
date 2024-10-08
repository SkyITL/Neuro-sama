import azure.cognitiveservices.speech as speechsdk

class TTS:
    def __init__(self, signals):
        # Initialize the TTS with necessary configuration
        self.signals = signals
        self.Speechkey = '863f1e1615a644ab956e71c71facf573'
        self.SpeechRegion = 'eastasia'
        self.speech_config = speechsdk.SpeechConfig(subscription=self.Speechkey, region=self.SpeechRegion)

        # Set the audio output to the VB-Audio Virtual Cable
        self.audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
        self.speech_config.speech_synthesis_voice_name = 'en-US-AshleyNeural'
        self.speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=self.audio_config)

    def synthesize_speech(self, text, pitch="+26%"):
        ssml_text = f"""
        <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US">
            <voice name="{self.speech_config.speech_synthesis_voice_name}">
                <prosody pitch="{pitch}"> {text} </prosody>
            </voice>
        </speak>
        """

        speech_synthesis_result = self.speech_synthesizer.speak_ssml_async(ssml_text).get()

        if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Speech synthesized for text [{}]".format(text))
        elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    print("Error details: {}".format(cancellation_details.error_details))
                    print("Did you set the speech resource key and region values?")

