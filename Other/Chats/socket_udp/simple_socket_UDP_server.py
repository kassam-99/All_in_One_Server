import threading
import os
import sys
import queue

# Get the project root directory (two levels up from the script)
project_root = os.path.abspath(__file__)
index = project_root.find("All_in_One_Server")
if index != -1:
    core_dir = project_root[:index+18]+"Core"
sys.path.append(core_dir)

from Settings import UDP_Server


server = UDP_Server()
server.start_udp_server()


def RecvData(sock,recvPackets):
    while True:
        data,addr = server.udp_server.recvfrom(1024)
        print(data,addr)
        recvPackets.put((data,addr))

def RunServer():
    clients = set()
    recvPackets = queue.Queue()


    threading.Thread(target=RecvData,args=(server.udp_server,recvPackets)).start()

    while True:
        while not recvPackets.empty():
            data,addr = recvPackets.get()
            print(addr)
            if addr not in clients:
                clients.add(addr)
                continue
            
            clients.add(addr)
            data = data.decode('utf-8')
            
            if data.endswith('qqq'):
                clients.remove(addr)
                continue
            
            print(str(addr)+data)
            for c in clients:
                if c!=addr:
                    server.udp_server.sendto(data.encode('utf-8'),c)



if __name__ == "__main__":
    RunServer()