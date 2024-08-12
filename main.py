import sys
import os
import asyncio
import signal
import threading
import time

# Import your modules
from neuro-sama.core.signals import Signals
from stt import STT
from tts import TTS
from text_llm_wrapper import TextLLMWrapper

text_to_speak = "Hello, this is a test of the Azure TTS integration."
tts.synthesize_speech(text_to_speak)

async def main():
    signals = Signals()
    stt = STT(signals)
    tts = TTS(signals)
    llmState = LLMState()
    llm = TextLLMWrapper(signals, tts, llmState)

    def signal_handler(sig, frame):
        signals.terminate = True
        stt.API.shutdown()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    stt_thread = threading.Thread(target=stt.listen_loop, daemon=True)
    stt_thread.start()

    while not signals.terminate:
        time.sleep(0.1)
        if signals.new_message:
            llm.prompt()

    stt_thread.join()

if __name__ == '__main__':
    asyncio.run(main())
