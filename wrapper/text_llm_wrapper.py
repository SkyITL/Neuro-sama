import ollama
import re
from constants import LLM_PROMPT

class TextLLMWrapper:
    def __init__(self, signals, tts, llmState, modules=None):
        self.signals = signals
        self.tts = tts
        self.llmState = llmState
        self.model_name = "llama3.1"  # Specify the model you're using with Ollama
        self.system_prompt =  (LLM_PROMPT)

    def prepare_payload(self):
        # No need for payload preparation with the ollama package, handled by the `ollama.chat` call directly.
        return {
            "messages": [{'role': 'user', 'content': self.generate_prompt()}]
        }
    
    def generate_prompt(self):
        # Start with the system prompt
        prompt = self.system_prompt + "\n"

        # Append the recent conversation history
        messages = self.signals.history[-100:]
        conversation_history = "\n\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])

        # Combine system prompt with conversation history
        full_prompt = prompt + conversation_history

        return full_prompt

    def prompt(self):
        if not self.llmState.enabled:
            return
        


        messages = [{'role': 'user', 'content': self.generate_prompt()}]
        stream = ollama.chat(model=self.model_name, messages=messages, stream=True)

        AI_message = ""
        try:
            # Iterate over each chunk of the response as it arrives
            for chunk in stream:
                chunk_text = chunk['message']['content']
                AI_message += chunk_text

                # Print the chunk to the console (optional)
                print(chunk_text, end='', flush=True)

                # Process and send TTS if the chunk ends with a sentence ender
                if re.search(r'[.!?:]\s*$', AI_message):
                    # Remove "Neuro-sama:" prefix from the first sentence
                    if AI_message.startswith("Neuro-sama:"):
                        AI_message = AI_message[len("Neuro-sama:"):].strip()

                    self.signals.history.append({"role": "Neuro-sama", "content": AI_message.strip()})
                    self.tts.synthesize_speech(AI_message.strip())  # Send the response to TTS for playback
                    AI_message = ""  # Reset after speaking

            # Finalize if there's anything left after streaming
            if AI_message.strip():
                # Remove "Neuro-sama:" prefix if still present
                if AI_message.startswith("Neuro-sama:"):
                    AI_message = AI_message[len("Neuro-sama:"):].strip()

                self.signals.history.append({"role": "Neuro-sama", "content": AI_message.strip()})
                self.tts.synthesize_speech(AI_message.strip())  # Send the final chunk to TTS
        except Exception as e:
            print(f"Error while streaming response: {e}")


