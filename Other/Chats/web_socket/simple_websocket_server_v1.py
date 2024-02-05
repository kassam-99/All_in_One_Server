import asyncio
import time
import websockets
from datetime import datetime
import os
import sys

project_root = os.path.abspath(__file__)
index = project_root.find("All_in_One_Server")
if index != -1:
    core_dir = project_root[:index+18]+"Core"
sys.path.append(core_dir)

from Settings import Websockets_Server
 

import asyncio
import websockets

clients = set()  # Set to store connected clients

async def handle_client(websocket):
    clients.add(websocket)
    try:
        while True:
            message = await websocket.recv()
            for client in clients:
                if client != websocket:
                    await client.send(message)
    except websockets.ConnectionClosed:
        clients.remove(websocket)



WS_server = Websockets_Server()

WS_server.Websocket_Handler = handle_client

WS_server.start_websockets_server()


