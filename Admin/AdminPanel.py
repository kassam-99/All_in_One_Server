import os
import sys
import json
from io import StringIO
from datetime import datetime
from collections import defaultdict 

if os.name == 'nt': # Only if we are running on Windows
    from ctypes import windll
    k = windll.kernel32
    k.SetConsoleMode(k.GetStdHandle(-11), 7)

# Get the project root directory (two levels up from the script)
project_root = os.path.abspath(__file__)
index = project_root.find("All_in_One_Server")
if index != -1:
    core_dir = project_root[:index+18]+"Core"
sys.path.append(core_dir)

# Other:

from Engine import ScriptEngine
from Modes import ModeManager
from Log import Logs
from Settings import Server_Settings, Path_Settings, TCP_Server
from SysMonitor import Sensor
from Commands import *




        













class Admin:
    def __init__(self):
        self.AdminLog = Logs()
        self.AdminEngine = ScriptEngine()
        self.AdminModes = ModeManager()
        self.AdminServerSettings = Server_Settings()
        self.AdminPathSettings = Path_Settings()
        self.AdminSensor = Sensor()
        self.AdminServerConnection = TCP_Server(self.AdminServerSettings.server_main_ip, self.AdminServerSettings.server_main_port) 
        
        self.AdminLog.LogEngine("AdminPanel", "LogCore_AdminPanel")
        
        self.system_found = self.AdminServerSettings.check_system()
        
        try:
            self.AdminServerConnection.start_TCP_Server()
        except Exception as e:
            self.AdminLog.print_and_log(f"\n{projet_name_admin} \033[31m[!]\033[0m Error while starting admin server: {e}")
            self.AdminServerConnection.tcp_handler.close()
            
        self.main_commands = {
            "list": lambda: self.AdminModes.list_modes(True),
            "rename": lambda r_parm=None, f_parm=None: self.AdminEngine.rename_running(r_parm, f_parm),
            "stop": lambda parm=None: self.AdminEngine.stop_running(parm),
            "stop_all": self.AdminEngine.stop_all_running,
            "restart": lambda parm=None: self.AdminEngine.restart_script(parm),
            "map": lambda: self.AdminModes.list_modes(True),
            "info": self.AdminSensor.Start_Sensor,
            "show": self.AdminEngine.show_running,
            "help": cmd_command,
            "read": banner
        }
        
        self.username = self.AdminServerSettings.ServerName
        self.password = self.AdminServerSettings.ServerPassword
        self.MSize = 2048  
        self.FParm = None
        self.RParm = None     


        







class AdminControl(Admin):
    def __init__(self):
        super().__init__()

    def Send_Admin(self, msg, conn, sendlog="info", PureMsg=None):
        try:
            if PureMsg == "AdminInfo":
                conn.send(msg.encode())
            else:
                if sendlog != "info":
                    self.AdminLog.print_and_log(msg, sendlog)
                else:
                    self.AdminLog.LogsMessages(msg)
                    
                conn.sendall(msg.encode())
                
        except OSError as e:
            if e.errno == 9:  # Bad file descriptor
                self.AdminLog.LogsMessages(f"\n{projet_name_admin} \033[31m[!]\033[0m Error sending message: {e} (Client socket closed)", "error")
            else:
                self.AdminLog.LogsMessages(f"\n{projet_name_admin} \033[31m[!]\033[0m Error sending message: {e}", "error")


    def Recv_Admin(self, conn):
        try:
            data = conn.recv(self.MSize)
            decoded_data = data.decode(errors='ignore')  # Set errors to 'ignore'
            self.AdminLog.LogsMessages(decoded_data)
            return decoded_data
        except OSError as e:
            if e.errno == 9:  # Bad file descriptor
                self.AdminLog.LogsMessages(f"\n{projet_name_admin} \033[31m[!]\033[0m Error receiving message: {e} (Client socket closed)", "error")
            else:
                self.AdminLog.LogsMessages(f"\n{projet_name_admin} \033[31m[!]\033[0m Error receiving message: {e}", "error")
            return ""
        
        
    def CaptureCode_Admin(self, func, *args, **kwargs):

        try:
            with StringIO() as capture_output:
                sys.stdout = capture_output
                func(*args, **kwargs)
                output = capture_output.getvalue()
                return output
        finally:
            sys.stdout = sys.__stdout__
            

    def Main_Admin(self, conn_client, func, *args, **kwargs):
        try:
            with StringIO() as capture_output:
                sys.stdout = capture_output
                func(*args, **kwargs)
                output = capture_output.getvalue()
                files = self.AdminModes.extract_folders_and_files(output)
                
        finally:
            sys.stdout = sys.__stdout__

        try:
            accumulated_output = ""
            for i, file in enumerate(files, start=1):
                accumulated_output += f"[{i}] {file}\n"
            self.Send_Admin(accumulated_output, conn_client)
        
        except Exception as e:
            ErrorFound = f"{projet_name_admin} \033[31m[!]\033[0m Error: {e}"
            self.Send_Admin(ErrorFound, conn_client, "error")
            
        try:
            self.Send_Admin(f"{projet_name_admin} \033[34m[>]\033[0m Enter the file option to run: ", conn_client)
            selected_file_index = int(self.Recv_Admin(conn_client))
            selected_file = files[selected_file_index - 1]
            self.Send_Admin(f"{projet_name_admin} \033[34m[>]\033[0m Script selected {selected_file}", conn_client)
            
        except (ValueError, IndexError, Exception) as e:
            ErrorFound = f"{projet_name_admin} \033[31m[!]\033[0m  Invalid input: {e}"
            self.Send_Admin(ErrorFound, conn_client, "error")
            
        try:
            accumulated_output_terminal = ""
            accumulated_output_terminal += "[*] Available terminals:\n"
            available_terminals = self.AdminServerSettings.get_available_terminals(self.system_found)
            for i, terminal in enumerate(available_terminals, start=1):
                accumulated_output_terminal += f"[{i}] {terminal}\n"
                
            self.Send_Admin(accumulated_output_terminal, conn_client)
            
        except (ValueError, IndexError, Exception) as e:
            ErrorFound = f"{projet_name_admin} \033[31m[!]\033[0m Invalid input: {e}"
            self.Send_Admin(ErrorFound, conn_client, "error")
            
        try:
            self.Send_Admin(f"{projet_name_admin} \033[34m[>]\033[0m Enter the terminal option to use: ", conn_client)
            terminal_mode = int(self.Recv_Admin(conn_client))
        
            self.Send_Admin(f"{projet_name_admin} \033[34m[>]\033[0m Do you want to add parameters? (y/n): ", conn_client)
            add_params = self.Recv_Admin(conn_client)
            if add_params == "y":
                self.Send_Admin(f"{projet_name_admin} \033[34m[>]\033[0m Enter parameters (separated by space): ", conn_client)
                params = self.Recv_Admin(conn_client)
                
                self.AdminEngine.start_running(start_script_name=selected_file, start_user_choice_terminal=terminal_mode, params=params)
            else:
                self.AdminEngine.start_running(start_script_name=selected_file, start_user_choice_terminal=terminal_mode)
        
        except (ValueError, IndexError):
            ErrorFound = f"{projet_name_admin} \033[31m[!]\033[0m Invalid input."
            self.Send_Admin(ErrorFound, conn_client, "error")
             

    def Control_Admin(self, data_recv_control, client_socket_control):
        
        response = None

        if data_recv_control.lower() == "help":
            response = self.main_commands[data_recv_control.lower()]
            
        elif data_recv_control.lower() == "stop":
            self.Send_Admin(f"{projet_name_admin} \033[34m[>]\033[0m Enter script name to stop: ", client_socket_control)
            self.FParm = self.Recv_Admin(client_socket_control)
            response_func = self.main_commands[data_recv_control.lower()]
            response = self.CaptureCode_Admin(response_func, self.FParm)
            self.Send_Admin(f"{projet_name_admin} \033[31m[!]\033[0m Script {self.FParm} stopped", client_socket_control)

        elif data_recv_control.lower() == "restart":
            self.Send_Admin(f"{projet_name_admin} \033[34m[>]\033[0m Enter script name to restart: ", client_socket_control)
            self.FParm = self.Recv_Admin(client_socket_control)
            response_func = self.main_commands[data_recv_control.lower()]
            response = self.CaptureCode_Admin(response_func, self.FParm)
            self.Send_Admin(f"{projet_name_admin} \033[31m[!]\033[0m Script {self.FParm} restarted", client_socket_control)

        elif data_recv_control.lower() == "rename": 
            self.Send_Admin(f"{projet_name_admin} \033[34m[>]\033[0m Enter script name to rename: ", client_socket_control)
            self.FParm = self.Recv_Admin(client_socket_control)
            self.Send_Admin(f"{projet_name_admin} \033[34m[>]\033[0m Enter a new name: ", client_socket_control)
            self.RParm = self.Recv_Admin(client_socket_control)
            response_func = self.main_commands[data_recv_control.lower()]
            response = self.CaptureCode_Admin(response_func, self.FParm, self.RParm)
            self.Send_Admin(f"{projet_name_admin} \033[31m[!]\033[0m Script {self.FParm} stopped", client_socket_control)
            
        elif data_recv_control.lower() == "map":
            response_func = self.main_commands[data_recv_control.lower()]
            response = self.CaptureCode_Admin(response_func)
            self.Send_Admin(str(response), client_socket_control)
            self.Send_Admin(f"{projet_name_admin} \033[34m[>]\033[0m Enter option - mapping: ", client_socket_control)

            try:
                self.FParm = self.Recv_Admin(client_socket_control)
                user_input_map = int(self.FParm)
                if 1 <= user_input_map <= len(self.AdminModes.available_modes):
                    selected_mode = self.AdminModes.available_modes[user_input_map - 1]
                    self.Send_Admin(f"{projet_name_admin} \033[33m[>]\033[0m Mode selected: {selected_mode}", client_socket_control)
                    response = self.CaptureCode_Admin(self.AdminModes.select_mode, selected_mode)
                    
                else:
                    self.Send_Admin(f"{projet_name_admin} \033[31m[!]\033[0m Invalid input: {user_input_map}. Type 'list' to see available modes.", client_socket_control, "error")
            except ValueError:
                self.Send_Admin(f"{projet_name_admin} \033[31m[!]\033[0m Invalid input: {self.FParm}. Please enter a number.", client_socket_control, "error")
    

        else:            
            response_func = self.main_commands[data_recv_control.lower()]
            response = self.CaptureCode_Admin(response_func)
        
        if response != None:
            self.Send_Admin(str(response), client_socket_control)
    



        






class AdminConnection(AdminControl):
    def __init__(self):
        super().__init__()
        self.failed_login_attempts = defaultdict(int)
        self.banned_ips_file = self.AdminPathSettings.checkpath("banned_ips.json")
        self.load_banned_ips()


    def load_banned_ips(self):
        try:
            with open(self.banned_ips_file, 'r') as f:
                content = f.read().strip()
                if content:
                    self.banned_ips = json.loads(content)
                else:
                    self.banned_ips = []
        except FileNotFoundError:
            self.banned_ips = []
        except json.decoder.JSONDecodeError as e:
            print(f"Error decoding JSON in {self.banned_ips_file}: {e}")
            self.banned_ips = []


    def save_banned_ips(self):
        with open(self.banned_ips_file, 'w') as f:
            json.dump(self.banned_ips, f)
            

    def StartAdminPanel(self):
        # Ensure the banned IPs file is available
        if not os.path.isfile(self.banned_ips_file):
            open(self.banned_ips_file, 'w').close()

        try:
            while True:
                self.AdminLog.print_and_log(f"\n{projet_name_admin} \033[36m[~]\033[0m Waiting for a connection...")

                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.AdminLog.print_and_log(f"{projet_name_admin} \033[36m[~]\033[0m Time: {current_time}")

                self.client_socket, self.client_address = self.AdminServerConnection.tcp_handler.accept()
                self.AdminLog.print_and_log(f"\n{projet_name_admin} \033[33m[+]\033[0m Accepted connection from {self.client_address}")

                self.authenticate_user(self.client_socket)

        except KeyboardInterrupt:
            self.Send_Admin(f"{projet_name_admin} \033[31m[!]\033[0m Server shutdown.", self.client_socket, "error")
            self.AdminServerConnection.tcp_handler.close()

        except Exception as e:
            ErrorFound = f"{projet_name_admin} \033[31m[!]\033[0m Error starting admin panel: {e}"
            self.Send_Admin(ErrorFound, self.client_socket, "error")


    def authenticate_user(self, connection):
        credentials = self.Recv_Admin(self.client_socket)
        username, password = credentials.split(',')

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.AdminLog.print_and_log(f"{projet_name_admin} \033[33m[+]\033[0m Time: {current_time}")

        # Check if IP is banned
        if self.client_address[0] in self.banned_ips:
            self.Send_Admin("{projet_name_admin} \033[31m[!]\033[0m Authentication failed. IP address is banned.", self.client_socket, "critical")
            self.AdminLog.print_and_log(f"\n{projet_name_admin} \033[31m[-]\033[0m IP address {self.client_address[0]} is banned.")
            self.client_socket.close()
            return

        if self.validate_user_credentials(username, password):
            self.AdminLog.print_and_log(f"\n{projet_name_admin} \033[34m[+]\033[0m User - {username} - has logged in successfully.")
            self.Send_Admin("\033[33m[+]\033[0m Authentication successful!", self.client_socket)

            # Reset failed login attempts
            if self.client_address[0] in self.failed_login_attempts:
                del self.failed_login_attempts[self.client_address[0]]

            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.AdminLog.print_and_log(f"{projet_name_admin} \033[34m[$]\033[0m Time: {current_time}")

            for logo in ListLogo:
                self.Send_Admin(logo, connection)
                break

            self.handle_client(connection, username)

        else:
            # Increase failed login attempts
            self.failed_login_attempts[self.client_address[0]] += 1
            
            if self.failed_login_attempts[self.client_address[0]] >= 3:
                self.banned_ips.append(self.client_address[0])
                self.save_banned_ips()

            self.AdminLog.print_and_log(f"\n{projet_name_admin} \033[31m[!]\033[0m User - {username} - could not log in successfully.")
            self.Send_Admin("\033[31m[!]\033[0m Authentication failed. Closing connection.", self.client_socket, "critical")
            self.client_socket.close()

            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.AdminLog.print_and_log(f"{projet_name_admin} \033[31m[$]\033[0m Time: {current_time}")



    def validate_user_credentials(self, username, password):
        return username.lower() == self.username.lower() and password == self.password 


    def handle_client(self, client_socket, usernameConn):
        try:
            while True:
                data_recv = self.Recv_Admin(client_socket)
                if not data_recv:
                    break
                
                if data_recv.lower() == "exit":
                    self.AdminLog.print_and_log(f"\n{projet_name_admin} \033[31m[-]\033[0m User - {usernameConn} - has logged out successfully.")
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.AdminLog.print_and_log(f"{projet_name_admin} \033[31m[$]\033[0m Time: {current_time}")
                    self.Send_Admin(f"{projet_name_admin} \033[31m[!]\033[0m Warning exit means that you will be disconnected from the server", client_socket)
                    self.Send_Admin(f"{projet_name_admin} \033[31m[!]\033[0m You can shut down the server from the dashboard page only ", client_socket)
                    self.Send_Admin("exit", client_socket, PureMsg="AdminInfo")
                    client_socket.close()
                        
                elif data_recv.lower() in self.main_commands:
                    self.Control_Admin(data_recv, client_socket)
                        
                elif data_recv.isdigit() and 1 <= int(data_recv) <= len(self.AdminModes.available_modes):
                    self.Main_Admin(client_socket, self.AdminModes.select_mode, self.AdminModes.available_modes[int(data_recv) - 1]) 

                else:
                    self.Send_Admin(f"{projet_name_admin} \033[31m[!]\033[0m Invalid input: {data_recv}. Type 'list' to see available modes.", client_socket, "error")
                
        except Exception as e:
            ErrorFound = f"{projet_name_admin} \033[31m[!]\033[0m Error handling client: {e}"
            self.Send_Admin(ErrorFound, client_socket, "error")
            client_socket.close()




        







if __name__ == "__main__":
    
    AdminConnection().StartAdminPanel()