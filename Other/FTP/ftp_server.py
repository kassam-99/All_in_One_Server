import os
import sys

project_root = os.path.abspath(__file__)
index = project_root.find("All_in_One_Server")
if index != -1:
    core_dir = project_root[:index+18]+"Core"
sys.path.append(core_dir)

from Settings import FTP_Server

pathx = "/media/zedx/WORKSPACE/Cybersecurity_workspace/Programming/Python/Projects/All_in_One_Server"


server = FTP_Server()



server.ftp_username = "test"
server.ftp_password = "test"

server.ftp_user_path = pathx
server.ftp_user_permission = 'elradfmwMT'


server.ftp_anonymous_path = pathx
server.ftp_anonymous_permission = 'elradfmwMT'

server.dtp_handler.write_limit = 30720 # 30 Kb/sec (30 * 1024)
server.dtp_handler.read_limit = 30720 # 30 Kb/sec (30 * 1024)

server.start_ftp_server()