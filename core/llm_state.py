# core/llm_state.py

class LLMState:
    def __init__(self):
        self.enabled = True  # Indicates whether the LLM is enabled
        self.next_cancelled = False  # Flag to indicate if the next operation should be cancelled
        self.processing = False  # Flag to show if LLM is currently processing

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def start_processing(self):
        self.processing = True

    def stop_processing(self):
        self.processing = False

    def cancel_next(self):
        self.next_cancelled = True

    def reset_cancel(self):
        self.next_cancelled = False

# Add any additional state management methods as needed
