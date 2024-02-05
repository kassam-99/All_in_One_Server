import threading
import os
import sys

# Get the project root directory (two levels up from the script)
project_root = os.path.abspath(__file__)
index = project_root.find("All_in_One_Server")
if index != -1:
    core_dir = project_root[:index+18]+"Core"
sys.path.append(core_dir)

from Settings import TCP_Server


def handle_rece_msg(server):
    while True:
        try:
            msg_rece = server.recv(4505)
            if msg_rece:
                print("[Client]: ", msg_rece.decode())  # Decode a message
            else:
                server.close()
                break
        except Exception as e:
            print(f'[!] Error handling message from server: {e}')
            server.close()
            break


def handle_sent_msg(server):
    while True:
        try:
            msg_send = input()
            if msg_send:
                server.send(msg_send.encode())  # Encode a message
            else:
                server.close()
                break
        except Exception as e:
            print(f'[!] Error handling message from server: {e}')
            server.close()
            break


def server_thread(client_socket):
    send = threading.Thread(target=handle_sent_msg, args=(client_socket,))
    rece = threading.Thread(target=handle_rece_msg, args=(client_socket,))
    send.start()
    rece.start()
    send.join()
    rece.join()



while True:
    server = TCP_Server()
    server.start_TCP_Server()

    client_socket, addr = server.tcp_handler.accept()

    print("[>] Accepted connection from: %s:%d" % (addr[0], addr[1]))
    print("[$] Chat started")
    
    try:
        server_thread(client_socket)

    except Exception as e:
        print(f"Error: {e}")
        server.close()
        break
