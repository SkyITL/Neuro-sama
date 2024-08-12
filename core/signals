import queue
import threading

class Signals:
    def __init__(self):
        self.terminate = False  # Flag to signal the termination of the program
        self.AI_thinking = False  # Flag to indicate if the AI is currently processing a request
        self.AI_speaking = False  # Flag to indicate if the AI is currently speaking
        self.new_message = False  # Flag to indicate that a new message (input) has been received
        self.history = []  # List to maintain the history of the conversation
        self.sio_queue = queue.Queue()  # Queue for managing events/messages between modules

        # You can add more state variables or flags as needed by your application

        # Optional: Lock for thread-safe operations
        self.lock = threading.Lock()

    def reset(self):
        """Method to reset certain signals if needed."""
        self.AI_thinking = False
        self.AI_speaking = False
        self.new_message = False

    def add_message(self, role, content):
        """Adds a message to the history and sets the new message flag."""
        with self.lock:
            self.history.append({"role": role, "content": content})
            self.new_message = True

    def get_latest_message(self):
        """Returns the latest message in the conversation history."""
        if self.history:
            return self.history[-1]
        return None

    def shutdown(self):
        """Gracefully shuts down all ongoing processes."""
        self.terminate = True
