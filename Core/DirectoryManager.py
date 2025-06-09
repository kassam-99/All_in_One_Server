import json
import os
from Log import Logs
from Settings import Path_Settings






class Paths_Manager:
    
    
    def __init__(self):
        self.Log = Logs()
        self.Log.LogEngine("DirectoryManager - Paths_Manager", "LogCore_DirectoryManager")
        self.DirectorySettings = Path_Settings()
        self.Pathsfile = self.DirectorySettings.Pathsfile
        
        # Robustly determine the project root and ensure it's in Paths.json
        try:
            self.project_path = self.DirectorySettings.checkpath('Server-FrameworkPath')
            if not self.project_path or not os.path.isdir(self.project_path):
                raise ValueError("Project path not found or invalid")
            self.Log.LogsMessages(f"Project path set to: {self.project_path}", "INFO")
        except Exception as e:
            self.Log.LogsMessages(f"[!] Couldn't find Server-FrameworkPath: {e}", "CRITICAL")
            # Fallback: Walk up from current file to find project root
            current_dir = os.path.dirname(__file__)
            while current_dir != os.path.dirname(current_dir):
                if os.path.basename(current_dir) == "Server-Framework":
                    self.project_path = current_dir
                    self.Log.LogsMessages(f"Fallback: Project path resolved to {self.project_path}", "INFO")
                    break
                current_dir = os.path.dirname(current_dir)
            else:
                self.project_path = os.path.dirname(__file__)
                self.Log.LogsMessages(f"Last resort: Project path set to {self.project_path}", "WARNING")
            
            # Persist the resolved path to Paths.json
            self.GeneralPaths()  # Initialize with general paths


    def _load_json(self):
        try:
            with open(self.Pathsfile, 'r', encoding="utf-8") as file:
                return json.load(file)
        except Exception:
            return {}


    def _save_json(self, data):
        try:
            with open(self.Pathsfile, 'w', encoding="utf-8") as file:
                json.dump(data, file, indent=4)
        except Exception as e:
            self.Log.LogsMessages(f"[!] Error saving JSON: {e}", "CRITICAL")


    def is_duplicate(self, section, pathname, newpath):
        data = self._load_json()
        if section in data and pathname in data[section] and data[section][pathname] == newpath:
            return True, section
        return False, None


    def add_path(self, section, pathname, newpath):
        try:
            data = self._load_json()
            is_dup, dup_section = self.is_duplicate(section, pathname, newpath)
            if is_dup:
                self.Log.LogsMessages(f"Path '{pathname}' = '{newpath}' already exists in section '{dup_section}'", "DEBUG")
                return
            if section not in data:
                data[section] = {}
            data[section][pathname] = newpath
            self._save_json(data)
            self.Log.LogsMessages(f"Added path '{pathname}' = '{newpath}' to section '{section}'", "INFO")
        except Exception as e:
            self.Log.LogsMessages(f"[!] Error in add_path: {e}", "CRITICAL")


    def remove_path(self, section, pathname):
        try:
            data = self._load_json()
            if section in data and pathname in data[section]:
                del data[section][pathname]
                if not data[section]:
                    del data[section]
                self._save_json(data)
                self.Log.LogsMessages(f"Deleted path '{pathname}' from '{section}'", "WARNING")
            else:
                self.Log.LogsMessages(f"Nothing deleted: '{pathname}' not found in '{section}'", "INFO")
        except Exception as e:
            self.Log.LogsMessages(f"[!] Error in remove_path: {e}", "CRITICAL")


    def SectionPath(self, section=None):
        """Create or update a section in Paths.json if it doesn’t exist."""
        try:
            data = self._load_json()
            if section and section not in data:
                data[section] = {}
                self._save_json(data)
                self.Log.LogsMessages(f"Created new section '{section}' in Paths.json", "INFO")
            return data.get(section, {})
        except Exception as e:
            self.Log.LogsMessages(f"[!] Error in SectionPath: {e}", "CRITICAL")
            return {}


    def GeneralPaths(self):
        """Initialize general paths in Paths.json."""
        try:
            data = self._load_json()
            if "ProjectRoot" not in data:
                data["ProjectRoot"] = {}
            if "Server-FrameworkPath" not in data["ProjectRoot"] or not os.path.isdir(data["ProjectRoot"]["Server-FrameworkPath"]):
                data["ProjectRoot"]["Server-FrameworkPath"] = self.project_path
            if "Logs" not in data:
                data["Logs"] = {"Server-FrameworkLogs": os.path.join(self.project_path, "Logs")}
            if "Core" not in data:
                data["Core"] = {"Server-FrameworkCore": os.path.join(self.project_path, "Core")}
            self._save_json(data)
            self.Log.LogsMessages(f"Initialized general paths in Paths.json", "INFO")
        except Exception as e:
            self.Log.LogsMessages(f"[!] Error in GeneralPaths: {e}", "CRITICAL")


    def Reset_Paths(self):
        """Reset Paths.json to an empty state or minimal defaults."""
        try:
            data = {"ProjectRoot": {"Server-FrameworkPath": self.project_path}}
            self._save_json(data)
            self.Log.LogsMessages(f"Reset Paths.json to minimal defaults", "WARNING")
        except Exception as e:
            self.Log.LogsMessages(f"[!] Error in Reset_Paths: {e}", "CRITICAL")
            
            
            
            
            
            
            
            
            
            


class Dir:
    def __init__(self):
        self.DirectorySettings = Path_Settings()
        self.paths_settings = self.DirectorySettings.Pathsfile
        self.Log = Logs()
        self.Log.LogEngine("DirectoryManager - Dir", "LogCore_DirectoryManager")

        try:
            self.project_path = self.DirectorySettings.checkpath('Server-FrameworkPath')
            if not self.project_path or not os.path.isdir(self.project_path):
                raise ValueError("Project path not found or invalid")
            self.Log.LogsMessages(f"[+] Dir: Project path set to: {self.project_path}", "INFO")
            
        except Exception as e:
            self.Log.LogsMessages(f"[!] Error initializing Dir: {e}", "CRITICAL")
            self.DirectorySettings.EmergencyPaths()
            self.project_path = self.DirectorySettings.checkpath('Server-FrameworkPath')
            if not self.project_path or not os.path.isdir(self.project_path):
                # Fallback: Walk up to find project root
                current_dir = os.path.dirname(__file__)
                while current_dir != os.path.dirname(current_dir):
                    if os.path.basename(current_dir) == "Server-Framework":
                        self.project_path = current_dir
                        self.Log.LogsMessages(f"Dir fallback: Project path resolved to {self.project_path}", "INFO")
                        break
                    current_dir = os.path.dirname(current_dir)
                else:
                    self.project_path = os.path.dirname(__file__)
                    self.Log.LogsMessages(f"Dir last resort: Project path set to {self.project_path}", "WARNING")
                    
        self.subdirectories = os.listdir(self.project_path)
        
        
    def ListDir(self, mode=False):
        try:
            DirFile = []
            for subdirectory in self.subdirectories:
                
                # Skip if in excluded directories
                if subdirectory in self.DirectorySettings.EXCLUDED_DIRS:
                    continue
                
                # Skip if it matches an excluded extension (likely a file)
                if any(subdirectory.endswith(ext) for ext in self.DirectorySettings.EXCLUDED_EXT):
                    continue
                
                # Construct full path to check if it's a directory
                full_path = os.path.join(self.project_path, subdirectory)
                
                # Skip if it's not a directory (i.e., it's a file)
                if not os.path.isdir(full_path):
                    continue
                
                # Skip if it's an empty directory
                if not os.listdir(full_path):  # Empty if os.listdir returns an empty list
                    continue
    
                # If it passes all checks, add it to the list or log it
                if mode:
                    DirFile.append(subdirectory)
                    
                else:
                    self.Log.print_and_log(subdirectory)
                    DirFile.append(subdirectory)
            
            if mode:
                return DirFile
            
        except Exception as e:
            self.Log.LogsMessages(f"[!] Error in ListDir: {e}", "CRITICAL")
            

    def list_contents(self, path, indent=""):
        try:
            for item in os.listdir(path):
                
                # Skip if item is in EXCLUDED_Folders
                if item in self.DirectorySettings.EXCLUDED_DIRS:
                    continue
                
                full_path = os.path.join(path, item)
                
                # Skip if item is in EXCLUDED_Files
                if item in self.DirectorySettings.EXCLUDED_Files:
                    continue
                
                # Skip if item has an excluded extension
                if any(item.endswith(ext) for ext in self.DirectorySettings.EXCLUDED_EXT):
                    continue
                    
                if os.path.isdir(full_path):
                    self.Log.print_and_log(f"{indent}--> {item}:")
                    self.list_contents(full_path, indent + "    ")
                else:
                    self.Log.print_and_log(f"{indent} {item}")
                    
        except Exception as e:
            self.Log.LogsMessages(f"[!] Error in list_contents: {e}", "CRITICAL")
            

    def ListContentsAllOfSubDir(self, checkfolder=None):
        try:
            if checkfolder:
                if checkfolder in self.subdirectories and checkfolder not in self.DirectorySettings.EXCLUDED_DIRS:
                    full_path = os.path.join(self.project_path, checkfolder)
                    if os.path.isdir(full_path):
                        self.Log.print_and_log(f"\n     {checkfolder}:")
                        self.list_contents(full_path, "         ")
                    else:
                        self.Log.print_and_log(f"\n     {checkfolder} is not a directory.")
            else:
                for subdirectory in self.subdirectories:
                    if subdirectory in self.DirectorySettings.EXCLUDED_DIRS:
                        continue
                    full_path = os.path.join(self.project_path, subdirectory)
                    if os.path.isdir(full_path):
                        self.Log.print_and_log(f"\n     {subdirectory}:")
                        self.list_contents(full_path, "         ")
                    else:
                        self.Log.print_and_log(f"\n     {subdirectory} is not a directory.")
        except Exception as e:
            self.Log.LogsMessages(f"[!] Error in ListContentsAllOfSubDir: {e}", "CRITICAL")


    def ListAllDir(self):
        try:
            self.Log.print_and_log("---- Subdirectories of Server-Framework Project ----")
            self.ListDir()
            self.Log.print_and_log("\n---- Contents of Subdirectories ----")
            self.ListContentsAllOfSubDir()
        except Exception as e:
            self.Log.LogsMessages(f"[!] Error in ListAllDir: {e}", "CRITICAL")












class ManageLogDir(Dir):
    def __init__(self):
        super().__init__()
        self.DirectoryPath = Paths_Manager()
        self.DirectorySettings = Path_Settings()
        self.Log = Logs()
        self.Log.LogEngine("DirectoryManager - ManageLogDir", "LogCore_DirectoryManager")
        self.MainPath = self.DirectorySettings.checkpath('Server-FrameworkPath') or self.project_path
        
        # Initialize log directory
        try:
            self.log_dir = self.DirectorySettings.checkpath('Server-FrameworkLogs')
            if not self.log_dir or not os.path.isdir(self.log_dir):
                self.log_dir = os.path.join(self.MainPath, "Logs")
                if not os.path.isdir(self.log_dir):
                    self.Log.LogsMessages("[!] Logs folder not found, creating one...", "WARNING")
                    os.makedirs(self.log_dir, exist_ok=True)
                self.DirectoryPath.add_path("Logs", "Server-FrameworkLogs", self.log_dir)
            self.log_list = os.listdir(self.log_dir)
        except Exception as e:
            self.Log.LogsMessages(f"[!] Error initializing log directory: {e}", "CRITICAL")
            self.log_dir = os.path.join(self.MainPath, "Logs")
            os.makedirs(self.log_dir, exist_ok=True)
            self.log_list = os.listdir(self.log_dir)

        self.PathSections = [d for d in os.listdir(self.MainPath) if d not in self.DirectorySettings.EXCLUDED_DIRS]
        
        # Initialize core directory
        self.Core_dir = self.DirectorySettings.checkpath('Server-FrameworkCore')
        if not self.Core_dir or not os.path.isdir(self.Core_dir):
            self.Log.LogsMessages("[!] Core path not found, using default", "WARNING")
            self.Core_dir = os.path.join(self.MainPath, "Core")
            if not os.path.isdir(self.Core_dir):
                os.makedirs(self.Core_dir, exist_ok=True)
            self.DirectoryPath.add_path("Core", "Server-FrameworkCore", self.Core_dir)

    def copy_folder(self, source_folder, destination_folder):
        try:
            if os.path.isdir(source_folder) and os.path.basename(source_folder) not in self.DirectorySettings.EXCLUDED_DIRS:
                os.makedirs(destination_folder, exist_ok=True)
                for item in os.listdir(source_folder):
                    source_item = os.path.join(source_folder, item)
                    destination_item = os.path.join(destination_folder, item)
                    if os.path.isfile(source_item) and not os.path.exists(destination_item):
                        self.Log.LogsMessages(f"Creating empty file: {destination_item}", "INFO")
                        with open(destination_item, 'w'):
                            pass
                        if os.path.splitext(destination_item)[1] != '.log':
                            new_name = os.path.splitext(destination_item)[0] + '.log'
                            os.rename(destination_item, new_name)
                    elif os.path.isdir(source_item):
                        self.copy_folder(source_item, destination_item)
        except Exception as e:
            self.Log.LogsMessages(f"[!] Error in copy_folder: {e}", "CRITICAL")

    def copy_CoreLog(self, source_mainfile, destination_logfile):
        try:
            extenLog = os.path.splitext(destination_logfile)[0] + '.log'
            if os.path.isfile(source_mainfile) and not os.path.exists(extenLog):
                self.Log.LogsMessages(f"Creating empty file: {extenLog}", "INFO")
                with open(extenLog, 'w'):
                    pass
                if os.path.splitext(destination_logfile)[1] != '.log':
                    filename = os.path.splitext(os.path.basename(destination_logfile))[0]
                    self.DirectoryPath.add_path("Logs", f"LogCore_{filename}", extenLog)
        except Exception as e:
            self.Log.LogsMessages(f"[!] Error in copy_CoreLog: {e}", "CRITICAL")

    def CompareSubDirWithLog(self):
        try:
            for DirFiles in self.PathSections:
                if DirFiles in self.DirectorySettings.EXCLUDED_DIRS:
                    continue
                Dir_Folder = self.DirectorySettings.checkpath(f'Server-Framework{DirFiles}') or os.path.join(self.MainPath, DirFiles)
                if not os.path.exists(Dir_Folder):
                    continue
                    
                for folder in os.listdir(Dir_Folder):
                    if folder in self.DirectorySettings.EXCLUDED_DIRS:
                        continue
                    if f"{folder.split('.')[0]}.log" not in self.log_list:
                        source_folder = os.path.join(Dir_Folder, folder)
                        destination_folder = os.path.join(self.log_dir, folder)
                        self.copy_folder(source_folder, destination_folder)
        except Exception as e:
            self.Log.LogsMessages(f"[!] Error in CompareSubDirWithLog: {e}", "CRITICAL")

    def RepathLogs(self, source_mainfile, destination_logfile):
        try:
            extenLog = os.path.splitext(destination_logfile)[0] + ".log"
            if (os.path.isfile(source_mainfile) and 
                os.path.splitext(destination_logfile)[1] != '.log' and 
                os.path.basename(os.path.dirname(source_mainfile)) not in self.DirectorySettings.EXCLUDED_DIRS):
                filename = os.path.splitext(os.path.basename(destination_logfile))[0]
                self.DirectoryPath.add_path("Logs", f"LogCore_{filename}", extenLog)
        except Exception as e:
            self.Log.LogsMessages(f"[!] Error in RepathLogs: {e}", "CRITICAL")

    def CheckpathLog(self):
        try:
            self.PathCore = {
                "Server-FrameworkPath": self.MainPath,
                "Server-FrameworkLogs": os.path.join(self.MainPath, "Logs")
            }
            for i in self.PathSections:
                if i not in self.DirectorySettings.EXCLUDED_DIRS:
                    self.PathCore[f"Server-Framework{i}"] = os.path.join(self.MainPath, i)
                
            def explore_folders(base_path, log_dir):
                for root, dirs, files in os.walk(base_path):
                    dirs[:] = [d for d in dirs if d not in self.DirectorySettings.EXCLUDED_DIRS]
                    for file in files:
                        source_file = os.path.join(root, file)
                        destination_file = os.path.join(log_dir, os.path.relpath(source_file, base_path))
                        self.RepathLogs(source_file, destination_file)
        
            for key, value in self.PathCore.items():
                if key not in ["Server-FrameworkPath", "Server-FrameworkLogs"] and os.path.isdir(value):
                    explore_folders(value, self.log_dir)
        except Exception as e:
            self.Log.LogsMessages(f"[!] Error in CheckpathLog: {e}", "CRITICAL")

    def MainLog(self):
        self.CheckpathLog()
        self.CompareSubDirWithLog()














class ProcessManager:
    def __init__(self):
        self.Log = Logs()
        self.Log.LogEngine("DirectoryManager - ProcessManager", "LogCore_DirectoryManager")
        self.DirectorySettings = Path_Settings()
        self.MainProcessFile = self.DirectorySettings.ProcessesFile

    def ReadProcesses(self):
        try:
            with open(self.MainProcessFile, 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def write_to_process_engine_file(self, script_name_dir, used_terminal_dir, process_id_dir, process_unique_dir, script_path):
        try:
            
            data = self.ReadProcesses()
            data[script_name_dir] = {
                "Script Name" : os.path.basename(script_path),
                "Mode" : os.path.basename(os.path.dirname(script_path)),
                "Used Terminal": used_terminal_dir,
                "Process ID": process_id_dir,
                "Unique ID": process_unique_dir,
                "Script Path": script_path,
                
            }
            with open(self.MainProcessFile, 'w') as json_file:
                json.dump(data, json_file, indent=4)
            self.Log.LogsMessages(f"[+] {script_name_dir} - {process_id_dir} - {process_unique_dir} started", "INFO")
        except Exception as e:
            self.Log.LogsMessages(f"[!] Error writing to process file: {e}", "CRITICAL")

    def delete_from_process_engine_file(self, script_name_dir, process_id_dir, process_unique_dir):
        try:
            data = self.ReadProcesses()
            key = script_name_dir
            if (key in data and 
                data[key].get("Unique ID") == process_unique_dir and 
                data[key].get("Process ID") == process_id_dir):
                del data[key]
                with open(self.MainProcessFile, 'w') as json_file:
                    json.dump(data, json_file, indent=4)
                self.Log.LogsMessages(f"[-] {script_name_dir} - {process_id_dir} - {process_unique_dir} stopped", "WARNING")
        except Exception as e:
            self.Log.LogsMessages(f"[!] Error deleting from process file: {e}", "CRITICAL")


if __name__ == "__main__":
    Dir().ListAllDir()