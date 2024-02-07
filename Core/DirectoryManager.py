import json
import os
import re
from Log import Logs
from Settings import Path_Settings








class Paths_Manager:
    def __init__(self):
        self.Log = Logs()
        self.Log.LogEngine("DirectoryManager - Paths_Manager", "LogCore_DirectoryManager")

        self.DirectorySettings = Path_Settings()
        self.Pathsfile = self.DirectorySettings.Pathsfile
        
        try:
            self.project_path = self.DirectorySettings.checkpath('All_in_One_ServerPath')
        except Exception as e:
            self.Log.LogsMessages(f"[!] Couldn't find All_in_One_ServerPath: {e}", "Critical")
        finally:
            self.project_path = self.DirectorySettings.checkpath('All_in_One_ServerPath')
            
                        
    def is_duplicate(self, pathname, newpath, lines):
        try:
            for i, line in enumerate(lines):
                # Check if the line contains the specified pathname and newpath
                if f"# {pathname} = \"{newpath}\"" in line:
                    # Find the section by looking for the nearest section header above the duplicate line
                    section = None
                    for j in range(i, -1, -1):
                        if lines[j].strip().startswith("=>"):
                            section = lines[j].strip().replace("=>", "").strip()
                            break
                    return True, section
            return False, None
        except Exception as e:
            self.Log.LogsMessages(f"[!] An error occurred in 'is_duplicate': {e}", "Critical")
            return False, None


    def add_path(self, section, pathname, newpath):
        try:
            # Read the existing content from the file
            with open(self.Pathsfile, 'r', encoding="utf-8") as file:
                lines = file.readlines()
            # Check if the path is already present
            duplicate, duplicate_section = self.is_duplicate(pathname, newpath, lines)
            if duplicate:
                self.Log.LogsMessages(f"The path with pathname '{pathname}' and newpath '{newpath}' is already present in the section '{duplicate_section}'.", "debug")
                return
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
        except Exception as e:
            self.Log.LogsMessages(f"[!] An error occurred in 'add_path': {e}", "Critical")
        
    def remove_path(self, section, pathname):
        try:
            with open(self.Pathsfile, "r", encoding="utf-8") as readpath:
                lines = readpath.readlines()
                lengthlines = len(lines)
        
            section_found = False
            for i, line in enumerate(lines):
                if line.strip() == f"=> {section}:":
                    section_found = True
                    break
            
            if section_found:
                pattern = re.compile(rf'^\s*#\s*{re.escape(pathname)}\s*=\s*".*"')
                lines = [l for l in lines if not pattern.match(l.strip())]
        
            with open(self.Pathsfile, 'w', encoding="utf-8") as file:
                file.writelines(lines)
        
            if len(lines) == lengthlines:
                self.Log.LogsMessages("Nothing is deleted", "Critical")
            else:
                self.Log.LogsMessages(f"Deleted the following path {pathname} is removed", "warning")
        except Exception as e:
            self.Log.LogsMessages(f"[!] An error occurred in 'remove_path': {e}", "Critical")


    def Reset_Paths(self):
        try:
            path_names = []  # path_name = "path/All_in_One_Server/.../.../"
            main_paths = []  # Of All_in_One_Server/...main../...main.../
    
            file_path = __file__
            index = file_path.find("All_in_One_Server")
            if index != -1:
                result = file_path[:index]
        
            with open(self.Pathsfile, "r", encoding="utf-8") as readpath:
                file_contents = readpath.read()
        
            for line in file_contents.split("\n"):
                if line.startswith('#'):
                    IndexPathName = line.find(" = ")
                    if IndexPathName != -1:
                        ResultPathName = line[:IndexPathName].strip()
                        path_names.append(ResultPathName)
        
                    IndexOldPath = line.find("All_in_One_Server")
                    if IndexOldPath != -1:
                        ResultOldPath = line[IndexOldPath:].strip('\'"')
                        main_paths.append(ResultOldPath)
        
            # Create new paths
            new_path = [f"{path_name} = \"{result}{old_path}\"" for path_name, old_path in zip(path_names, main_paths)]
            
            # Replace old paths with new paths in file_contents
            for i, line in enumerate(file_contents.split("\n")):
                if line.startswith('#'):
                    IndexPathName = line.find(" = ")
                    if IndexPathName != -1:
                        file_contents = file_contents.replace(line, new_path.pop(0))
        
            # Write the modified paths back to the file
            with open(self.Pathsfile, "w", encoding="utf-8") as writepath:
                writepath.write(file_contents)
                
            self.Log.LogsMessages("Path reseted", "Critical")
        except Exception as e:
            self.Log.LogsMessages(f"[!] An error occurred in 'Reset_Paths': {e}", "Critical")


    def SectionPath(self):
        try:
            folderSections = set()  # Folders in All_in_One_Server C2 Server
            PathsSections = set()   # Sections in All_in_One_Server C2 Server
            differenceSections = set() 
            
            # Checking folders in All_in_One_Server
            self.subdirectories = os.listdir(self.project_path)
            folderSections.update(subdirectory for subdirectory in self.subdirectories)
            
            # Checking Sections in All_in_One_Server
            with open(self.Pathsfile, 'r', encoding="utf-8") as ReadSections:
                lines = ReadSections.readlines()
            
            for line in lines:
                if line.strip().startswith("=>"):
                    pattern = r'=>\s*(\w+)\s*:'
                    match = re.search(pattern, line)
                    if match:
                        extracted_word = match.group(1)
                        PathsSections.add(extracted_word)
                
            # Find the difference between folderSections and PathsSections
            differenceSections = folderSections.difference(PathsSections)
            diffeewnceFolders = PathsSections.difference(folderSections)
            if differenceSections:
                self.Log.LogsMessages("Folders in All_in_One_Server but not in Path.txt", "debug")
                for item in differenceSections:
                    self.Log.LogsMessages(f"Difference: {item}", "info")
                    lines.extend([f"\n=> {item}:\n"])
        
                    # Write the updated content back to the file
                    with open(self.Pathsfile, 'w', encoding="utf-8") as file:
                        file.writelines(lines)
                    
            if diffeewnceFolders:
                self.Log.LogsMessages("Sections in Path.txt but not in All_in_One_Server folder", "debug")
                for item in diffeewnceFolders:
                    os.mkdir(item)
                    self.Log.LogsMessages(f"Difference: {item}", "info")
        except Exception as e:
            self.Log.LogsMessages(f"[!] An error occurred in 'SectionPath': {e}", "Critical")
                       
                
    def GeneralPaths(self):
        try:
            self.subdirectories = os.listdir(self.project_path)
            BannedDir = self.DirectorySettings.EXCLUDED_DIRS
            DirFolderName = list()
        
            def list_contents(path):
                for item in os.listdir(path):
                    filepath = os.path.join(path, item)
                    full_path = os.path.join(self.project_path, filepath)
                    if os.path.isfile(full_path):
                        yield full_path, True 
                    elif os.path.isdir(full_path) and full_path not in BannedDir:
                        for sub_fullpath, sub_has_files in list_contents(full_path):
                            if sub_has_files:
                                yield sub_fullpath, True
                            else:
                                continue
        
            for subdirectory in self.subdirectories:
                if subdirectory not in BannedDir:
                    if os.path.isdir(subdirectory):
                        DirFolderName.append(subdirectory)
        
            for fullcheckpath in DirFolderName:
                for full_path, has_files in list_contents(fullcheckpath):
                    if has_files:
                        ipathname = os.path.basename(full_path)
                        self.add_path(fullcheckpath, ipathname, full_path)
                    else:
                        pass
        except Exception as e:
            self.Log.LogsMessages(f"[!] An error occurred in 'GeneralPaths': {e}", "Critical")







class Dir:
    def __init__(self):
        self.DirectorySettings = Path_Settings()
        self.paths_settings = self.DirectorySettings.Pathsfile
        self.Log = Logs()
        self.Log.LogEngine("DirectoryManager - Dir", "LogCore_DirectoryManager")
        
        try:
            self.project_path = self.DirectorySettings.checkpath('All_in_One_ServerPath')
            self.subdirectories = os.listdir(self.project_path)
            
                
        except:
            self.Log.LogsMessages("[!] All_in_One_ServerPath nots in Paths.txt", "Critical")
            self.DirectorySettings.EmergencyPaths()
            
        self.project_path = self.DirectorySettings.checkpath('All_in_One_ServerPath')
        self.subdirectories = os.listdir(self.project_path)


    def ListDir(self, mode=False):
        try:
            DirFile = list()
            
            if mode == False:
                for subdirectory in self.subdirectories:
                    self.Log.print_and_log(subdirectory)
                    DirFile.append(subdirectory)
            
            if mode == True:
                for subdirectory in self.subdirectories:
                    DirFile.append(subdirectory)
                return DirFile
        except Exception as e:
            self.Log.LogsMessages(f"[!] An error occurred in 'ListDir': {e}", "Critical")
            
        
    def list_contents(self, path, indent=""):
        try:
            for item in os.listdir(path):
                if item == "__pycache__":
                    continue
                full_path = os.path.join(path, item)
    
                if os.path.isdir(full_path):
                    self.Log.print_and_log(f"{indent}--> {item}:")
                    self.list_contents(full_path, indent + "    ")
                else:
                    self.Log.print_and_log(f"{indent} {item}")
        except Exception as e:
            self.Log.LogsMessages(f"[!] An error occurred in 'list_contents': {e}", "Critical")
            
                
    def ListContentsAllOfSubDir(self, checkfolder=None):
        try:
            if checkfolder is not None:
                for subdirectory in self.subdirectories:
                    if subdirectory == checkfolder:
                        full_path = os.path.join(self.project_path, subdirectory)
                        if os.path.isdir(full_path):
                            self.Log.print_and_log(f"\n     {subdirectory}:")
                            self.list_contents(full_path, "         ")
                        else:
                            self.Log.print_and_log(f"\n     {subdirectory} is not in a directory.")
                            
            else:
                for subdirectory in self.subdirectories:
                    full_path = os.path.join(self.project_path, subdirectory)
                    if os.path.isdir(full_path):
                        self.Log.print_and_log(f"\n     {subdirectory}:")
                        self.list_contents(full_path, "         ")
                    else:
                        self.Log.print_and_log(f"\n     {subdirectory} is not in a directory.")
        except Exception as e:
            self.Log.LogsMessages(f"[!] An error occurred in 'ListContentsAllOfSubDir': {e}", "Critical")


    def ListAllDir(self):
        try:
            self.Log.print_and_log("---- Subdirectories of All_in_One_Server Project ----")
            self.ListDir()
    
            self.Log.print_and_log("\n---- Contents of Subdirectories ----")
            self.ListContentsAllOfSubDir()
        except Exception as e:
            self.Log.LogsMessages(f"[!] An error occurred in 'ListAllDir': {e}", "Critical")

 







class ManageLogDir(Dir):
    def __init__(self):
        super().__init__()
        self.DirectoryPath = Paths_Manager()  
        self.DirectorySettings = Path_Settings()
        self.Log = Logs()
        self.Log.LogEngine("DirectoryManager - ManageLogDir", "LogCore_DirectoryManager")
        
        try:
            self.log_dir = self.DirectorySettings.checkpath('All_in_One_ServerLogs')
            if not self.log_dir or not os.path.isdir(self.log_dir):
                self.Log.LogsMessages("[!] Logs folder not found in Paths.txt. Creating one...", "Critical")
                raise ValueError

            self.log_list = os.listdir(self.log_dir)
        except Exception as e:
            self.Log.LogsMessages(str(e), "warning")
            os.mkdir(self.log_dir)

        self.log_list = os.listdir(self.log_dir)
        
        self.PathSections = list()
        self.MainPath = self.DirectorySettings.checkpath('All_in_One_ServerPath')
        
        for subdirectory in os.listdir(self.MainPath):
            self.PathSections.append(subdirectory)

        self.Core_dir = self.DirectorySettings.checkpath('All_in_One_ServerCore')
        if not self.Core_dir or not os.path.isdir(self.Core_dir):
            self.Log.LogsMessages("[!] All_in_One_ServerCore path not found in Paths.txt", "Critical")
            raise ValueError


    def copy_folder(self, source_folder, destination_folder):
        try:
            if os.path.isdir(source_folder):
                os.makedirs(destination_folder, exist_ok=True)
        
                for item in os.listdir(source_folder):
                    source_item = os.path.join(source_folder, item)
                    destination_item = os.path.join(destination_folder, item)
        
                    if os.path.isfile(source_item):
                        if not os.path.exists(destination_item):
                            self.Log.LogsMessages(f"Creating empty file: {destination_item}", "info")
                            with open(destination_item, 'w') as empty_file:
                                pass
        
                            if os.path.splitext(destination_item)[1] != '.log':
                                os.rename(destination_item, destination_item[:-len(os.path.splitext(destination_item)[1])] + '.log')
                                #filename = os.path.splitext(os.path.basename(destination_item))[0]
                                #self.DirectoryPath.add_path("Logs", filename, destination_item)
        
                    else:
                        self.copy_folder(source_item, destination_item)
    
            else:  # If source_folder is not a directory
                
                for item in os.path.split(source_folder):
                    if item == "settings.json":
                        continue
                    destination_item = os.path.join(self.log_dir, item)
                    if os.path.splitext(destination_item)[1]:  # Check if there's an extension
                        file_destination_item = destination_item[:-len(os.path.splitext(destination_item)[1])] + '.log'
                        if not os.path.exists(file_destination_item):
                            self.Log.LogsMessages(f"Creating empty file: {file_destination_item}", "info")
                            with open(file_destination_item, 'w') as empty_file:
                                pass        
        except Exception as e:
            self.Log.LogsMessages(f"[!] An error occurred in 'copy_folder': {e}", "Critical")


    def copy_CoreLog(self, source_mainfile, destination_logfile):
        try:
            extenLog = destination_logfile[:-len(os.path.splitext(destination_logfile)[1])] + '.log'
            if os.path.isfile(source_mainfile):
                if not os.path.exists(destination_logfile):
                    self.Log.LogsMessages(f"Creating empty file: {extenLog}")
                    with open(extenLog, 'w') as empty_file:
                        pass
                    if os.path.splitext(destination_logfile)[1] != '.log':
                        filename = os.path.splitext(os.path.basename(destination_logfile))[0]
                        self.DirectoryPath.add_path("Logs", "LogCore_"+filename, extenLog)
        except Exception as e:
            self.Log.LogsMessages(f"[!] An error occurred in 'copy_CoreLog': {e}", "Critical")


    def CompareSubDirWithLog(self): # If the log folder has removed or deleted
        try:
            for DirFiles in self.PathSections:
                if DirFiles == "Core":
                    Dir_Folder = self.DirectorySettings.checkpath('All_in_One_Server'+DirFiles)
                    for CoreFile in os.listdir(Dir_Folder):
                        if f"{CoreFile.split('.')[0]}.log" not in self.log_list:   
                            if CoreFile.endswith(".py"):
                                source_mainfile  = os.path.join(self.Core_dir, CoreFile)
                                destination_logfile = os.path.join(self.log_dir, CoreFile)
                                self.copy_CoreLog(source_mainfile, destination_logfile)
                else:
                    Dir_Folder = self.DirectorySettings.checkpath('All_in_One_Server'+DirFiles)
                    for folder in os.listdir(Dir_Folder):
                        source_folder = os.path.join(Dir_Folder, folder)
                        destination_folder = os.path.join(self.log_dir, folder)
            
                        if f"{folder.split('.')[0]}.log" not in self.log_list:
                            self.copy_folder(source_folder, destination_folder)
        except Exception as e:
            self.Log.LogsMessages(f"[!] An error occurred in 'CompareSubDirWithLog': {e}", "Critical")
    
    
    def RepathLogs(self, source_mainfile, destination_logfile):
        try:
            extenLog = os.path.splitext(destination_logfile)[0] + ".log"  # Force .log extension
            if os.path.isfile(source_mainfile):
                if os.path.splitext(destination_logfile)[1] != '.log':
                    filename = os.path.splitext(os.path.basename(destination_logfile))[0]
                    logname = f"LogCore_{filename}"
                    self.DirectoryPath.add_path("Logs", logname, extenLog)
        except Exception as e:
            self.Log.LogsMessages(f"[!] An error occurred in 'RepathLogs': {e}", "Critical")
                   
                                
    def CheckpathLog(self):
        try:
            self.PathCore = {  # Add default paths if needed
                "All_in_One_ServerPath": f"{self.MainPath}",
                "All_in_One_ServerLogs": f"{self.MainPath}Logs"
                } 
    
            for i in self.PathSections:
                self.PathCore["All_in_One_Server"+i] = self.MainPath+i
                
            def explore_folders(base_path, log_dir):
                for root, dirs, files in os.walk(base_path):
                    if os.path.samefile(base_path, self.Core_dir):
                        dirs[:] = [d for d in dirs if d not in ["__pycache__", "Logs"]]
                        
                    for file in files:
                        source_file = os.path.join(root, file)
                        destination_file = os.path.join(log_dir, os.path.relpath(source_file, base_path))
                        self.RepathLogs(source_file, destination_file)
        
                    for subdirectory in dirs:
                        source_folder = os.path.join(root, subdirectory)
                        destination_folder = os.path.join(log_dir, os.path.relpath(source_folder, base_path))
                        self.RepathLogs(source_folder, destination_folder)
        
            for key, value in self.PathCore.items():
                if key != "All_in_One_ServerPath" and key != "All_in_One_ServerLogs":
                    if os.path.exists(value) and os.path.isdir(value):
                        explore_folders(value, self.log_dir)
        except Exception as e:
            self.Log.LogsMessages(f"[!] An error occurred in 'CheckpathLog': {e}", "Critical")
                  
                    
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
                data = json.load(file)
            return data
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            return {}
        
        except Exception as e:
            self.Log.LogsMessages(f"An error occurred while writing to the JSON file: {e}", "CRITICAL")
        
    
    def write_to_process_engine_file(self, script_name_dir, used_terminal_dir, process_id_dir, process_unique_dir):
        try:
            with open(self.MainProcessFile, 'r') as json_file:
                data = json.load(json_file)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            data = {}
            
        except Exception as e:
            self.Log.LogsMessages(f"An error occurred while writing to the JSON file: {e}", "CRITICAL")
            
        key = script_name_dir
        data[key] = {
            "Used Terminal": used_terminal_dir,
            "Process ID": process_id_dir,
            "Unique ID": process_unique_dir
        }

        try:
            with open(self.MainProcessFile, 'w') as json_file:
                json.dump(data, json_file, indent=4)
        except Exception as e:
            self.Log.LogsMessages(f"An error occurred while writing to the JSON file: {e}", "CRITICAL")
        
        self.Log.LogsMessages(f"[+] {script_name_dir} - {process_id_dir} - {process_unique_dir} started", "INFO")
    
    
    def delete_from_process_engine_file(self, script_name_dir, process_id_dir, process_unique_dir):
        try:
            with open(self.MainProcessFile, 'r') as json_file:
                data = json.load(json_file)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            return
        except Exception as e:
            self.Log.LogsMessages(f"An error occurred while deleting from the JSON file: {e}", "CRITICAL")
            
        key = script_name_dir
        if key in self.ReadProcesses():
            if "Unique ID" in data[key] and data[key]["Unique ID"] == process_unique_dir:
                if "Process ID" in data[key] and data[key]["Process ID"] == process_id_dir:
                    
                    try:
                        del data[key]
                    except Exception as e:
                        self.Log.LogsMessages(f"An error occurred while deleting from the JSON file: {e}", "CRITICAL")
                              
                    with open(self.MainProcessFile, 'w') as json_file:
                        json.dump(data, json_file, indent=4)
                        
                    self.Log.LogsMessages(f"[-] {script_name_dir} - {process_id_dir} - {process_unique_dir} stopped", "WARNING")












    

if __name__ == "__main__":
    
    #print(Paths_Manager().CheckMainPath())
    #Paths_Manager().SectionPath()

    #Paths_Manager().add_path("kassam", "nameid", "202110022")
    #Paths_Manager().Reset_Paths()
    
    #ManageLogDir().CompareSubDirWithLog()
    #ManageLogDir().CheckpathLog()
    
    
    #Paths_Manager().remove_path("Weapons" ,"serverchat.py")
    
    #Dir().ListAllDir()
    ManageLogDir().MainLog()
    Dir().ListAllDir()