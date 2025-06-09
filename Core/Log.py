import logging
import os
import json
from datetime import datetime


class Logs:
    def __init__(self, default_log_level=logging.DEBUG):
        self.default_log_level = default_log_level
        self.logger = None
        self.ServerFrameworkpaths = __file__
        self.script_dir = os.path.dirname(self.ServerFrameworkpaths)
        self.Pathsfile = os.path.join(self.script_dir, "Paths.json")
        
        # Set up main logger with a FileHandler
        self.mainloggerfile = os.path.join(self.script_dir, "Main_logger.log")
        self.log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        # Initialize the main logger
        self.main_logger = logging.getLogger("MainLogger")
        self.main_logger.setLevel(self.default_log_level)
        
        # Remove existing handlers to avoid duplicates
        if self.main_logger.handlers:
            self.main_logger.handlers.clear()
        
        main_handler = logging.FileHandler(self.mainloggerfile)
        main_handler.setLevel(self.default_log_level)
        formatter = logging.Formatter(self.log_format)
        main_handler.setFormatter(formatter)
        self.main_logger.addHandler(main_handler)

    def log_to_file(self, message, TypeLog):
        """Log messages using the main logger instead of direct file writing."""
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        log_level = level_map.get(TypeLog.upper(), logging.WARNING)
        self.main_logger.log(log_level, message)

    def _load_json(self):
        """Helper method to load JSON data with consistent logging."""
        try:
            with open(self.Pathsfile, 'r', encoding="utf-8") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.log_to_file(f"Paths file not found or invalid at {self.Pathsfile}: {e}", "ERROR")
            return {}
        except Exception as e:
            self.log_to_file(f"Error while reading Paths.json: {e}", "CRITICAL")
            return {}

    def checkpath(self, targetpath):
        """Check for a target path in the JSON data with consistent logging."""
        try:
            data = self._load_json()
            for section, paths in data.items():
                for path_name, path_value in paths.items():
                    if targetpath in path_name or targetpath in path_value:
                        return path_value
            return None
        except Exception as e:
            self.log_to_file(f"Error in checkpath: {e}", "CRITICAL")
            return None

    def LogEngine(self, log_name, log_path):
        """Set up a logger with a single FileHandler, avoiding duplicates."""
        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(self.default_log_level)
        logfile = self.checkpath(log_path)

        if logfile is not None:
            log_dir = os.path.dirname(logfile)

            try:
                os.makedirs(log_dir, exist_ok=True)
            except OSError as e:
                self.log_to_file(f"Error creating directory {log_dir}: {e}", "CRITICAL")
                return

            # Remove existing FileHandlers to prevent duplicates
            for handler in self.logger.handlers[:]:  # Iterate over a copy to avoid modifying during iteration
                if isinstance(handler, logging.FileHandler):
                    self.logger.removeHandler(handler)

            handler = logging.FileHandler(logfile)
            handler.setLevel(self.default_log_level)
            formatter = logging.Formatter(self.log_format)
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.log_to_file(f"Logger '{log_name}' initialized with file '{logfile}'", "INFO")

    def LogsMessages(self, message, message_type="info"):
        """Log messages with the specified logger if initialized."""
        if self.logger is not None:
            message_type = message_type.lower()
            level_map = {
                "debug": self.logger.debug,
                "info": self.logger.info,
                "warning": self.logger.warning,
                "error": self.logger.error,
                "critical": self.logger.critical
            }
            log_method = level_map.get(message_type, self.logger.warning)
            if log_method == self.logger.warning and message_type not in level_map:
                self.logger.warning(f"Unknown log level '{message_type}', using 'warning' instead.")
            log_method(message)

    def print_and_log(self, message, message_type="info"):
        """Log and print messages simultaneously."""
        self.LogsMessages(message, message_type)
        print(message)


if __name__ == "__main__":
    logger = Logs()
    logger.LogEngine("ExampleLogger", "Log.log")
    logger.LogsMessages("This is a hidden message")
    logger.print_and_log("This is a test message.", message_type="info")