# Libraries to handle I/O files, folders and Manage a system
import os
import json
import re
import signal
from Log import Logs


class EmergencyHardCoded:
    
    def __init__(self):
        self.Log = Logs()  
        self.file_path = __file__
        self.ProjectName = "All_in_One_Server"
        self.index_length_project = len(self.ProjectName)
        self.MainPathsText = "Paths.txt"
        self.MainProcessesJson = "ProcessesLab.json"
        self.MainBannedIP = "banned_ips.json"
        self.PathSections = list()
        self.BannedDir = ["Core", "Logs"]
        index = self.file_path.find(self.ProjectName)
        if index != -1:
            self.MainPath = self.file_path[:index+self.index_length_project+1]

        self.script_dir = os.path.dirname(self.file_path)
        self.Pathsfile = os.path.join(self.script_dir, self.MainPathsText)
        
        self.script_Processes = os.path.dirname(self.file_path)
        self.ProcessesFile = os.path.join(self.script_Processes, self.MainProcessesJson)
        self.IPFile = os.path.join(self.MainPath+"Admin", self.MainBannedIP)

        
        self.All_in_One_ServerPathsSubfolder = {  # Add default paths if needed
            "All_in_One_ServerPath": f"{self.MainPath}",
            "All_in_One_ServerLogs": f"{self.MainPath}Logs"
            } 
        self.PathCore = {}  # Add default paths if needed
        self.PathAdmin = {}  # Add default paths if needed
        self.PathLogs = {}  # Add default paths if needed

        for subdirectory in os.listdir(self.MainPath):

            self.PathSections.append(subdirectory)
            
        for i in self.PathSections:
            self.All_in_One_ServerPathsSubfolder["All_in_One_Server"+i] = self.MainPath+i

            
    
        self.PathServer = [self.All_in_One_ServerPathsSubfolder, self.PathAdmin, self.PathCore, self.PathLogs]

        self.project_path = self.All_in_One_ServerPathsSubfolder.get('All_in_One_ServerPath')
        

        
        
        

class EmergencyPathManager(EmergencyHardCoded):        
    def __init__(self):
        super().__init__()
        self.Log.LogEngine("Emergency - EmergencyPathManager", "LogCore_Emergency")
        
        with open(self.Pathsfile, 'w', encoding="utf-8"):
            pass
        with open(self.ProcessesFile, 'w', encoding="utf-8"):
            pass
        with open(self.IPFile, 'w', encoding="utf-8"):
            pass
        
        

    def add_path(self, section, pathname, newpath):
        # Read the existing content from the file
        with open(self.Pathsfile, 'r', encoding="utf-8") as file:
            lines = file.readlines()

        # Find the section in the file
        section_found = False
        for i, line in enumerate(lines):
            if line.strip() == f"=> {section}:":
                section_found = True
                break
        # If the section is found, add the new path under it
        if section_found:
            lines.insert(i + 1, f"\n# {pathname} = \"{newpath}\"\n")
        else:
            # If the section is not found, add a new section
            lines.extend([f"\n=> {section}:\n", f"\n# {pathname} = \"{newpath}\"\n"])
        # Write the updated content back to the file
        with open(self.Pathsfile, 'w', encoding="utf-8") as file:
            file.writelines(lines)
                                 

    def Create_Sections(self):
        with open(self.Pathsfile, 'a', encoding="utf-8") as file:
            for section in self.PathSections:
                file.write(f"\n=> {section}:\n\n\n\n")
                
                
    def Check_Defaults_Paths(self):
        for section, paths in zip(["All_in_One_Server-Subfolders", "Admin", "Core", "Logs"], [self.All_in_One_ServerPathsSubfolder, self.PathAdmin, self.PathCore, self.PathLogs]):
            non_default_paths_found = [(path_name, path_value) for path_name, path_value in paths.items() if path_value]
            if non_default_paths_found:
                for path_name, path_value in non_default_paths_found:
                    self.add_path(section, path_name, path_value)

    
    def GeneralPaths(self):
        self.subdirectories = os.listdir(self.project_path)
        DirFolderName = list()
        
        def list_contents(path):
            for item in os.listdir(path):
                filepath = os.path.join(path, item)
                full_path = os.path.join(self.project_path, filepath)
                if os.path.isfile(full_path):
                    yield full_path, True 
                elif os.path.isdir(full_path) and full_path not in self.BannedDir:
                    for sub_fullpath, sub_has_files in list_contents(full_path):
                        if sub_has_files:
                            yield sub_fullpath, True
                        else:
                            continue
    
        for subdirectory in self.subdirectories:
            if subdirectory not in self.BannedDir:
                if os.path.isdir(subdirectory):
                    DirFolderName.append(subdirectory)
    
        for fullcheckpath in DirFolderName:
            for full_path, has_files in list_contents(fullcheckpath):
                if has_files:
                    ipathname = os.path.basename(full_path)
                    self.add_path(fullcheckpath, ipathname, full_path)
                else:
                    pass        
                

    def RepathLogs(self, source_mainfile, destination_logfile):
        extenLog = destination_logfile[:-len(os.path.splitext(destination_logfile)[1])] + '.log'
        if os.path.isfile(source_mainfile):
                if os.path.splitext(destination_logfile)[1] != '.log':
                    filename = os.path.splitext(os.path.basename(destination_logfile))[0]
                    self.add_path("Logs", "LogCore_"+filename, extenLog)
                    
                    
    def explore_folders(self, base_path, section, log_dir):  # Used it to explore all the folder to create a log path for each file
        for root, dirs, files in os.walk(base_path):
            if os.path.samefile(base_path, self.All_in_One_ServerPathsSubfolder.get('All_in_One_ServerCore')):
                dirs[:] = [d for d in dirs if d not in ["__pycache__", "Logs"]]

            elif os.path.samefile(base_path, self.All_in_One_ServerPathsSubfolder.get('All_in_One_ServerAdmin')):
                dirs[:] = [d for d in dirs if d not in ["__pycache__"]]
 
            for file in files:
                source_file = os.path.join(root, file)
                destination_file = os.path.join(log_dir, os.path.relpath(source_file, base_path))
                self.RepathLogs(source_file, destination_file)
 
            for subdirectory in dirs:
                source_folder = os.path.join(root, subdirectory)
                destination_folder = os.path.join(log_dir, os.path.relpath(source_folder, base_path))
                self.RepathLogs(source_folder, destination_folder)
                
    
    def Log_start(self):
        for key, value in self.All_in_One_ServerPathsSubfolder.items():
            if key != "All_in_One_ServerPath" and key != "All_in_One_ServerLogs":  # Skip "All_in_One_ServerPath"
                if os.path.exists(value) and os.path.isdir(value):
                    self.explore_folders(value, key, self.All_in_One_ServerPathsSubfolder.get('All_in_One_ServerLogs'))
    
    
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
        with open(self.Pathsfile, 'r', encoding="utf-8") as readpath:
            for search in readpath.readlines():
                if search.startswith('#'):
                    if targetpath in search:
                        matches = re.findall(r'["\'](.*?)["\']', search)
                        for path in matches:
                            return path
                        
    def ReadProcesses(self):
        try:
            with open(self.ProcessesFile, 'r') as file:
                data = json.load(file)
            return data
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            return {}

    def delete_from_process_engine_file(self, script_name, process_id):
        try:
            with open(self.ProcessesFile, 'r') as json_file:
                data = json.load(json_file)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            return

        key = script_name

        if key in self.ReadProcesses():
            if "Process ID" in data[key] and data[key]["Process ID"] == process_id:
                try:
                    # Use os.kill with signal.SIGTERM to terminate the process
                    os.kill(process_id, signal.SIGTERM)
                except OSError:
                    self.Log.LogsMessages(f"[!] Error: Unable to terminate process with ID {process_id}", "WARNING")

                del data[key]

                with open(self.ProcessesFile, 'w') as json_file:
                    json.dump(data, json_file, indent=4)
                    
                self.Log.LogsMessages(f"[!] {script_name} - {process_id} stopped for emergency reason", "WARNING")




if __name__ == "__main__":
    
    EmergencyPathManager().StartEmergencyModePath()
    #EmergencyProcessManager().delete_from_process_engine_file("simple_socketTCP_server.py", 22620)

        
        





