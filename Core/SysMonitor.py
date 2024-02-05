# Libraries to handle I/O files, folders and Manage a system
import datetime
import time
import psutil
import GPUtil
import platform
import os
from plyer import notification

# Other:
from Log import Logs
from Settings import Path_Settings
from DirectoryManager import Paths_Manager, ManageLogDir








class Sensor:
    
        
    def __init__(self):
        self.LogSys = Logs()
        self.LogSys.LogEngine("SysMonitor - Sensor", "LogCore_SysMonitor")


    def CPU_Checker(self):
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            self.LogSys.print_and_log("[*] CPU Usage:", "debug")
            self.LogSys.print_and_log(f"    CPU Usage Percentage: {cpu_percent}%\n", "debug")
        except Exception as e:
            self.LogSys.print_and_log(f"[!] Error checking CPU usage: {e}", "error")

    def Uptime(self):
        try:
            uptime = round(time.time() - psutil.boot_time())
            self.LogSys.print_and_log(f"[*] System Uptime: {datetime.timedelta(seconds=uptime)}\n", "debug")
        except Exception as e:
            self.LogSys.print_and_log(f"[!] Error checking system uptime: {e}", "error")

    def Check_Sensors(self):
        try:
            self.Component_Temp = {}
            self.Battery = {}
            self.Fan = {}

            if hasattr(psutil, "sensors_temperatures"):
                self.Component_Temp = psutil.sensors_temperatures()

            if hasattr(psutil, "sensors_battery"):
                self.Battery = psutil.sensors_battery()

            if hasattr(psutil, "sensors_fans"):
                self.Fan = psutil.sensors_fans()
        except Exception as e:
            self.LogSys.print_and_log(f"[!] Error checking sensors: {e}", "error")


    def Component_Temp_Checker(self):
        try:
            for i, temp in enumerate(self.Component_Temp.keys()):
                self.LogSys.print_and_log(f"[*] Device No.({i+1}):  {temp}", "debug")
                if temp:
                    for check in self.Component_Temp[temp]:
                        self.LogSys.print_and_log(f"        {check.label or temp}    Current Temperature: {check.current}°C ", "debug")
            self.LogSys.print_and_log("\n", "debug")
        except Exception as e:
            self.LogSys.print_and_log(f"[!] Error checking component temperatures: {e}", "error")


    def Battery_Checker(self):
        self.LogSys.print_and_log("[*] Battery: ", "debug")
        
        if not hasattr(psutil, "sensors_battery"):
            self.LogSys.print_and_log("    Battery information not available on this system.", "debug")
            return

        if self.Battery.power_plugged is None:
            self.LogSys.print_and_log("        No battery Installed", "debug")
        else:
            if self.Battery.power_plugged:
                self.LogSys.print_and_log("        Power Plugged ", "debug")
                self.LogSys.print_and_log("        Status: %s" % ("charging" if self.Battery.percent < 100 else "fully charged"))
                self.LogSys.print_and_log("        Battery Percentage: %s" % round(self.Battery.percent, 2), "%")
                self.LogSys.print_and_log("        left: %s" % self.Battery.secsleft)

            else:
                self.LogSys.print_and_log("        Power Unplugged ", "debug")
                self.LogSys.print_and_log("        Status: Discharging", "debug")
                self.LogSys.print_and_log("        Battery Percentage: %s" % round(self.Battery.percent, 2))
                self.LogSys.print_and_log("        left: %s" % self.Battery.secsleft)


    def Fan_Checker(self):
        self.LogSys.print_and_log("\n[*] Fan: ", "debug")
        for fan in self.Fan:
            self.LogSys.print_and_log("        Fan speed: %s" % fan.label,  fan.current)


    def Brigthness_checker(self):
        brightness = "N/A"
        if platform.system() == "Linux":
            intel = "/sys/class/backlight/intel_backlight/brightness"
            amd = "/sys/class/backlight/amdgpu_bl0/brightness"
            
            if os.path.exists(intel):
                with open(intel, 'r') as f:
                    brightness = int(f.read()) / 1200
            elif os.path.exists(amd):
                with open(amd, 'r') as f:
                    brightness = int(f.read()) / 1200

        self.LogSys.print_and_log("\n[*] Brightness: %s" % brightness)


    def Memory_Checker(self):
        memory_info = psutil.virtual_memory()
        total_memory_gb = memory_info.total / (1024 ** 3)
        used_memory_gb = memory_info.used / (1024 ** 3)
        free_memory_gb = memory_info.available / (1024 ** 3)
    
        self.LogSys.print_and_log("\n[*] Memory Usage:", "debug")
        self.LogSys.print_and_log(f"    Total Memory: {total_memory_gb:.2f} GB", "debug")
        self.LogSys.print_and_log(f"    Used Memory: {used_memory_gb:.2f} GB", "debug")
        self.LogSys.print_and_log(f"    Free Memory: {free_memory_gb:.2f} GB", "debug")
        self.LogSys.print_and_log(f"    Memory Usage Percentage: {memory_info.percent}%\n", "debug")


    def Disk_Checker(self, directory='/'):
        disk_info = psutil.disk_usage(directory)
        total_disk_gb = disk_info.total / (1024 ** 3)
        used_disk_gb = disk_info.used / (1024 ** 3)
        free_disk_gb = disk_info.free / (1024 ** 3)
    
        self.LogSys.print_and_log("\n[*] Disk Usage:", "debug")
        self.LogSys.print_and_log(f"    Total Disk Space: {total_disk_gb:.2f} GB", "debug")
        self.LogSys.print_and_log(f"    Used Disk Space: {used_disk_gb:.2f} GB", "debug")
        self.LogSys.print_and_log(f"    Free Disk Space: {free_disk_gb:.2f} GB", "debug")
        self.LogSys.print_and_log(f"    Disk Usage Percentage: {disk_info.percent}%\n", "debug")


    def Network_Checker(self):
        network_info = psutil.net_io_counters()
        self.LogSys.print_and_log("\n[*] Network Usage:", "debug")
        self.LogSys.print_and_log(f"    Bytes Sent: {network_info.bytes_sent}", "debug")
        self.LogSys.print_and_log(f"    Bytes Received: {network_info.bytes_recv}", "debug")
        self.LogSys.print_and_log(f"    Packets Sent: {network_info.packets_sent}", "debug")
        self.LogSys.print_and_log(f"    Packets Received: {network_info.packets_recv}\n", "debug")


    def OS_Info(self):
        self.LogSys.print_and_log("\n[*] Operating System Information:", "debug")
        self.LogSys.print_and_log(f"    System: {platform.system()}", "debug")
        self.LogSys.print_and_log(f"    Release: {platform.release()}", "debug")
        self.LogSys.print_and_log(f"    Version: {platform.version()}\n", "debug")


    def Logged_Users(self):
        users = psutil.users()
        self.LogSys.print_and_log("[*] Logged-in Users:", "debug")
        for user in users:
            self.LogSys.print_and_log(f"    User: {user.name}, Terminal: {user.terminal}, Host: {user.host}, Started: {datetime.datetime.fromtimestamp(user.started)}", "debug")


    def GPU_Checker(self):
        try:
            if platform.system() == "Windows":
                gpus = GPUtil.getGPUs()
                self.LogSys.print_and_log("\n[*] GPU Usage:", "debug")
                for i, gpu in enumerate(gpus):
                    self.LogSys.print_and_log(f"    GPU {i + 1} - Utilization: {gpu.load * 100}%", "debug")
                    self.LogSys.print_and_log(f"    GPU {i + 1} - Memory Usage: {gpu.memoryUsed} MB / {gpu.memoryTotal} MB", "debug")
            else:
                self.LogSys.print_and_log("\n[*] GPU Usage: Not available on this system.", "debug")
        except Exception as e:
            self.LogSys.print_and_log(f"[!] Error accessing GPU information: {e}", "debug")
            
            
    def Start_Sensor(self):
        self.Uptime()
        self.CPU_Checker()
        self.Check_Sensors()
        self.Component_Temp_Checker()
        self.Battery_Checker()
        self.Fan_Checker()
        self.Brigthness_checker()
        self.Memory_Checker()
        self.Disk_Checker()
        self.Network_Checker()
        self.OS_Info()
        self.Logged_Users()
        self.GPU_Checker()












class RealTime_Dir:
    
    
    def __init__(self):
        # Assuming Logs class and Path_Settings class are defined elsewhere
        self.LogSys = Logs()
        self.LogSys.LogEngine("SysMonitor - RealTime_Dir", "LogCore_SysMonitor")
        self.monitorFile = Path_Settings()
        self.MainPath = self.monitorFile.checkpath("All_in_One_ServerPath")
        self.LogPath = self.monitorFile.checkpath("All_in_One_ServerLogs")
        self.snapshot = {}
        self.snapshot_log = {}
        self.monitorPath = Paths_Manager()
        self.monitorLog = ManageLogDir()


    def take_snapshot(self):

        try:
            self.LogSys.LogsMessages("[+] Taking a snapshot")
            self.snapshot.clear()
            for root, dirs, files in os.walk(self.MainPath):          
                for folder in dirs:
                    folder_path = os.path.join(root, folder)
                    relative_path = os.path.relpath(folder_path, self.MainPath)
                    self.snapshot[relative_path] = os.path.getmtime(folder_path)
    
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, self.MainPath)
                    if relative_path == 'Logs/SysMonitor.log' or relative_path == 'Logs\\SysMonitor.log':
                        continue 
                    self.snapshot[relative_path] = os.path.getmtime(file_path)
        
        except Exception as e:
            self.LogSys.print_and_log(f"[!] Error taking snapshot: {e}", "error")
 
 
    def monitor_changes(self):
        try:
            current_state = {}
    
            for root, dirs, files in os.walk(self.MainPath):
                    
                for folder in dirs:
                    folder_path = os.path.join(root, folder)
                    relative_path = os.path.relpath(folder_path, self.MainPath)
                    current_state[relative_path] = os.path.getmtime(folder_path)
    
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, self.MainPath)
                    if relative_path == 'Logs/SysMonitor.log' or relative_path == 'Logs\\SysMonitor.log':
                        continue 
                    current_state[relative_path] = os.path.getmtime(file_path)
    
            added_items = set(current_state.keys()) - set(self.snapshot.keys())
            removed_items = set(self.snapshot.keys()) - set(current_state.keys())
            modified_items = {item for item in set(self.snapshot.keys()) & set(current_state.keys()) if (self.snapshot[item] != current_state[item])} 
    
            if added_items or removed_items or modified_items:
                self.alert_user(added_items, removed_items, modified_items)
    
            self.snapshot = current_state
        except Exception as e:
            self.LogSys.print_and_log(f"[!] Error monitoring changes: {e}", "error")


    def alert_user(self, added_items, removed_items, modified_items):
        self.LogSys.LogsMessages("Change detected:", "debug")
        if added_items:
            self.LogSys.LogsMessages(f"[#] Added items: {added_items}", "debug")
            file_path = added_items.pop()
            SecFile = os.path.split(file_path)
            self.Take_Action(add=True, Folder=SecFile[0], File=SecFile[-1])

        if removed_items:
            self.LogSys.LogsMessages(f"[#] Removed items: {removed_items}", "debug")
            file_path = removed_items.pop()
            SecFile = os.path.split(file_path)
            self.Take_Action(remove=True, Folder=SecFile[0], File=SecFile[-1])

        if modified_items:
            self.LogSys.LogsMessages(f"[#] Modified items: {modified_items}", "debug")
            file_path = modified_items.pop()
            SecFile = os.path.split(file_path)

        self.LogSys.LogsMessages("\n", "debug")


    def Take_Action(self, add=False, remove=False, modified=False, Folder=None, File=None):
        if add:
            self.monitorPath.SectionPath()
            self.monitorPath.GeneralPaths()
            self.monitorLog.MainLog()
        
        elif remove:
            if Folder == "Logs":
                self.monitorLog.MainLog()
            else:
                self.monitorPath.remove_path(section=Folder, pathname=File)
                self.monitorPath.Reset_Paths()
                self.monitorPath.SectionPath()
        
        elif modified:
            self.monitorPath.GeneralPaths()
            self.monitorPath.Reset_Paths()


    def Start_Monitor(self):
        self.take_snapshot()
        while True:
            time.sleep(1)
            self.monitor_changes()











class RealTime_Process:
    def __init__(self):
        self.LogSys = Logs()
        self.LogSys.LogEngine("SysMonitor - RealTime_Process", "LogCore_SysMonitor")
        self.monitorFile = Path_Settings()
        self.MainPath = self.monitorFile.checkpath("All_in_One_ServerPath")
    
    def ProcessAlert(self, script_name_alert):
        notification_title = "Information"
        notification_message = f"Script started: {script_name_alert}"
        self.send_notification(notification_title, notification_message)


    def send_notification(self, title, message):
        if platform.system() == "Darwin":  # macOS
            notification.notify(
                title=title,
                subtitle="Process Monitor",  # macOS specific: Set subtitle
                message=message,
                timeout=10,
            )
        elif platform.system() == "Linux":
            notification.notify(
                title=title,
                message=message,
                timeout=10,
            )
        elif platform.system() == "Windows":
            notification.notify(
                title=title,
                message=message,
                app_name="ProcessMonitor",
                timeout=10,
                ticker="Process Alert",
                toast=False,
            )
        else:
            self.LogSys.LogsMessages("Unsupported operating system for notifications.")

        notification_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.LogSys.LogsMessages(f"Notification sent at: {notification_timestamp}")




if __name__ == "__main__":
    #Sensor().Start_Sensor()
    RealTime_Dir().Start_Monitor()
    #RealTime_Process().ProcessInfo("simple_socketTCP_server.py", 34113)
    
    


