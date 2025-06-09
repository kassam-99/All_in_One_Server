# Libraries to handle I/O files, folders and Manage a system 


import os
import json
import re
import signal
from Log import Logs

class EmergencyHardCoded:
    
    def __init__(self):
        self.Log = Logs()
        
        self.file_path = os.path.abspath(__file__)
        self.ProjectName = "Server-Framework"
        self.MainPathsText = "Paths.json"
        self.MainProcessesJson = "ProcessesLab.json"
        self.MainBannedIP = "banned_ips.json"
        self.PathSections = []

        self.EXCLUDED_DIRS = ["server_env", ".vscode", "__pycache__", ".git", ".env"]
        self.EXCLUDED_Files = ["Commands", ".env", ".gitignore", "requirements.txt", ".git"]
        self.EXCLUDED_EXT = [
            # Temporary & Log Files
            ".tmp", ".log", ".bak", ".gz",
            
            # Compiled Files
            ".pyc", ".pyo", ".class", ".o", ".obj", ".so", ".dll", ".exe", ".out",
            
            # Configuration & Environment Files
            ".env", ".cfg", ".config", ".ini", ".toml", ".lock",
            
            # Documentation & ReadMe Files
            ".md", ".rst", ".adoc", ".rtf", ".doc", ".docx",
            
            # Version Control & Git
            ".gitignore", ".gitattributes", ".gitmodules",
            
            # Archives & Compressed Files
            ".zip", ".tar", ".gz", ".bz2", ".7z", ".rar", ".xz",
            
            # Virtual Environment & Package Files
            ".whl", ".egg", ".dist-info", ".tar.gz",
            
            # Shell & Executable Scripts
            ".bat", ".cmd", ".ps1",
            
            # Image, Video & Media Files
            ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".ico", ".tiff",
            ".mp3", ".wav", ".flac", ".mp4", ".avi", ".mov", ".mkv", ".webm",
            
        ]

        # Corrected project path detection
        index = self.file_path.find("Server-Framework")  # Fixed string case
        if index != -1:
            self.MainPath = self.file_path[:index + len("Server-Framework")+1]  # Adjusted slicing to match length of "Server-Framework"
        else:
            error_message = "Project directory 'Server-Framework' not found in file path"
            self.Log.LogsMessages(error_message, "CRITICAL")
            raise ValueError(error_message)

        self.script_dir = os.path.dirname(self.file_path)
        self.Pathsfile = os.path.join(self.script_dir, self.MainPathsText)
        self.ProcessesFile = os.path.join(self.script_dir, self.MainProcessesJson)
        self.IPFile = os.path.join(self.MainPath + "Admin", self.MainBannedIP)

        # Initialize default paths
        self.Server_FrameworkPathsSubfolder = {
            "Server-FrameworkPath": f"{self.MainPath}",
            "Server-FrameworkLogs": f"{self.MainPath}Logs"
        }
        self.PathCore = {}
        self.PathAdmin = {}
        self.PathLogs = {}

        # Populate PathSections with subdirectories
        for subdirectory in os.listdir(self.MainPath):
            self.PathSections.append(subdirectory)
        
        # Build path dictionary
        for i in self.PathSections:
            self.Server_FrameworkPathsSubfolder["Server-Framework" + i] = os.path.join(self.MainPath, i)

        self.PathServer = [self.Server_FrameworkPathsSubfolder, self.PathAdmin, self.PathCore, self.PathLogs]
        self.project_path = self.Server_FrameworkPathsSubfolder.get('Server-FrameworkPath')
        

    def get_excluded_items(self,
        base_path: str,  # Added to make it dynamic based on a directory
        excluded_dirs=None, excluded_files=None, excluded_extensions=None, excluded_paths=None,
        exclude_dirs_bool=False, exclude_files_bool=False, exclude_extensions_bool=False, 
        exclude_paths_bool=False, exclude_all=False
    ):
        # Default empty lists if None is provided, with dynamic additions
        excluded_dirs = excluded_dirs or []
        excluded_files = excluded_files or []
        excluded_extensions = excluded_extensions or []
        excluded_paths = excluded_paths or [base_path]  # Default to base_path dynamically
    
        excluded_items = set()
    
        # Enable all exclusions if `exclude_all` is True
        if exclude_all:
            exclude_dirs_bool = exclude_files_bool = exclude_extensions_bool = exclude_paths_bool = True
    
        # Dynamically detect common patterns in the base_path
        if os.path.exists(base_path) and os.path.isdir(base_path):
            for item in os.listdir(base_path):
                full_path = os.path.join(base_path, item)
                # Add hidden files or directories
                if any(item.endswith(ext) for ext in self.EXCLUDED_EXT):
                    excluded_items.add(item)
                # Dynamically exclude common temp/generated files
                elif os.path.isfile(full_path) and item in self.EXCLUDED_Files:
                    excluded_items.add(item)
                # Dynamically exclude common build/output dirs
                elif os.path.isdir(full_path) and item in self.EXCLUDED_DIRS:
                    excluded_items.add(item)
    
        # Exclude files inside `excluded_paths`
        if exclude_paths_bool:
            for path in excluded_paths:
                if os.path.exists(path) and os.path.isdir(path):
                    for item in os.listdir(path):
                        full_path = os.path.join(path, item)
                        if os.path.isfile(full_path):
                            excluded_items.add(item)
    
        # Apply other exclusions
        for path in excluded_paths:
            if os.path.exists(path) and os.path.isdir(path):
                for item in os.listdir(path):
                    file_name_without_ext, file_ext = os.path.splitext(item)  # Split filename and extension
    
                    if (
                        (exclude_dirs_bool and item in excluded_dirs) or
                        (exclude_files_bool and (item in excluded_files or file_name_without_ext in excluded_files)) or
                        (exclude_extensions_bool and item.endswith(tuple(excluded_extensions))) or
                        item.startswith(".") or  # Hidden files
                        item.startswith("__")    # System files
                    ):
                        excluded_items.add(item)
    
        return list(excluded_items)
    





class EmergencyPathManager(EmergencyHardCoded):        
    def __init__(self):
        super().__init__()
        self.Log.LogEngine("Emergency - EmergencyPathManager", "LogCore_Emergency")
        
        # Initialize JSON files only if they don't exist
        for file_path in [self.Pathsfile, self.ProcessesFile, self.IPFile]:
            try:
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                if not os.path.exists(file_path):  # Check before creating to avoid overwriting
                    with open(file_path, 'w', encoding="utf-8") as f:
                        json.dump({}, f)
            except Exception as e:
                self.Log.LogsMessages(f"[!] Error initializing file {file_path}: {e}", "CRITICAL")

        self.BannedDir = self.get_excluded_items(
            base_path=self.MainPath,
            exclude_dirs_bool=True, excluded_dirs= self.EXCLUDED_DIRS,
            exclude_files_bool=True, excluded_files=self.EXCLUDED_Files,
            exclude_extensions_bool=True, excluded_extensions=self.EXCLUDED_EXT
        )


    def _load_json(self):
        try:
            with open(self.Pathsfile, 'r', encoding="utf-8") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}


    def _save_json(self, data):
        try:
            with open(self.Pathsfile, 'w', encoding="utf-8") as file:
                json.dump(data, file, indent=4)
        except Exception as e:
            self.Log.LogsMessages(f"[!] Error saving JSON: {e}", "CRITICAL")


    def add_path(self, section, pathname, newpath):
        try:
            data = self._load_json()
            if section not in data:
                data[section] = {}
            data[section][pathname] = newpath
            self._save_json(data)
        except Exception as e:
            self.Log.LogsMessages(f"[!] Error in add_path: {e}", "CRITICAL")


    def Create_Sections(self):
        data = self._load_json()
        for section in self.PathSections:
            if section not in data:
                data[section] = {}
        self._save_json(data)


    def Check_Defaults_Paths(self):
        data = self._load_json()
        section_map = {
            "Server-Framework-Subfolders": self.Server_FrameworkPathsSubfolder,
            "Admin": self.PathAdmin,
            "Core": self.PathCore,
            "Logs": self.PathLogs
        }
        
        for section, paths in section_map.items():
            if section not in data:
                data[section] = {}
            non_default_paths_found = [(path_name, path_value) for path_name, path_value in paths.items() if path_value]
            for path_name, path_value in non_default_paths_found:
                data[section][path_name] = path_value
        self._save_json(data)


    def GeneralPaths(self):
        try:
            self.subdirectories = os.listdir(self.project_path)
        except Exception as e:
            self.Log.LogsMessages(f"[!] Error listing project path: {e}", "WARNING")
            return
    
        DirFolderName = []
        
        def list_contents(path):
            try:
                for item in os.listdir(path):
                    if (item.startswith(".") or item.startswith("~") or item.startswith("_") or 
                        item.startswith("$") or item.startswith("__") or item in self.BannedDir):
                        continue
                    filepath = os.path.join(path, item)
                    if os.path.isfile(filepath) and os.path.splitext(item)[1] not in self.EXCLUDED_EXT:
                        yield filepath, True 
                    elif os.path.isdir(filepath) and item not in self.BannedDir:
                        for sub_fullpath, sub_has_files in list_contents(filepath):
                            yield sub_fullpath, sub_has_files
            except Exception as e:
                self.Log.LogsMessages(f"[!] Error in list_contents for {path}: {e}", "WARNING")
        
        for subdirectory in self.subdirectories:
            full_path = os.path.join(self.project_path, subdirectory)
            if (subdirectory not in self.BannedDir and 
                os.path.exists(full_path) and 
                os.path.isdir(full_path)):
                DirFolderName.append(subdirectory)
        
        for fullcheckpath in DirFolderName:
            full_path = os.path.join(self.project_path, fullcheckpath)
            try:
                for path, has_files in list_contents(full_path):
                    if has_files:
                        ipathname = os.path.basename(path)
                        self.add_path(fullcheckpath, ipathname, path)
            except Exception as e:
                self.Log.LogsMessages(f"[!] Error processing {fullcheckpath}: {e}", "WARNING")


    def RepathLogs(self, source_mainfile, destination_logfile):
        try:
            # Check if source or destination contains excluded items
            source_parts = source_mainfile.split(os.sep)
            dest_parts = destination_logfile.split(os.sep)
            
            # Skip if any part of the path is in EXCLUDED_DIRS or EXCLUDED_Files
            if (any(part in self.EXCLUDED_DIRS for part in source_parts) or
                any(part in self.EXCLUDED_DIRS for part in dest_parts) or
                any(part in self.EXCLUDED_Files for part in source_parts) or
                any(part in self.EXCLUDED_Files for part in dest_parts)):
                return
            
            # Check file extensions
            source_ext = os.path.splitext(source_mainfile)[1]
            dest_ext = os.path.splitext(destination_logfile)[1]
            if source_ext in self.EXCLUDED_EXT or dest_ext in self.EXCLUDED_EXT:
                return
    
            # Proceed with log file creation
            extenLog = os.path.splitext(destination_logfile)[0] + '.log'
            if os.path.isfile(source_mainfile):
                if os.path.splitext(destination_logfile)[1] != '.log':
                    filename = os.path.splitext(os.path.basename(destination_logfile))[0]
                    self.add_path("Logs", "LogCore_" + filename, extenLog)
        except Exception as e:
            self.Log.LogsMessages(f"[!] Error in RepathLogs: {e}", "CRITICAL")
            
            
    def explore_folders(self, base_path, section, log_dir):
        try:
            for root, dirs, files in os.walk(base_path):
                # Correctly filter out unwanted directories
                dirs[:] = [d for d in dirs if not (d.startswith(".") or d.startswith("~") or 
                                                  d.startswith("_") or d.startswith("$") or 
                                                  d.startswith("__") or d in self.BannedDir)]
                
                # Skip processing if root contains an excluded directory
                if any(excluded in root for excluded in self.EXCLUDED_DIRS):
                    continue
    
                for file in files:
                    if (file.startswith(".") or file.startswith("~") or file.startswith("_") or 
                        file.startswith("$") or file.startswith("__") or 
                        os.path.splitext(file)[1] in self.EXCLUDED_EXT):
                        continue
                    
                    source_file = os.path.join(root, file)
                    destination_file = os.path.join(log_dir, os.path.relpath(source_file, base_path))
                    self.RepathLogs(source_file, destination_file)
                
                for subdirectory in dirs:
                    source_folder = os.path.join(root, subdirectory)
                    destination_folder = os.path.join(log_dir, os.path.relpath(source_folder, base_path))
                    self.RepathLogs(source_folder, destination_folder)
        except Exception as e:
            self.Log.LogsMessages(f"[!] Error in explore_folders: {e}", "WARNING")


    def Log_start(self):
        for key, value in self.Server_FrameworkPathsSubfolder.items():
            if key not in ["Server-FrameworkPath", "Server-FrameworkLogs"]:
                if os.path.exists(value) and os.path.isdir(value):
                    self.explore_folders(value, key, self.Server_FrameworkPathsSubfolder.get('Server-FrameworkLogs'))


    def StartEmergencyModePath(self):
        self.Create_Sections()
        self.Check_Defaults_Paths()
        self.GeneralPaths()
        self.Log_start()











class EmergencyProcessManager(EmergencyHardCoded):
    def __init__(self):
        super().__init__()
        self.Log.LogEngine("Emergency - EmergencyProcessManager", "LogCore_Emergency")
        
    def checkpath(self, targetpath):
        data = self._load_json()
        for section, paths in data.items():
            for path_name, path_value in paths.items():
                if targetpath in path_value:
                    return path_value
        return None

    def _load_json(self):
        try:
            with open(self.Pathsfile, 'r', encoding="utf-8") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def ReadProcesses(self):
        try:
            with open(self.ProcessesFile, 'r') as file:
                data = json.load(file)
            return data
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def delete_from_process_engine_file(self, script_name, process_id):
        try:
            with open(self.ProcessesFile, 'r') as json_file:
                data = json.load(json_file)
        except (FileNotFoundError, json.JSONDecodeError):
            return

        key = script_name
        if key in self.ReadProcesses():
            if "Process ID" in data[key] and data[key]["Process ID"] == process_id:
                try:
                    os.kill(process_id, signal.SIGTERM)
                except OSError:
                    self.Log.LogsMessages(f"[!] Error: Unable to terminate process with ID {process_id}", "WARNING")

                del data[key]
                with open(self.ProcessesFile, 'w') as json_file:
                    json.dump(data, json_file, indent=4)
                    
                self.Log.LogsMessages(f"[!] {script_name} - {process_id} stopped for emergency reason", "WARNING")


if __name__ == "__main__":
    EmergencyPathManager().StartEmergencyModePath()