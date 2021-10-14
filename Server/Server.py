import asyncio
import websockets
import json
import time
import threading


CONNECTIONS = {}
BOT = None

PINGS = {}

async def main_loop(websocket, path):
    global BOT
    try:
        #print(websocket.remote_address)
        username = await websocket.recv()
        print(username,"is trying to connect")
        await websocket.send(json.dumps({"username_valid":True}))
        password = await websocket.recv()
        print(password)
        
        if(username == "ErisBot"):
            BOT = websocket
            #asyncio.ensure_future(bot_loop(websocket),loop=asyncio.get_event_loop())
            #asyncio.create_task(bot_loop(websocket))
            await bot_loop(websocket)
        else:
            CONNECTIONS[websocket] = username
            print(CONNECTIONS)
            #asyncio.ensure_future(client_loop(websocket),loop=asyncio.get_event_loop())
            #asyncio.create_task(client_loop(websocket))
            await client_loop(websocket)
        
    finally:
        del CONNECTIONS[websocket]
        print("dc")
        print(CONNECTIONS)

async def client_loop(websocket):
    global PINGS
    async for message in websocket:
        data = json.loads(message)
        if(data["command"] == "ping_response"):
            print("TASK_CLI:",asyncio.current_task())
            print("Ponged by",CONNECTIONS[websocket])
            #print(PINGS)
            PINGS[CONNECTIONS[websocket]] = time.time() - PINGS[CONNECTIONS[websocket]]
            print("PINGS after:",PINGS)
            if(max(PINGS.values()) < 1000000000):
                await BOT.send(json.dumps(PINGS))
        elif(data["command"] == "commit_response"):
            await BOT.send(json.dumps({"commit_success":data["command_success"]}))
        elif(data["command"] == "update_response"):
            await BOT.send(json.dumps({"update_success":data["command_success"]}))
        elif(data["command"] == "checkout_response"):
            await BOT.send(json.dumps({"checkout_success":data["command_success"]}))

##    while True:
##        x = await websocket.ping()

async def bot_loop(websocket):
    global PINGS
    #print(dir(websocket))
    async for message in websocket:
        data = json.loads(message)
        if(data["command"] == "ping"):
            print("TASK_BOT:",asyncio.current_task())
            await websocket.send("True")
            
            PINGS = {}

            
            for conn in CONNECTIONS:
                print("Pinging",CONNECTIONS[conn])
                PINGS[CONNECTIONS[conn]] = time.time()
                await conn.send(json.dumps({"command":"ping"}))
            pings = {}
            #asyncio.sleep(4)
        elif(data["command"] == "commit"):
            print("Recieved commit command")
            client = None
            for conn in CONNECTIONS:
                if(CONNECTIONS[conn] == data["target"]):
                    client = conn
                    break
            if(client == None):
                print("Nothing")
                return #handle this later
            await client.send(json.dumps(data))
        elif(data["command"] == "update"):
            print("Received update comamnd")
            client = None
            for conn in CONNECTIONS:
                if(CONNECTIONS[conn] == data["target"]):
                    client = conn
                    break
            if(client == None):
                print("Nothing")
                return #handle this later
            await client.send(json.dumps(data))
        elif(data["command"] == "checkout"):
            print("Received checkout comamnd")
            client = None
            for conn in CONNECTIONS:
                if(CONNECTIONS[conn] == data["target"]):
                    client = conn
                    break
            if(client == None):
                print("Nothing")
                return #handle this later
            await client.send(json.dumps(data))



async def main():
    async with websockets.serve(main_loop, "192.168.1.231", 6969):
        await asyncio.Future()

asyncio.run(main())
