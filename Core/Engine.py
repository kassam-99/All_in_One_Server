# Libraries to handle I/O files, folders and Manage a system
import os
import subprocess
import uuid
import psutil
import multiprocessing
import time
from datetime import datetime, timedelta


# Other:
from Log import Logs
from Settings import Server_Settings, Path_Settings
from DirectoryManager import ProcessManager
from SysMonitor import RealTime_Process

     
     
     
     

class EngineServer():
    def __init__(self):
        self.engine_logs = Logs()
        self.engine_logs.LogEngine("Engine - EngineServer", "LogCore_Engine")
        self.Engine_ServerSettings = Server_Settings()
        self.Engine_PathSettings = Path_Settings()
        self.Engine_ProcessManager = ProcessManager()
        self.Engine_Realtime_Process = RealTime_Process()
        
        self.Script_Operation = dict()
        self.Script_Params = dict()
        
        self.system_type = self.Engine_ServerSettings.check_system()
     
        """
        self.Script_Operation[script_nickname_process] = {
            'terminal': terminal,
            'pid': process_id,
            'Unique ID': process_unique
        }
        """

     
     
     
     

class ProcessEngine(EngineServer):
    def __init__(self):
        super().__init__()


    def find_process_id_by_name(self, script_name):
        process_id = None
        process_id_list = list()
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if script_name in proc.info['name'] or (proc.info['cmdline'] and script_name in ' '.join(proc.info['cmdline'])):
                    process_id_check = proc.info['pid']
                    process_id_list.append(process_id_check)
        except Exception as e:
            self.engine_logs.LogsMessages(f"[!] Error while checking process ID - {script_name}: {e}","ERROR")
                
        for check in process_id_list:
            if check not in self.Script_Operation.values():
                process_id = check
            
        return process_id


    def get_process_id_by_name(self, script_name):
        try:
            if self.system_type == "Linux":
                process_id = self.find_process_id_by_name(script_name)
                if process_id is not None:
                    return process_id
                else:
                    self.engine_logs.print_and_log("[!] No process found", "CRITICAL")
                    
            elif self.system_type == "Darwin":
                process_id = self.find_process_id_by_name(script_name)
                if process_id is not None:
                    return process_id
                else:
                    self.engine_logs.print_and_log("[!] No process found", "CRITICAL")
                    
            elif self.system_type == "Windows":
                process_id = None
                command = f'tasklist /FI "IMAGENAME eq {script_name}" /NH'
                result = os.popen(command).read()
                lines = result.strip().split('\n')
                
                if len(lines) > 1:
                    process_id = int(lines[0].split()[1])
                    return process_id
                else:
                    self.engine_logs.print_and_log("[!] No process found", "CRITICAL")

        except Exception as e:
            self.engine_logs.print_and_log(f"[!] Error: {str(e)}", "ERROR")
            
        
    def Process_Organiser(self, script_name_process, terminal, script_nickname_process=None):
        process_id_org = self.get_process_id_by_name(script_name_process)
        
        if process_id_org == None:
            self.engine_logs.print_and_log("[!] Couldn't launch a script", "CRITICAL")
            
        else:
            process_unique = str(uuid.uuid4())
            if 'Unique ID' in self.Script_Operation:
                existing_unique_id = self.Script_Operation['Unique ID']
                while existing_unique_id == process_unique:
                    process_unique = str(uuid.uuid4())
            
            if script_nickname_process is not None:           
                self.engine_logs.print_and_log(f"{script_nickname_process} - Unique ID {process_unique}")
                self.Script_Operation[script_nickname_process] = {'terminal': terminal, 'pid': process_id_org, 'Unique ID': process_unique} 
                self.Engine_ProcessManager.write_to_process_engine_file(script_name_dir=script_nickname_process, used_terminal_dir=terminal, process_id_dir=process_id_org, process_unique_dir=process_unique)         
            
            elif script_name_process in self.Script_Operation:
                i = 2
                while f"{script_name_process} ({i})" in self.Script_Operation:
                    i += 1
                SameScript = f"{script_name_process} ({i})"
                self.engine_logs.print_and_log(f"{SameScript} - Unique ID {process_unique}")
                self.Script_Operation[SameScript] = {'terminal': terminal, 'pid': process_id_org, 'Unique ID': process_unique}
                self.Engine_ProcessManager.write_to_process_engine_file(script_name_dir=SameScript, used_terminal_dir=terminal, process_id_dir=process_id_org, process_unique_dir=process_unique)
                
            else:
                self.engine_logs.print_and_log(f"{script_name_process} - Unique ID {process_unique}")
                self.Script_Operation[script_name_process] = {'terminal': terminal, 'pid': process_id_org, 'Unique ID': process_unique}
                self.Engine_ProcessManager.write_to_process_engine_file(script_name_dir=script_name_process, used_terminal_dir=terminal, process_id_dir=process_id_org, process_unique_dir=process_unique)
     
     
     
     
     

class ScriptEngine(ProcessEngine):
    def __init__(self):
        super().__init__()


    def start_running(self, start_script_name, start_user_choice_terminal, start_script_nickname=None, params=None):
        
        
        script_path = self.Engine_PathSettings.checkpath(start_script_name)
        
        if script_path is None:
            self.engine_logs.print_and_log(f"[!] Script '{start_script_name}' not found.", "CRITICAL")
            return
        
        if not os.path.exists(script_path):
            self.engine_logs.print_and_log(f"[!] Script '{start_script_name}' not found at path: {script_path}", "CRITICAL")
            return
        
        script_path = self.Engine_PathSettings.checkpath(start_script_name)
        
        script_extension = os.path.splitext(start_script_name)[1].lower()
        extension_to_command = {
            '.py': 'python',
            '.sh': 'bash',
            '.js': 'node',
            '.rb': 'ruby',
            '.php': 'php',
            '.bat': 'cmd',
            '.cpp': 'g++',
            '.java': 'java',
            '.pl': 'perl',
            '.ps1': 'powershell',
            '.psm1': 'powershell',
            '.vbs': 'cscript', 
        }
        
        if script_extension in extension_to_command:
            interpreter = extension_to_command[script_extension]
        else:
            self.engine_logs.print_and_log(f"[!] Unsupported script language for file: {start_script_name}", "CRITICAL")
            return
            
        if self.system_type == "Windows":
            command = f"{interpreter} {script_path}"
            self.engine_logs.LogsMessages(f"[+] Executing command: {command}", "INFO")
        elif self.system_type == "Linux":
            command = f"{interpreter} {script_path}"
            self.engine_logs.LogsMessages(f"[+] Executing command: {command}", "INFO")
        elif self.system_type == "Darwin":
            command = f"{interpreter} {script_path}"
            self.engine_logs.LogsMessages(f"[+] Executing command: {command}", "INFO")
        else:
            self.engine_logs.print_and_log(f"[!] Unsupported operating system: {self.system_type}", "CRITICAL")
        
        if start_script_name in self.Script_Params:
            for key, value in self.Script_Params[start_script_name].items():
                params = value
        
        if params is not None:
            if isinstance(params, list):
                command += " " + " ".join(params)
            else:
                command += f" {params}"
            
            self.Script_Params[start_script_name] = {'Params': params} 
            
        if isinstance(start_user_choice_terminal, int):    
            available_terminals = self.Engine_ServerSettings.get_available_terminals(self.system_type)
            chosen_terminal = available_terminals[start_user_choice_terminal - 1]
        
        if isinstance(start_user_choice_terminal, str):
            chosen_terminal = start_user_choice_terminal
            
        try:
            if start_script_nickname is not None:
                self.execute_script_multiprocess(command=command, user_choice_terminal=chosen_terminal, script_name=start_script_name, script_nickname=start_script_nickname)
                self.engine_logs.LogsMessages(f"{start_script_name} completed - nickname: {start_script_nickname}")                
            else:
                self.execute_script_multiprocess(command=command, user_choice_terminal=chosen_terminal, script_name=start_script_name)
                self.engine_logs.LogsMessages(f"{start_script_name} completed")

        except Exception as e:
            error_message = f"[!] Error executing script: {str(e)}"
            self.engine_logs.LogsMessages(error_message, "ERROR")

        except KeyboardInterrupt:
            self.engine_logs.LogsMessages("[!] Script execution interrupted by the user.", "Warning")

        finally:
            pass


    def execute_script(self, command, choice_terminal):
        
        try:

            try:
                if self.system_type == "Windows":
                    if choice_terminal == "cmd":
                        process = subprocess.Popen(["start", "cmd", "/k", command], shell=True)
                        
                    elif choice_terminal == "powershell":
                        process = subprocess.Popen(["start", "powershell", command], shell=True)
                        
                elif self.system_type == "Linux":
                    if "gnome-terminal" == choice_terminal:
                        process = subprocess.Popen(["gnome-terminal", "-e", command], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        
                    elif "konsole" == choice_terminal:
                        process = subprocess.Popen(["konsole", "--noclose", "-e", command], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        
                    elif "xfce4-terminal" == choice_terminal:
                        process = subprocess.Popen(["xfce4-terminal", "--command= " + command], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        
                    elif "terminator" == choice_terminal:
                        process = subprocess.Popen(["terminator", "-e", command], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        
                    elif "xterm" == choice_terminal:
                        process = subprocess.Popen(["xterm", "-e", command], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                                               
                elif self.system_type == "Darwin":
                        if choice_terminal == "Terminal":
                            process = subprocess.Popen(["open", "-a", "Terminal", "-c", command], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            
                        elif choice_terminal == "iTerm":
                            process = subprocess.Popen(["open", "-a", "iTerm", "--args", "-e", command], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            
                        elif choice_terminal == "Alacritty":
                            process = subprocess.Popen(["open", "-a", "Alacritty", "-e", command], stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # Assuming Alacritty is installed

                        
            except FileNotFoundError:
                self.engine_logs.print_and_log(f"[!] Terminal '{choice_terminal}' not found.", "ERROR")

            except Exception as e:
                self.engine_logs.print_and_log(f"[!] Couldn't launch a script: {e}", "ERROR")

        except IndexError:
            self.engine_logs.print_and_log("[!] Invalid terminal choice.", "ERROR")

        except subprocess.CalledProcessError as e:
            error_message = f"[!] Error executing script: {e.returncode}"
            self.engine_logs.print_and_log(error_message, "ERROR")
        except NotImplementedError as e:
            error_message = f"[!] Error executing script: {str(e)}"
            self.engine_logs.print_and_log(error_message, "ERROR")
        except KeyboardInterrupt:
            self.engine_logs.print_and_log("[!] Script execution interrupted by the user.", "WARNING")
        except Exception as e:
            error_message = f"[!] Unexpected error: {str(e)}"
            self.engine_logs.print_and_log(error_message, "WARNING")
        finally:
            pass


    def execute_script_multiprocess(self, command, user_choice_terminal, script_name, script_nickname=None):
        try:
            process = multiprocessing.Process(target=self.execute_script, args=(command,user_choice_terminal))
            process.start()
            
            time.sleep(1)
            
            self.Engine_Realtime_Process.ProcessAlert(script_name)
            
            if script_nickname is not None:
                self.Process_Organiser(script_name_process=script_name, terminal=user_choice_terminal, script_nickname_process=script_nickname)
            
            else:
                self.Process_Organiser(script_name_process=script_name, terminal=user_choice_terminal)
                
        except Exception as e:
            error_message = f"[!] Error executing script: {str(e)}"
            self.engine_logs.LogsMessages(error_message, "ERROR")
            
        except KeyboardInterrupt:
            self.engine_logs.LogsMessages("[!] Script execution interrupted by the user.", "Warning")
        
        finally:
            pass


    def stop_running(self, script_name):
        if script_name in self.Script_Operation:
            process_info = self.Script_Operation.pop(script_name)
            process_script_pid = process_info['pid']
            process_script_id = process_info['Unique ID']
            process = psutil.Process(process_script_pid)
            self.Engine_ProcessManager.delete_from_process_engine_file(script_name_dir=script_name, process_id_dir=process_script_pid, process_unique_dir=process_script_id)
            message_stop = f"{script_name} - Terminated successfully"
            self.Engine_Realtime_Process.send_notification("Information - Stop", message_stop)
        else:
            self.engine_logs.print_and_log(f"[!] {script_name} not found in running scripts.", "WARNING")
            return
    
        try:
            process.kill()
            self.engine_logs.print_and_log(f"[-] Process with PID {process_script_pid} terminated successfully.", "WARNING")
        except psutil.NoSuchProcess:
            self.engine_logs.print_and_log(f"[!] Process with PID {process_script_pid} not found.", "WARNING")
        except psutil.AccessDenied:
            self.engine_logs.print_and_log(f"[!] Access denied. Unable to terminate process with PID {process_script_pid}.", "WARNING")
        except Exception as e:
            self.engine_logs.print_and_log(f"[!] Error terminating process with PID {process_script_pid}: {e}", "ERROR")
        
       
    def show_running(self):
        for script_name, operation_info in self.Script_Operation.items():
            terminal = operation_info.get('terminal')
            script_pid = operation_info.get('pid')
            script_id = operation_info.get('Unique ID')
            
            try:
                process = psutil.Process(script_pid)

                if terminal is not None and script_pid is not None and self.is_process_running_show(pid=script_pid):
                    status = "Running"
                    running_time = self.get_running_time_show(script_pid)
                    self.print_script_info(script_name, terminal, script_pid, status, running_time, script_id, process)

                else:
                    self.print_script_info(script_name, terminal, script_pid, "Not Running", 0, script_id, None)

            except psutil.NoSuchProcess:
                self.print_script_info(script_name, terminal, script_pid, "Not Running", 0, script_id, None)

    def print_script_info(self, script_name, terminal, script_pid, status, running_time, script_id, process):
        self.engine_logs.print_and_log("\n")
        self.engine_logs.print_and_log(f"[$] Script: {script_name}")
        self.engine_logs.print_and_log(f"[╼] Terminal: {terminal}")
        self.engine_logs.print_and_log(f"[╼] Status: {status}")
        self.engine_logs.print_and_log(f"[╼] PID: {script_pid}")
        self.engine_logs.print_and_log(f"[╼] Running Time: {running_time}")
        self.engine_logs.print_and_log(f"[╼] Unique ID: {script_id}")

        if process:
            self.engine_logs.print_and_log(f"[╼] CPU Usage: {process.cpu_percent()}%")
            self.engine_logs.print_and_log(f"[╼] Memory Usage: {process.memory_info().rss / (1024 ** 2):.2f} MB")
               

    def is_process_running_show(self, pid):
        try:
            return psutil.pid_exists(pid)
        except Exception as e:
            self.engine_logs.print_and_log(f"[!] Error checking process status for PID {pid}: {e}")
            return False
        
        
    def get_running_time_show(self, pid):
        try:
            process = psutil.Process(pid)
            create_time = process.create_time()
            current_time = datetime.now().timestamp()
            running_time_seconds = current_time - create_time
            running_time = str(timedelta(seconds=running_time_seconds))
            return running_time

        except Exception as e:
            self.engine_logs.print_and_log(f"[!] Error getting running time for PID {pid}: {e}")
            return "N/A"
        

    def rename_running(self, script_name_old, script_name_new):
        found_old_name = None
        terminal_old = None
        for script_name, operation_info in self.Script_Operation.items():  
            if script_name.strip() == script_name_old.strip():
                found_old_name = script_name
                terminal_old = operation_info.get('terminal')
                break
            
        if found_old_name is None:
            for script_name in self.Script_Operation:
                self.engine_logs.print_and_log(f"[-] '{repr(script_name.strip())}'")
            self.engine_logs.print_and_log(f"[!] {script_name_old} not found :( retry again ", "WARNING")
            return
    
        if script_name_new in self.Script_Operation:
            self.engine_logs.print_and_log(f"[!] {script_name_new} already exists. Choose a different name.")
        else:
            self.stop_running(script_name=script_name_old)
            time.sleep(1)
            self.start_running(start_script_name=script_name_old, start_user_choice_terminal=terminal_old, start_script_nickname=script_name_new)
    
            self.engine_logs.print_and_log(f"[+] {found_old_name} -> {script_name_new} changed successfully !")
            message_rename = f"{found_old_name} -> {script_name_new} changed successfully"
            self.Engine_Realtime_Process.send_notification("Information - Rename", message_rename)

    
    def restart_script(self, script_name_restart):
        script = None
        terminal = None
        for script_name, operation_info in self.Script_Operation.items():  
            if script_name.strip() == script_name_restart.strip():
                script = script_name
                terminal = operation_info.get('terminal')
                break

        if script is None:
            for script_name in self.Script_Operation:
                self.engine_logs.print_and_log(f"[-] '{repr(script_name.strip())}'")
            self.engine_logs.print_and_log(f"[!] {script} not found :( retry again ", "WARNING")
            return
            
        if script in self.Script_Operation:
            self.stop_running(script)
            time.sleep(1)
            self.start_running(start_script_name=script_name, start_user_choice_terminal=terminal)
            
            self.engine_logs.print_and_log(f"[+] Script '{script_name}' restarted successfully.")
            message_restart = f"Script '{script_name}' restarted successfully."
            self.Engine_Realtime_Process.send_notification("Information - Restart", message_restart)
        else:
            self.engine_logs.print_and_log(f"[!] Script '{script_name}' not found :( retry again ", "WARNING")
        
        
    def stop_all_running(self):
        for script_name in list(self.Script_Operation.keys()):
            self.stop_running(script_name)

        self.engine_logs.print_and_log("[!] All running scripts stopped.", "CRITICAL")
        message_stop_all = "All running scripts stopped."
        self.Engine_Realtime_Process.send_notification("Information - Stop/All ", message_stop_all)
     
     
     
     
    


if __name__ == "__main__":
    pass