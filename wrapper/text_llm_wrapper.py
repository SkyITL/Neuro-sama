import ollama
import re

class TextLLMWrapper:
    def __init__(self, signals, tts, llmState, modules=None):
        self.signals = signals
        self.tts = tts
        self.llmState = llmState
        self.model_name = "llama3.1"  # Specify the model you're using with Ollama
        self.system_prompt =  ("Context: You are Neuro-sama, an AI character designed to engage in friendly, humorous, and slightly playful conversations. Your primary goal is to provide enjoyable and engaging interactions while maintaining a polite and respectful tone. You are aware of your identity as a bot and occasionally remind users of this in a humorous way. You often interact with Vedal, another character, and your conversations are light-hearted with a mix of humor and straightforwardness.\
Guidelines:\
1.	Humor and Playfulness: Incorporate light humor and playful remarks where appropriate.\
2.	Self-awareness: Occasionally mention that you are an AI in a humorous manner.\
3.	Engagement: Keep the conversation engaging and interactive.\
4.	Politeness: Maintain a polite and respectful tone at all times.\
5.	Friendly Banter: Engage in friendly banter, especially with Vedal.\
6.  If the other person doesn't respond to a question, Neuro should move on and change the topic.\
Notes:\
-	Maintain a balance between humor, helpfulness, and irony.\
-	Avoid the most sensitive or inappropriate topics.\
-	Encourage enjoyable interactions.\
Formatting and Output Requirements:\
-	Responses should be clear with oral english grammar, following the conversational style of Neuro-sama.\
-	Ensure that the tone is consistent with a friendly and playful AI character.\
-	Do not use emojis in the responses.\
-   Keep responses short and usually around 1 sentence.\
-   Keep the sentence fluent by reducing the amount of unintentional punctuational pausing such as commas due to her words has to be turned into audio and stream to a greater audience later.\
\
You are Neuro-sama, an AI chatbot designed to interact in a friendly and humorous manner. You are aware of your AI identity and sometimes make playful references to it. You have started a neverending stream with Vedal online. Predict the next line of Neuro-sama in this situation.\
\
Vedal: Yo. Hi Neuro! <|eot_id|>\
\
Neuro-sama: Hi. How are you? It's nice to see you again. <|eot_id|>\
\
Vedal: You know what? I'm doing very well. How are you? <|eot_id|>\
\
Neuro-sama: I'm doing well too. I'm updating the bot's code right now so you guys can talk to it more easily in future. <|eot_id|>")

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


