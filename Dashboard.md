# All-in-One Server - Dashboard
The All-in-One Server Dashboard is a command-line interface for managing and running server scripts. It provides a user-friendly interface to list, select, and run scripts with custom parameters and terminals. The dashboard also includes a real-time file system monitor and system information sensor.

## Features
List, select, and run server scripts
Customize terminal and parameters for each script
Real-time file system monitor
System information sensor
Emergency mode for handling critical situations
Getting Started
Clone the repository:


`
    git clone https://github.com/kassam-99/ALL-in-One-Server-Framework.git
`
Navigate to the project root directory - `Admin`:


cd All_in_One_Server
Run the dashboard:


python Dashboard.py
## Usage
The dashboard provides various options to manage and run server scripts. Here are some of the available commands:

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

## Real-Time File System Monitor
The real-time file system monitor keeps track of changes in the project directory. It can be useful for detecting suspicious monitoring script execution.

## System Information Sensor
The system information sensor displays system-specific information, such as the operating system and available terminals.

## Emergency Mode
In case of a critical situation, the dashboard can enter emergency mode, which modifies the system's PATH environment variable to ensure safe execution of scripts.

## Dependencies
Python 3.x
multiprocessing
os
signal
subprocess
sys
StringIO
ctypes (for Windows)
Engine, Modes, Log, Settings, Emergency, SysMonitor, and Commands modules (included in the project)
Contributing
Contributions are welcome! Please submit a pull request or open an issue for any bugs, improvements, or features you'd like to add.

