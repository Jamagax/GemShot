import logging
import os
from datetime import datetime
import json

class LifeOSLogger:
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Main Activity Log
        self.log_file = os.path.join(self.log_dir, "lifeos_activity.log")
        
        # Structured Data Log (JSONL for future analytics)
        self.data_log_file = os.path.join(self.log_dir, "lifeos_data.jsonl")
        
        self._setup_logging()

    def _setup_logging(self):
        # Create a custom logger
        self.logger = logging.getLogger("LifeOS_Agent")
        self.logger.setLevel(logging.DEBUG)
        
        # File Handler
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Format
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    def log_event(self, event_type, message, **kwargs):
        """Logs a human readable message and appends structured data."""
        # 1. Human Log
        self.logger.info(f"[{event_type.upper()}] {message}")
        
        # 2. Structured Data Log
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "message": message,
            "meta": kwargs
        }
        
        try:
            with open(self.data_log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            self.logger.error(f"Failed to write structured log: {e}")

    def info(self, msg):
        self.logger.info(msg)

    def error(self, msg, error=None):
        if error:
            self.logger.error(f"{msg} | Details: {error}")
        else:
            self.logger.error(msg)

# Singleton accessible instance
log_agent = LifeOSLogger()
