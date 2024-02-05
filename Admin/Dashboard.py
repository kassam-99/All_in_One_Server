# Libraries to handle I/O files, folders and Manage a system
import multiprocessing
import os
import signal
import subprocess
import sys
from io import StringIO


# Get the project root directory (two levels up from the script)
project_root = os.path.abspath(__file__)
index = project_root.find("All_in_One_Server")
if index != -1:
    core_dir = project_root[:index+18]+"Core"
sys.path.append(core_dir)

if os.name == 'nt': # Only if we are running on Windows
    from ctypes import windll
    k = windll.kernel32
    k.SetConsoleMode(k.GetStdHandle(-11), 7)

# Other:
from Engine import ScriptEngine
from Modes import ModeManager
from Log import Logs
from Settings import Server_Settings, Path_Settings
from Emergency import EmergencyPathManager
from SysMonitor import RealTime_Dir, Sensor
from Commands import *




class Dashboard_Panel:
    def __init__(self):
        EmergencyPathManager().StartEmergencyModePath()
        self.log_dashboard = Logs()
        self.log_dashboard.LogEngine("Dashboard_Panel", "LogCore_Dashboard")
        
        self.mode_dashboard = ModeManager()
        self.run_dashboard = ScriptEngine()
        self.settings_dashboard = Server_Settings()
        self.path_dashboard = Path_Settings()
        self.RealTime_Dir_dashboard = RealTime_Dir()
        self.Sensor_dashboard = Sensor()
        self.system_found = self.settings_dashboard.check_system()
        
        self.main_commands = {
            "list": lambda: self.mode_dashboard.list_modes(True),
            "rename": lambda: self.run_dashboard.rename_running(input("[>] Enter script name to rename: "), input("[>] Enter a new name: ")),
            "stop": lambda: self.run_dashboard.stop_running(input("[>] Enter script name to stop: ")),
            "stop_all": self.run_dashboard.stop_all_running,
            "restart": lambda: self.run_dashboard.restart_script(input("[>] Enter script name to restart: ")),
            "map": lambda: self.mode_dashboard.list_modes(True),
            "info": self.Sensor_dashboard.Start_Sensor,
            "show": self.run_dashboard.show_running,
            "help": lambda: print(cmd_command),
            "read": banner
        }


    def capture_output(self, func, *args, **kwargs):
        original_stdout = sys.stdout
        sys.stdout = StringIO()

        try:
            func(*args, **kwargs)
            output = sys.stdout.getvalue()
            return output
        except Exception as e:
            self.log_dashboard.LogsMessages(f"\n{project_name_terminal} [\033[31m!\033[0m] Invalid capture_output: {e}", "ERROR") 
        
        finally:
            sys.stdout = original_stdout
            

    def main(self, func, *args, **kwargs):
        try:
            with StringIO() as self.capture_output:
                sys.stdout = self.capture_output
                func(*args, **kwargs)
                output = self.capture_output.getvalue()
        finally:
            sys.stdout = sys.__stdout__

        files = self.mode_dashboard.extract_folders_and_files(output)

        for i, file in enumerate(files, start=1):
            self.log_dashboard.print_and_log(f"[{i}] {file}")

        try:
            selected_file_index = int(input(f"\n{project_name_terminal} [>] Enter the file option to run: "))
            
            selected_file = files[selected_file_index - 1]
            self.log_dashboard.print_and_log(f"\n{project_name_terminal} [>] Script selected {selected_file}")
            self.settings_dashboard.get_available_terminals(self.system_found, True)
            
            terminal_mode = int(input(f"\n{project_name_terminal} [>] Enter the terminal option to use: "))
            
            add_params = input(f"\n{project_name_terminal} [>] Do you want to add parameters? (y/n): ").lower()
            if add_params == "y":
                params = input(f"\n{project_name_terminal} [>] Enter parameters (separated by space): ").split()
                self.run_dashboard.start_running(start_script_name=selected_file, start_user_choice_terminal=terminal_mode, params=params)
            else:
                self.run_dashboard.start_running(start_script_name=selected_file, start_user_choice_terminal=terminal_mode)
        
        except (ValueError, IndexError):
            self.log_dashboard.print_and_log(f"\n{project_name_terminal} [\033[31m!\033[0m] Invalid input.") 
            

    def Main_Dashboard(self):
        terminals = self.settings_dashboard.get_available_terminals(self.system_found)
        adminscript = self.path_dashboard.checkpath("AdminPanel.py")
        
        for logo in ListLogo:
            print(logo)
            break

        process1 = multiprocessing.Process(target=self.RealTime_Dir_dashboard.Start_Monitor)
        process1.start()

        if terminals:
            choice_terminal = terminals[0]  # Choose the first available terminal

            if self.system_found == "Windows":
                if choice_terminal.lower() == "cmd":
                    process2 = subprocess.Popen(["start", "cmd",  "/c", f"python {adminscript}"], shell=True)
                elif choice_terminal.lower() == "powershell":
                    process2 = subprocess.Popen(["start", "powershell", f"python {adminscript}"], shell=True)

            elif self.system_found == "Linux":
                if choice_terminal == "gnome-terminal":
                    process2 = subprocess.Popen(f'gnome-terminal -- bash -c "python {adminscript}"', shell=True)
                elif choice_terminal == "konsole":
                    process2 = subprocess.Popen(f'konsole --noclose -e "python {adminscript}"', shell=True)
                elif choice_terminal == "xfce4-terminal":
                    process2 = subprocess.Popen(f'xfce4-terminal --command="python {adminscript}"', shell=True)
                elif choice_terminal == "terminator":
                    process2 = subprocess.Popen(f'terminator -e "python {adminscript}"', shell=True)
                elif choice_terminal == "xterm":
                    process2 = subprocess.Popen(f'xterm -e "python {adminscript}"', shell=True)

            elif self.system_found == "Darwin":
                if choice_terminal == "Terminal":
                    process2 = subprocess.Popen(f'open -a Terminal -c "python {adminscript}"', shell=True)
                elif choice_terminal == "iTerm":
                    process2 = subprocess.Popen(f'open -a iTerm --args -e "python {adminscript}"', shell=True)
                elif choice_terminal == "Alacritty":
                    process2 = subprocess.Popen(f'open -a Alacritty -e "python {adminscript}"', shell=True)

        else:
            print("[!] No compatible terminals found for the launching admin panel")

        try:
            while True:
                            
                user_input = input(f"\n{project_name_terminal} [>] Enter option: ").lower()
                    
                if user_input == "exit":
                    os.killpg(os.getpgid(process2.pid), signal.SIGTERM)
                    os.abort()
                    
                if user_input.lower() in self.main_commands:
                    self.main_commands[user_input]()
    
                    if user_input.lower() == "map":
                        user_input_map = input(f"\n{project_name_terminal} [>] Enter option - mapping: ")
                    
                        if user_input_map.isdigit() and 1 <= int(user_input_map) <= len(self.mode_dashboard.available_modes):
                            self.mode_dashboard.select_mode(self.mode_dashboard.available_modes[int(user_input_map) - 1])
                        else:
                            self.log_dashboard.print_and_log(f"\n{project_name_terminal} [\033[31m!\033[0m] Invalid input: {user_input_map}. Type 'list' to see available modes.")
                        
                elif user_input.isdigit() and 1 <= int(user_input) <= len(self.mode_dashboard.available_modes):
                    self.main(self.mode_dashboard.select_mode, self.mode_dashboard.available_modes[int(user_input) - 1])
                    
                else:
                    self.log_dashboard.print_and_log(f"\n{project_name_terminal} [\033[31m!\033[0m] Invalid input: {user_input}. Type 'list' to see available modes.")
        
           
        except EOFError:
            pass

        except Exception as e:
            self.log_dashboard.LogsMessages(f"\n{project_name_terminal} [\033[31m!\033[0m] Unexpected Error {e}", "ERROR")

        except KeyboardInterrupt:
            os.abort()
            



if __name__ == "__main__":
    Dashboard_Panel().Main_Dashboard()