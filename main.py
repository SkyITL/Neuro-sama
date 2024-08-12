import signal
import sys
import time
import threading
import asyncio

# Import core modules
from core.signals import Signals
from core.prompter import Prompter
from core.stt import STT
from core.tts import TTS
from core.socket_server import SocketIOServer

# Import wrappers
from wrappers.text_llm_wrapper import TextLLMWrapper

# Import modules
from modules.memory import Memory
from modules.vtube_studio import VtubeStudio
from modules.custom_prompt import CustomPrompt
from modules.input_filter import InputFilter  # Hypothetical module for input filtering
from modules.output_filter import OutputFilter  # Hypothetical module for output filtering


async def main():
    print("Starting Project...")

    # Handle signals for graceful shutdown
    def signal_handler(sig, frame):
        print('Received CTRL + C, attempting to gracefully exit.')
        signals.terminate = True
        stt.API.shutdown()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Initialize core components
    signals = Signals()  # Central signal and state management
    stt = STT(signals)  # Speech-to-Text
    tts = TTS(signals)  # Text-to-Speech
    memory = Memory(signals)  # Conversation memory management

    # Initialize LLM Wrappers
    llmState = LLMState()
    llms = {
        "text": TextLLMWrapper(signals, tts, llmState)
    }

    # Initialize filters
    input_filter = InputFilter(signals)  # Filter or preprocess input text
    output_filter = OutputFilter(signals)  # Filter or post-process generated text

    # Initialize other modules
    prompter = Prompter(signals, llms, memory)
    vtube_studio = VtubeStudio(signals)

    # Setup WebSocket server (e.g., for streaming TTS)
    sio = SocketIOServer(signals, stt, tts, llms["text"], prompter)

    # Threads to manage concurrency (As daemons, so they exit when the main thread exits)
    prompter_thread = threading.Thread(target=prompter.prompt_loop, daemon=True)
    stt_thread = threading.Thread(target=stt.listen_loop, daemon=True)
    sio_thread = threading.Thread(target=sio.start_server, daemon=True)

    # Start Threads
    sio_thread.start()
    prompter_thread.start()
    stt_thread.start()

    # Manage module threads (for VtubeStudio, etc.)
    modules = {
        "vtube_studio": vtube_studio
    }
    module_threads = {}
    for name, module in modules.items():
        module_thread = threading.Thread(target=module.init_event_loop, daemon=True)
        module_threads[name] = module_thread
        module_thread.start()

    # Main loop to keep the application running until termination
    while not signals.terminate:
        time.sleep(0.1)

    print("TERMINATING ======================")

    # Wait for threads to finish before exiting
    for module_thread in module_threads.values():
        module_thread.join()

    sio_thread.join()
    prompter_thread.join()
    stt_thread.join()

    print("All threads exited, shutdown complete")
    sys.exit(0)


if __name__ == '__main__':
    asyncio.run(main())
