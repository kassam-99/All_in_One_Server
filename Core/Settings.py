# Libraries to handle I/O files, folders and Manage a system
import re
import os
import platform

# Libraries to setup and handle a connection settings
import socket
import asyncio
import subprocess
import websockets
from http.server import HTTPServer, SimpleHTTPRequestHandler
import ssl
import paramiko
from pyftpdlib.handlers import FTPHandler, ThrottledDTPHandler
from pyftpdlib.servers import FTPServer
from pyftpdlib.authorizers import DummyAuthorizer

# Other:
from Log import Logs
from Emergency import EmergencyPathManager





class Path_Settings:
    def __init__(self):
        self.Log = Logs()
        self.Log.LogEngine("Settings - Path_Settings", "LogCore_Settings")
        self.EXCLUDED_DIRS = ["Core", "Logs", "Admin"]  # Banned modes: To not be used in Mode.py
        self.EmergencyMode = False
        
        try:
            self.All_in_One_server_paths = __file__
            self.script_dir = os.path.dirname(self.All_in_One_server_paths)
            self.Pathsfile = os.path.join(self.script_dir, "Paths.txt")
            self.ProcessesFile = os.path.join(self.script_dir, "ProcessesLab.json")

        except FileNotFoundError as e:
            self.Log.LogsMessages(f"[!] Error: {e}", "CRITICAL")
            self.EmergencyMode = True
        except Exception as e:
            self.Log.LogsMessages(f"[!] Unexpected error: {e}", "CRITICAL")
            self.EmergencyMode = True
        finally:
            if self.EmergencyMode == True:
                self.EmergencyPaths()

        
    def checkpath(self, targetpath):
        checkpath_result = None
        with open(self.Pathsfile, 'r', encoding="utf-8") as readpath:
            for search in readpath.readlines():
                if search.startswith('#'):
                    if targetpath in search:
                        matches = re.findall(r'["\'](.*?)["\']', search)
                        for path in matches:
                            checkpath_result = path  # Update the variable with the found path
                            return checkpath_result  # Return the path immediately if found
        
        if checkpath_result is None:
            self.EmergencyPaths()
                        
    
    def EmergencyPaths(self):
        self.Log.LogsMessages("[!] Emergency Script is called", "CRITICAL")
        self.Log.LogsMessages("[!] Paths.txt file not found", "WARNING")
        EmergencyPathManager().StartEmergencyModePath()


    
        
        
    




class Server_Settings:
    
    DEFAULT_IP = "localhost"
    DEFAULT_PORT = 3000
    DEFAULT_ServerUsername = "admin"
    DEFAULT_ServerPassword = "admin"
        
    def __init__(self, server_main_ip=DEFAULT_IP, server_main_port=DEFAULT_PORT, ServerName=DEFAULT_ServerUsername, ServerPassword=DEFAULT_ServerPassword):
        """
        Initialize server settings.
        """
        self.Log = Logs()
        self.Log.LogEngine("Settings - Server_Settings", "LogCore_Settings")
        self.ServerName = ServerName
        self.ServerPassword = ServerPassword
        self.server_main_ip = server_main_ip
        self.server_main_port = server_main_port
        self.max_connections = None
        self.timeout = None
        self.malware_threads_max = None

    def set_max_connections(self, max_connections):
        """
        Set the maximum number of connections.
        """
        if not isinstance(max_connections, int) or max_connections < 0:
            self.Log.print_and_log("[!] max_connections must be a non-negative integer", "WARNING")
        self.max_connections = max_connections

    def set_timeout(self, timeout):
        """
        Set the timeout value.
        """
        if not isinstance(timeout, (int, float)) or timeout < 0:
            self.Log.print_and_log("[!] timeout must be a non-negative numeric value", "WARNING")
        self.timeout = timeout

    def set_malware_threads_max(self, malware_threads_max):
        """
        Set the maximum number of threads for handling malware.
        """
        if not isinstance(malware_threads_max, int) or malware_threads_max < 0:
            self.Log.print_and_log("[!] malware_threads_max must be a non-negative integer", "WARNING")
        self.malware_threads_max = malware_threads_max
        
        
    @staticmethod    
    def ConnectionPath():
        """
        import os
        import sys
        
        project_root = os.path.abspath(__file__)
        index = project_root.find("All_in_One_server_")
        if index != -1:
            core_dir = project_root[:index+6]+"Core"
        sys.path.append(core_dir)
        
        from Settings import *
        """
        pass
        
        
    @staticmethod
    def check_system():
        system_platform = platform.system().lower()
        platform_mapping = {
            'linux': 'Linux',
            'windows': 'Windows',
            'darwin': 'Mac',
            'aix': 'AIX',
            'freebsd': 'FreeBSD',
            'netbsd': 'NetBSD',
            'openbsd': 'OpenBSD',
            'sunos': 'Solaris',
            'cygwin': 'Cygwin',
            'msys': 'MSYS',
            'os2': 'OS/2',
            'riscos': 'RISC OS'
        }
        return platform_mapping.get(system_platform, 'Unknown')
    
    
    @staticmethod
    def get_available_terminals(system_type, list=False):
        
        if system_type == "Windows":
            terminals = ["cmd", "powershell"]
            command = "where"
        elif system_type == "Linux":
            terminals = ["terminator", "gnome-terminal", "konsole", "xfce4-terminal", "xterm"]
            command = "which"
        elif system_type == "Darwin":
            terminals = ["Terminal", "iTerm", "Alacritty"]
            command = "which"
        else:
            print("[!] Unsupported platform")
            return []
    
        # Filter out non-available terminals
        available_terminals = []
        for terminal in terminals:
            if subprocess.call([command, terminal], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
                available_terminals.append(terminal)
    
        if list:
            print("[*] Available terminals:")
            for i, terminal in enumerate(available_terminals):
                print(f"[{i + 1}] {terminal}")
    
        return available_terminals


    @staticmethod
    def check_for_port(p1, p2):
        for port in range(p1, p2+1):
            socket_port = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_port.settimeout(1)
            available_port = socket_port.connect_ex(('localhost', port))
            if available_port != 0:
                return port
            socket_port.close()
        raise Exception("[!] Couldn't find an open port")
    
    
    @staticmethod
    def start_server():
        print("Select the server type:")
        print("[1] Socket_tcp_Server")
        print("[2] UDP_Server")
        print("[3] Websockets_Server")
        print("[4] HTTP_Server")
        print("[5] HTTPS_Server")
        print("[6] SSH_Server")
        print("[7] FTP_Server")
        print("[8] Exit")

        try:
            choice = int(input("[>] Enter the number corresponding to the server type: "))

            if choice == 1:
                server = TCP_Server()
                server.start_TCP_Server()

            elif choice == 2:
                server = UDP_Server()
                server.start_udp_server()
                
            elif choice == 3:
                server = Websockets_Server()
                server.start_websockets_server()

            elif choice == 4:
                server = HTTP_Server()
                server.start_http_server()

            elif choice == 5:
                server = HTTPs_Server()
                server.start_https_server()

            elif choice == 6:
                server = ssh_Server()
                server.start_ssh_server()

            elif choice == 7:
                server = FTP_Server()
                server.start_ftp_server()

            elif choice == 8:
                print("Exiting the program.")
                return

            else:
                print("[!] Invalid choice. Please enter a valid number.")

        except ValueError:
            print("[!] Invalid input. Please enter a valid number.")


    def server_details(self, connection_type, server_ip, server_port):
        try:

            if len(server_ip) >= 1:
                lserver = f"[*] \033[34m{connection_type}\033[0m Server is \033[32mrunning!\033[0m, listening on, \033[33m{server_ip}:{server_port}\033[0m"
            else:
                server_ip = socket.gethostbyname(socket.gethostname())
                lserver = f"[*] \033[34m{connection_type}\033[0m Server is \033[32mrunning!\033[0m, listening on, \033[33m{server_ip}:{server_port}\033[0m"
                
            host_name = socket.gethostname()
            x = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            x.connect(('10.0.0.0', 0))
            server_ip = x.getsockname()[0]
                
            self.Log.print_and_log(f"{lserver}")
            self.Log.print_and_log(f"[-] Hostname: \033[31m{host_name}\033[0m")
            self.Log.print_and_log(f"[-] Platform: \033[31m{self.check_system()}\033[0m")
            self.Log.print_and_log(f"[-] IP: \033[33m{server_ip}\033[0m")
            self.Log.print_and_log(f"[-] Port: \033[33m{server_port}\033[0m")
            self.Log.print_and_log(f"[-] Connection type: \033[34m{connection_type}\033[0m")
            self.Log.print_and_log(f"[-] Share IP and port with the client")
            
        except Exception as e:
            self.Log.print_and_log(f"[!] Unable to get Hostname and IP: {e}", "CRITICAL")





class TCP_Server(Server_Settings):
    def __init__(self, tcp_server_ip=None, tcp_server_port=None):
        super().__init__()
        try:
            if tcp_server_ip is None:
                self.tcp_server_ip = "localhost"
            elif not isinstance(tcp_server_ip, str):
                self.Log.print_and_log("[!] tcp_server_ip must be a string", "CRITICAL")
            else:
                self.tcp_server_ip = tcp_server_ip

            if tcp_server_port is None:
                self.tcp_server_port = self.check_for_port(8000, 8099)
            elif not isinstance(tcp_server_port, int):
                self.Log.print_and_log("[!] tcp_server_port must be an integer", "CRITICAL")
            else:
                self.tcp_server_port = tcp_server_port

            self.tcp_handler = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_handler.bind((self.tcp_server_ip, self.tcp_server_port))
            self.tcp_handler.listen() # Number of Bad Connections to Allow before Refusing
            
        except ValueError as ve:
    
            self.Log.print_and_log(f"[!] Error: {ve}", "ERROR")
            
        except Exception as e:
            self.Log.print_and_log(f"[!] Error setting up server: {e}", "ERROR")
            raise
        """        
        # In order to accept connections you need to add TCP_Server variable
          to your code ex:
          server = TCP_Server()
          server.start_TCP_Server()
          client_socket, addr = server.tcp_handler.accept()
        """
    def start_TCP_Server(self):
        try:
            self.server_details("TCP", self.tcp_server_ip, self.tcp_server_port)
            
        except Exception as e:
            self.Log.print_and_log(f"[!] Error accepting connection: {e}", "ERROR")




class UDP_Server(Server_Settings):
    def __init__(self, udp_server_ip=None, udp_server_port=None):
        super().__init__()
        try:
            if udp_server_ip is None:
                self.udp_server_ip = "localhost"
            elif not isinstance(udp_server_ip, str):
                self.Log.print_and_log("[!] udp_server_ip must be a string", "CRITICAL")
            else:
                self.udp_server_ip = udp_server_ip

            if udp_server_port is None:
                self.udp_server_port = self.check_for_port(8100, 8199)
            elif not isinstance(udp_server_port, int):
                self.Log.print_and_log("[!] udp_server_port must be an integer", "CRITICAL")
            else:
                self.udp_server_port = udp_server_port

            self.udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp_server.bind((self.udp_server_ip, self.udp_server_port))

        except Exception as e:
            self.Log.print_and_log(f"[!] Error setting up UDP server: {e}", "ERROR")
            raise
        """        
        # In order to accept connections you need to add UDP_Server variable
          to your code ex:
          server = UDP_Server()
          server.start_udp_server()
          data,addr = server.udp_server.recvfrom(1024))
          
          server.sendto(data.encode('utf-8'))
        """       

    def start_udp_server(self):
        try:
            self.server_details("UDP", self.udp_server_ip, self.udp_server_port)

        except Exception as e:
            self.Log.print_and_log(f"[!] Error in UDP server: {e}", "ERROR")
            self.Log.print_and_log(f"[!] Error stopping UDP server: {e}", "ERROR")
            

            
            
            
             
class Websockets_Server(Server_Settings):
    def __init__(self, Websocket_server_ip=None, Websocket_server_port=None):
        super().__init__()
        try:
            
            if Websocket_server_ip is None:
                self.Websocket_server_ip = "localhost"
            elif not isinstance(Websocket_server_ip, str):
                self.Log.print_and_log("[!] Websocket_server_ip must be a string", "CRITICAL")
            else:
                self.Websocket_server_ip = Websocket_server_ip

            if Websocket_server_port is None:
                self.Websocket_server_port = self.check_for_port(8200, 8299)
            elif not isinstance(Websocket_server_port, int):
                self.Log.print_and_log("[!] Websocket_server_port must be an integer", "CRITICAL")
            else:
                self.Websocket_server_port = Websocket_server_port
                
            self.Server_Websocket = f"ws://{self.Websocket_server_ip}:{self.Websocket_server_port}"
            self.Websocket_Handler = None 
            # self.Websocket_Handler: Main function to Run a server.
            # It must be assigned in a server script

        except Exception as e:
            self.Log.print_and_log(f"[!] Error setting up websockets server: {e}", "ERROR")
            raise
        """        
        # To run a Websocket server:
          def Main_handler():
                   ...
          WS_server = Websockets_Server()
          WS_server.Websocket_Handler = Main_handler => Main function
          WS_server.start_websockets_server()
        """
    def start_websockets_server(self):
        if self.Websocket_Handler is None:
            self.Log.print_and_log("[!] websocket_handler must be set before starting the server", "WARNING")
        
        self.server_details("Websockets", self.Websocket_server_ip, self.Websocket_server_port)
        try:
            async def main():
                async with websockets.serve(self.Websocket_Handler, self.Websocket_server_ip, self.Websocket_server_port):
                    await asyncio.Future()
    
            asyncio.run(main())
    
        except websockets.WebSocketException as e:
            self.Log.print_and_log(f"[!] WebSocket error: {e}", "ERROR")
        except OSError as e:
            self.Log.print_and_log(f"[!] OS error: {e}", "ERROR")
        except Exception as e:
            self.Log.print_and_log(f"[!] Error during websocket server startup: {e}", "ERROR")
    
        finally:
            self.Log.print_and_log("[!] Closing Websockets server", "CRITICAL")

            





class HTTP_Server(Server_Settings):
    def __init__(self, http_server_ip=None, http_server_port=None):
        super().__init__()
        
        try:
            if http_server_ip is None:
                self.http_server_ip = "localhost"
            elif not isinstance(http_server_ip, str):
                self.Log.print_and_log("[!] http_server_ip must be a string", "CRITICAL")
            else:
                self.http_server_ip = http_server_ip

            if http_server_port is None:
                self.http_server_port = self.check_for_port(8300, 8399)
            elif not isinstance(http_server_port, int):
                self.Log.print_and_log("[!] http_server_port must be an integer", "CRITICAL")
            else:
                self.http_server_port = http_server_port
                
            self.HTTP_STATUS_OK = 200
            self.HTTP_STATUS_BAD_REQUEST = 400
            self.HTTP_Handler = None
        
        except Exception as e:
            self.Log.print_and_log(f"[!] Error setting up HTTP connection: {e}", "ERROR")
            
        """
        HTTPServer_GroupChat = HTTP_Server()
        HTTPServer_GroupChat.HTTP_Handler = GroupChatHandler
        HTTP_STATUS = HTTPServer_GroupChat.HTTP_STATUS_OK
        
        HTTPServer_GroupChat.start_http_server()
        
        while True:  # Keep the server running continuously
        client_connection, client_address = HTTPServer_GroupChat.server.accept()
        client = GroupChatHandler(client_connection, client_address, HTTPServer_GroupChat)
        
        clients.append(client)
        threading.Thread(target=client.handle).start() 
        """
    
    def start_http_server(self):
        if self.HTTP_Handler is None:
            self.Log.print_and_log("[!] HTTP_Handler must be set before starting the server", "WARNING")
            return  # Don't proceed if the handler is not set
        self.server_details("HTTP", self.http_server_ip, self.http_server_port)
        
        try:
            Run_server = HTTPServer((self.http_server_ip, self.http_server_port), self.HTTP_Handler)
            Run_server.serve_forever()
            
        except Exception as e:
            self.Log.print_and_log(f"[!] Error accepting HTTP connection: {e}", "ERROR")
            Run_server.server_close()

        
        


class HTTPs_Server(Server_Settings):
    def __init__(self, https_server_ip=None, https_server_port=None):
        super().__init__()
        try:
            if https_server_ip is None:
                self.https_server_ip = "localhost"
            elif not isinstance(https_server_ip, str):
                self.Log.print_and_log("[!] https_server_ip must be a string", "CRITICAL")
            else:
                self.https_server_ip = https_server_ip

            if https_server_port is None:
                self.https_server_port = self.check_for_port(8400, 8499)
            elif not isinstance(https_server_port, int):
                self.Log.print_and_log("[!] https_server_port must be an integer", "CRITICAL")
            else:
                self.https_server_port = https_server_port
            # Provide the path to your SSL certificate and key files
            self.certfile = None
            self.keyfile = None

        except Exception as e:
            self.Log.print_and_log(f"[!] Error initializing HTTPS server: {e}", "ERROR")


    def start_https_server(self):
        self.server_details("HTTPS", self.https_server_ip, self.https_server_port)
        try:

            httpd = HTTPServer((self.https_server_ip, self.https_server_port), SimpleHTTPRequestHandler)
            httpd.socket = ssl.wrap_socket(httpd.socket, certfile=self.certfile, keyfile=self.keyfile, server_side=True)
            httpd.serve_forever()

        except Exception as e:
            self.Log.print_and_log(f"[!] Error starting HTTPS server: {e}", "ERROR")
            
            
            


class ssh_Server(Server_Settings):
    def __init__(self, ssh_server_ip=None, ssh_server_port=None):
        super().__init__()
        try:
            if ssh_server_ip is None:
                self.ssh_server_ip = "127.0.0.1"
            elif not isinstance(ssh_server_ip, str):
                self.Log.print_and_log("[!] ssh_server_ip must be a string", "CRITICAL")
            else:
                self.ssh_server_ip = ssh_server_ip

            if ssh_server_port is None:
                self.ssh_server_port = self.check_for_port(8500, 8599)
            elif not isinstance(ssh_server_port, int):
                self.Log.print_and_log("[!] ssh_server_port must be an integer", "CRITICAL")
            else:
                self.ssh_server_port = ssh_server_port
                
            self.KEYNAME = None
            self.ssh_server_USERNAME = None
            self.ssh_server_PASSWORD = None
            self.ssh_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.ssh_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.ssh_server_socket.bind((self.ssh_server_ip, self.ssh_server_port))
            self.ssh_server_socket.listen(100)

        except Exception as e:
            self.Log.print_and_log(f"[!] Error initializing SSH server: {e}", "ERROR")

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        if (username == self.ssh_server_USERNAME) and (password == self.ssh_server_PASSWORD):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def start_ssh_server(self):
        self.server_details("SSH", self.ssh_server_ip, self.ssh_server_port)
            
        try:
            client, data = self.ssh_server_socket.accept()
            ssh_server_manager = paramiko.Transport(client)
            ssh_server_manager.load_server_moduli()
            
            if self.KEYNAME == None:
                ssh_server_manager.add_server_key(paramiko.RSAKey.generate(2048))
            else:
                host_key = paramiko.RSAKey(filename=self.KEYNAME)
                ssh_server_manager.add_server_key(host_key)
            
            server_interface = paramiko.ServerInterface()
            server_interface.check_channel_request = self.check_channel_request
            server_interface.check_auth_password = self.check_auth_password
        
            ssh_server_manager.start_server(server=server_interface)
            self.ssh_server_handler = ssh_server_manager.accept(20)

        except Exception as e:
            self.Log.print_and_log(f"[!] Error starting SSH server: {e}", "ERROR")
            self.ssh_server_socket.close()
            
            
            
            
            
class FTP_Server(Server_Settings):
    def __init__(self, ftp_server_ip=None, ftp_server_port=None):
        super().__init__()
        try:
            if ftp_server_ip is None:
                self.ftp_server_ip = "localhost"
            elif not isinstance(ftp_server_ip, str):
                self.Log.print_and_log("[!] ftp_server_ip must be a string", "CRITICAL")
            else:
                self.ftp_server_ip = ftp_server_ip

            if ftp_server_port is None:
                self.ftp_server_port = self.check_for_port(8600, 8699)
            elif not isinstance(ftp_server_port, int):
                self.Log.print_and_log("[!] ftp_server_port must be an integer", "CRITICAL")
            else:
                self.ftp_server_port = ftp_server_port
            
            self.ftp_username = None
            self.ftp_password = None
            
            self.ftp_user_path = None
            self.ftp_user_permission = None
            
            self.ftp_anonymous_path = None
            self.ftp_anonymous_permission= None
            
            self.ftp_address = ('localhost', 2100)
                    
            self.ftp_handler = FTPHandler
            self.ftp_authorizer = DummyAuthorizer()
            self.dtp_handler = ThrottledDTPHandler
            
            self.dtp_handler.read_limit = None # 30 Kb/sec (30 * 1024)
            self.dtp_handler.write_limit = None # 30 Kb/sec (30 * 1024)
            
            
        except Exception as e:
            self.Log.print_and_log(f"[!] Error setting up FTP connection: {e}", "ERROR")
    


    def start_ftp_server(self):
        try:
            
            self.ftp_authorizer.add_user(self.ftp_username, self.ftp_password, self.ftp_user_path, perm=self.ftp_user_permission)
            
            self.ftp_authorizer.add_anonymous(self.ftp_anonymous_path, perm=self.ftp_anonymous_permission)
            
            self.ftp_handler.authorizer = self.ftp_authorizer
            
            self.server_ftp = FTPServer(self.ftp_address, self.ftp_handler)
        
            self.server_details("FTP", self.ftp_server_ip, self.ftp_server_port)
            
            self.server_ftp.serve_forever()

        except Exception as e:
            self.Log.print_and_log(f"[!] Error starting FTP server: {e}", "ERROR")






if __name__ == "__main__":
    #PathSettings  = Path_Settings()
    #print(PathSettings.checkpath("All_in_One_server_Core"))
    #print(PathSettings.CheckMainPath())
    server = Server_Settings()
    #server.start_server()
    server.get_available_terminals("Windows", list=True)
    
    
