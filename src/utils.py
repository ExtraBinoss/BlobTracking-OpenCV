import random
import string

class RandomTextGenerator:
    def __init__(self, items=None):
        if items:
            self.items = items
        else:
            self.items = [
                "SYSTEM_OK", "TRACKING", "BLOB_DETECTED", "ANALYZING", 
                "DATA_STREAM", "SIGNAL_LOST", "RECONNECTING", "BUFFERING",
                "X_POS", "Y_POS", "VELOCITY", "ACCELERATION", "TARGET_LOCKED",
                "SEARCHING", "PROCESSING", "RENDERING", "OUTPUT", "INPUT"
            ]
    
    def get_random_text(self):
        return random.choice(self.items)

    def generate_random_string(self, length=8):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
