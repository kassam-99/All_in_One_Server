import logging
import re
import os
from datetime import datetime


# DEBUG, INFO, WARNING, ERROR, CRITICAL
"""

DEBUG - Detailed information, typically of interest only when diagnosing problems.

INFO - Confirmation that things are working as expected.

WARNING - An indication that something unexpected happened, or indicative of some problem in the near future (e.g. disk space low). The software is still working as expected.

ERROR - Due to a more serious problem, the software has not been able to perform some function.

CRITICAL - A serious error, indicating that the program itself may be unable to continue running.     
    
"""

class Logs:
    def __init__(self, default_log_level=logging.DEBUG):
        self.default_log_level = default_log_level
        self.logger = None
        self.AllinOnepaths = __file__
        self.script_dir = os.path.dirname(self.AllinOnepaths)
        self.Pathsfile = os.path.join(self.script_dir, "Paths.txt")
        
        self.mainloggerfile = os.path.join(self.script_dir, "Main_logger.log")
        self.log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        

    def log_to_file(self, message, TypeLog):
        with open(self.mainloggerfile, "a", encoding="utf-8") as error_log_file:
            error_log_file.write(f"{datetime.now()} - {TypeLog}: {message}\n")
            
    def checkpath(self, targetpath):
        try:
            with open(self.Pathsfile, 'r', encoding="utf-8") as readpath:
                for search in readpath.readlines():
                    if search.startswith('#'):
                        if targetpath in search:
                            matches = re.findall(r'["\'](.*?)["\']', search)
                            for path in matches:
                                return path

        except FileNotFoundError:
            error_message = f"Paths file not found at {self.Pathsfile}"
            self.log_to_file(error_message, "ERROR")
        except Exception as e:
            error_message = f"Error while reading Paths.txt: {e}"
            self.log_to_file(error_message, "Critical")

    def LogEngine(self, log_name, log_path):
        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(self.default_log_level)
        logfile = self.checkpath(log_path)

        if logfile is not None:
            log_dir = os.path.dirname(logfile)

            try:
                os.makedirs(log_dir, exist_ok=True)
            except OSError as e:
                error_message =  f"Error creating directory: {log_dir}"
                self.log_to_file(error_message, "Critical")
                error_message =  f"Error details: {e}"
                self.log_to_file(error_message, "Critical")
                return

            handler = logging.FileHandler(logfile)
            handler.setLevel(self.default_log_level)

            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)

            self.logger.addHandler(handler)

    def LogsMessages(self, message, message_type="info"):
        if self.logger is not None:
            message_type = message_type.lower()

            if message_type == "debug":
                self.logger.debug(message)
            elif message_type == "info":
                self.logger.info(message)
            elif message_type == "warning":
                self.logger.warning(message)
            elif message_type == "error":
                self.logger.error(message)
            elif message_type == "critical":
                self.logger.critical(message)
            else:
                self.logger.warning(f"Unknown log level '{message_type}', using 'warning' instead.")
                self.logger.warning(message)

    def print_and_log(self, message, message_type="info"):
        self.LogsMessages(message, message_type)
        print(message)
        

        


if __name__ == "__main__":
    logger = Logs()
    logger.LogEngine("ExampleLogger", "Log.log")
    logger.LogsMessages("This is a hidden message")
    logger.print_and_log("This is a test message.", message_type="info")
