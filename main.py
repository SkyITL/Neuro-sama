import sys
import os
import asyncio
import signal
import threading
import time

# Ensure the project root directory is in the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

# Import your modules
from core.signals import Signals
from core.tts import TTS
from core.stt import STT
from wrapper.text_llm_wrapper import TextLLMWrapper
from core.llm_state import LLMState

async def main():
    signals = Signals()
    stt = STT(signals, model_name="medium.en")
    tts = TTS(signals)
    llmState = LLMState()
    llm = TextLLMWrapper(signals, tts, llmState)


    # Start a conversation loop
    while True:
        # Get user input
        user_input = stt.stream_transcribe()
        print(user_input)

        #if user_input.lower() in ["exit", "quit"]:
        #    print("Exiting conversation.")
        #    break

        # Append user input to the conversation history
        #signals.history.append({"role": "Vedal", "content": user_input})

        # Generate response from the LLM
        llm.prompt()

if __name__ == '__main__':
    asyncio.run(main())
