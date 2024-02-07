# All-in-One Server Framework 

The All-in-One Server Framework is a versatile and comprehensive solution designed for managing, controlling, and monitoring various server-related operations. It supports multiple types of connections, including TCP, UDP, Websockets, HTTP, HTTPS, SSH, and FTP.

# Core
The framework consists of several modules, each serving a specific purpose, providing functionalities such as directory management, process management, emergency handling, mode management, logging, server settings, and system monitoring.

## Directory Structure

DirectoryManager.py:
    Manages paths and directories.
    Handles directory listing, content retrieval, log directory management, and process management.

Emergency.py:
    Provides emergency handling functionalities.
    Manages paths and processes in emergency situations.
    Includes classes for handling paths and processes during emergencies.

Modes.py:
    Manages different operation modes.
    Lists and selects available modes.
    Extracts folders and files from input strings.

Log.py:
    Handles logging functionalities.
    Logs messages at different levels.
    Configures and initializes the logging engine.

settings.py:
    Defines classes for managing server settings.
    Includes settings for various server types such as TCP, UDP, Websockets, HTTP, HTTPS, SSH, and FTP.

SysMonitor.py:
    Monitors system-related information in real-time.
    Checks CPU usage, system uptime, sensors, battery, fans, brightness, memory, disk, network, OS info, logged users, and GPU.

Engine.py:
    Manages script execution and monitoring.
    Controls running scripts, including starting, stopping, renaming, and monitoring.

# Getting Started

Clone the repository.
    
    git clone https://github.com/kassam-99/ALL-in-One-Server-Framework.git


Install dependencies

    pip install requirements.txt


# Usage Examples

Launch a server:

    cd Admin

    python Dashboard.py

Or to connect to a server with administrative privileges:

    python Admin.py

`Make sure to read AdminPanel.md and Dashaboard.md before starting a server`
Managing Paths:
    Use Paths_Manager in DirectoryManager.py to add, remove, and reset paths.
    Utilize EmergencyPathManager in Emergency.py for emergency path management.

Real-time System Monitoring:
    Use Sensor in SysMonitor.py to check CPU, memory, disk, network, and other system-related information in real-time.
    Monitor directories and logs with RealTime_Dir and RealTime_Process in SysMonitor.py.

Server Settings:
    Customize server settings for different types (TCP, UDP, Websockets, HTTP, HTTPS, SSH, FTP) using Server_Settings in settings.py.

Script Management:
    Use ScriptEngine in Engine.py to start, stop, rename, and monitor running scripts.

# Contributing

Feel free to contribute by opening issues, submitting pull requests, or providing feedback. We welcome any improvements or additional features that enhance the functionality and usability of the framework.
