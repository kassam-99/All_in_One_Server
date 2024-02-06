# Libraries to handle I/O files, folders and Manage a system
import re

# Other:
from DirectoryManager import Dir
from Log import Logs
from Settings import Path_Settings



class ModeManager:
    def __init__(self):
        self.log_modes = Logs()
        self.log_modes.LogEngine("ModeManager", "LogCore_Modes")

        self.dir_mode = Dir()
        self.mode_settings = Path_Settings()
        self.banned_modes = self.mode_settings.EXCLUDED_DIRS
        
        self.available_modes = []
        

    def list_modes(self, listed_mode=False):
        self.available_modes = [mode for mode in self.dir_mode.ListDir(True) if mode not in self.banned_modes]
        if listed_mode:
            self.log_modes.print_and_log("[*] Available Modes:")
            for i, mode in enumerate(self.available_modes, start=1):
                if '.' not in mode:
                    self.log_modes.print_and_log(f"[{i}] {mode}")

        return self.available_modes


    def select_mode(self, user_mode):
        if user_mode in self.available_modes:
            self.dir_mode.ListContentsAllOfSubDir(user_mode)
        else:
            self.log_modes.print_and_log(f"[!] Selected mode {user_mode} not found. Available modes: {self.available_modes}", "error")


    def extract_folders_and_files(self, input_string):
        file_pattern = re.compile(r'\s+([^:\s]+\.\w+)')
        files = [file_match.group(1) for line in input_string.split('\n') if (file_match := file_pattern.search(line))]
        return files

    def ListDir(self):
        self.dir_mode.ListAllDir()

if __name__ == "__main__":
    pass



