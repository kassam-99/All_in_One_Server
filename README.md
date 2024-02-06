# All-in-One Server Dashboard
The All-in-One Server Dashboard is a command-line interface for managing and running server scripts. It provides a user-friendly interface to list, select, and run scripts with custom parameters and terminals. The dashboard also includes a real-time file system monitor and system information sensor.

# Features
List, select, and run server scripts
Customize terminal and parameters for each script
Real-time file system monitor
System information sensor
Emergency mode for handling critical situations
Getting Started
Clone the repository:

Copy code
git clone https://github.com/kassam-99/All_in_One_Server.git
Navigate to the project root directory:

Copy code
cd All_in_One_Server
Run the dashboard:

Copy code
python Dashboard.py
# Usage
The dashboard provides various options to manage and run server scripts. Here are some of the available commands:

 - list: List available server scripts
 - rename <script_name> <new_name>: Rename a server script
 - stop <script_name>: Stop a running server script
 - stop_all: Stop all running server scripts
 - restart <script_name>: Restart a server script
 - map: Map a server script to a specific mode (for advanced users)
 - info: Display system information
 - show: Show running server scripts
 - help: Display available commands and usage
 - read: Display project banner

# Real-Time File System Monitor
The real-time file system monitor keeps track of changes in the project directory. It can be useful for detecting suspicious monitoring script execution.

# System Information Sensor
The system information sensor displays system-specific information, such as the operating system and available terminals.

# Emergency Mode
In case of a critical situation, the dashboard can enter emergency mode, which modifies the system's PATH environment variable to ensure safe execution of scripts.

# Dependencies
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

# License
This project is licensed under the MIT License - see the LICENSE.md file for details