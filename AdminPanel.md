# All-in-One Server - Admin Panel
This project is a part of the All-in-One Server, which includes various functionalities such as file management, terminal access, and more. The Admin Panel is a separate component that allows administrators to manage and control the server remotely.

## Features
Authenticate users with a username and password
Display server information and available modes
Start, stop, restart, and rename server scripts
Manage banned IP addresses
Monitor system information

## Requirements
Python 3.x
Required Python libraries: socket, json, datetime, collections, ctypes (for Windows)
The Engine, Modes, Log, Settings, SysMonitor, and Commands modules from the All-in-One Server Core

## Usage
Ensure the required libraries and modules are installed and available.
Update the Server_Settings and Path_Settings with the appropriate settings for your environment.
Run the script using Python: python AdminPanel.py or just run Dashboard.py
Connect to the admin panel using a terminal or command prompt and enter the provided IP address and port number through `Admin.py script`.

Authenticate with the correct username and password.

Defalut username and password:
 - username = `admin`
 - password = `admin`



- `Note`: you can change a username, password, listening IP and port from `All-in-One Server/Core/Settings.py`


    class Server_Settings:    
        DEFAULT_IP = "localhost"
        DEFAULT_PORT = 3000
        DEFAULT_ServerUsername = "admin"
        DEFAULT_ServerPassword = "admin"



Use the available commands to manage and control the server.

## Commands
 - `list`: Display available modes
 - `rename` <old_name> <new_name>: Rename a running script
 - `stop` <name>: Stop a running script
 - `stop_all`: Stop all running scripts
 - `restart` <name>: Restart a running script
 - `map`: Display available modes and allow selecting a mode
 - `info`: Display system information
 - `show`: Display running scripts
 - `help`: Display available commands and usage
 - `read`: Display the server banner
 - `exit`: Log out and close the connection

## Admin Connection Class
The AdminConnection class is responsible for handling client connections, authenticating users, and managing the server.

### Methods
load_banned_ips(): Load banned IP addresses from a JSON file.
save_banned_ips(): Save banned IP addresses to a JSON file.
StartAdminPanel(): Start the admin panel and wait for client connections.
authenticate_user(connection): Authenticate the user with the provided credentials.
validate_user_credentials(username, password): Validate the user's credentials.
handle_client(client_socket, usernameConn): Handle the client's requests and commands.

## AdminControl Class
The AdminControl class is responsible for processing client commands and managing the server.

### Methods
Send_Admin(msg, conn, sendlog="info", PureMsg=None): Send a message to the client.
Recv_Admin(conn): Receive a message from the client.
CaptureCode_Admin(func, *args, **kwargs): Capture the output of a function.
Main_Admin(func, *args, **kwargs): Process a function's output and allow the user to select an option.
Control_Admin(data_recv_control, client_socket_control): Process client commands and execute the appropriate function.