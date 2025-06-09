# Libraries to handle I/O files, folders and Manage a system  Server-Framework
import re

# Other:
from DirectoryManager import Dir
from Log import Logs
from Settings import Path_Settings


class ModeManager:
    def __init__(self):
        self.log_modes = Logs()
        self.log_modes.LogEngine("ModeManager", "LogCore_Modes")
        self.project_name_terminal = "\u001b[34mServer-Framework\u001b[0m - \u001b[33mServer\u001b[0m"

        try:
            self.dir_mode = Dir()
            self.mode_settings = Path_Settings()
            self.banned_modes = self.mode_settings.EXCLUDED_DIRS
            self.available_modes = self.list_modes()  # Populate on init
            
        except Exception as e:
            self.log_modes.print_and_log(f"{self.project_name_terminal} [\u001b[31m!\u001b[0m] Error initializing ModeManager: {e}", "CRITICAL")
            self.available_modes = []


    def list_modes(self, listed_mode=False):
        """List available modes, optionally logging them."""
        try:
            modes = self.dir_mode.ListDir(True)
            if modes is None:
                raise ValueError("Dir.ListDir returned None")
            self.available_modes = [mode for mode in modes if mode not in self.banned_modes]
            if listed_mode:
                self.log_modes.print_and_log("[\u001b[35m*\u001b[0m] Available Modes:")
                for i, mode in enumerate(self.available_modes, start=1):
                    self.log_modes.print_and_log(f"[\u001b[36m{i}\u001b[0m] {mode}")
            return self.available_modes
        
        except Exception as e:
            self.log_modes.print_and_log(f"{self.project_name_terminal} [\u001b[31m!\u001b[0m] Error listing modes: {e}", "ERROR")
            return []


    def select_mode(self, user_mode):
        """Display contents of a selected mode."""
        try:
            if not self.available_modes:
                self.list_modes()  # Ensure modes are populated
            if user_mode in self.available_modes:
                self.dir_mode.ListContentsAllOfSubDir(user_mode)
                # Optionally extract files
                # output = capture_output(self.dir_mode.ListContentsAllOfSubDir, user_mode)
                # files = self.extract_folders_and_files(output)
                # self.log_modes.print_and_log(f"Files in {user_mode}: {files}")
            else:
                self.log_modes.print_and_log(f"{self.project_name_terminal} [\u001b[31m!\u001b[0m] Selected mode {user_mode} not found. Available modes: {self.available_modes}", "ERROR")
                
        except Exception as e:
            self.log_modes.print_and_log(f"{self.project_name_terminal} [\u001b[31m!\u001b[0m] Error selecting mode {user_mode}: {e}", "ERROR")


    def extract_folders_and_files(self, input_string):
        """Extract filenames from a string (e.g., Dir output)."""
        try:
            file_pattern = re.compile(r'\s+([^:\s]+\.\w+)')
            files = [file_match.group(1) for line in input_string.split('\n') if (file_match := file_pattern.search(line))]
            return files
        
        except Exception as e:
            self.log_modes.print_and_log(f"{self.project_name_terminal} [\u001b[31m!\u001b[0m] Error extracting files: {e}", "ERROR")
            return []
        

    def ListDir(self):
        """List all directories and their contents."""
        try:
            self.dir_mode.ListAllDir()
            
        except Exception as e:
            self.log_modes.print_and_log(f"{self.project_name_terminal} [\u001b[31m!\u001b[0m] Error listing all directories: {e}", "ERROR")





if __name__ == "__main__":
    # Basic test
    manager = ModeManager()
    manager.list_modes(listed_mode=True)
    if manager.available_modes:
        manager.select_mode(manager.available_modes[0])  # Test first available mode
    manager.ListDir()




