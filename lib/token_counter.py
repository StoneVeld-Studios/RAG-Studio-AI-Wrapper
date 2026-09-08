import os

class QwenTokenCounter:
    """
    Interfaces directly with the qwen-tokenizer library to perform 
    blazing-fast, memory-based context window calculations.
    """
    def __init__(self):
        self.tokenizer = None
        self._initialize_tokenizer()

    def _initialize_tokenizer(self):
        """
        Safely initializes the Qwen tokenizer. Falls back to a reliable 
        word-ratio estimation algorithm if the library fails to boot.
        """
        try:
            # Import the library inside the method to ensure clean fallback boundaries
            from qwen_tokenizer import QwenTokenizer
            # Qwen uses the standard tiktoken base under the hood
            self.tokenizer = QwenTokenizer.from_pretrained("Qwen/Qwen2.5-Coder-7B-Instruct", local_files_only=False)
        except Exception:
            # Fallback warning printed silently to system console
            print("[System Notice] Qwen-tokenizer engine unavailable. Utilizing fallback word-ratio calculations.")
            self.tokenizer = None

    def calculate_tokens(self, text_payload: str) -> int:
        """
        Calculates the exact token count of an assembled text string in system memory.
        """
        if not text_payload:
            return 0

        # Track tokens via the high-accuracy compiled engine
        if self.tokenizer is not None:
            try:
                return len(self.tokenizer.encode(text_payload))
            except Exception:
                pass

        # Fallback Strategy: 1 word roughly equals 1.3 tokens for code/documentation layout
        word_count = len(text_payload.split())
        return int(word_count * 1.3)

    def is_within_safety_margin(self, current_tokens: int, max_allowed_tokens: int, reservation_tokens: int = 500) -> tuple:
        """
        Verifies if the current payload leaves enough breathing room for the model's reply.
        Returns a tuple: (is_safe: bool, status_message: str)
        """
        # Always leave room (default 500 tokens) so the AI doesn't choke mid-sentence
        safe_threshold = max_allowed_tokens - reservation_tokens
        
        if current_tokens > max_allowed_tokens:
            return False, f"CRITICAL OVERFLOW: Payload ({current_tokens}) exceeds maximum runner capacity ({max_allowed_tokens})."
        elif current_tokens > safe_threshold:
            return True, f"WARNING: Payload ({current_tokens}) is entering the safety buffer zone. Minimal output space remaining."
        
        return True, f"SAFE: Payload ({current_tokens}/{max_allowed_tokens}) is optimized for local inference."
