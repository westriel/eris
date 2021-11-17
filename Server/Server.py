import asyncio
import websockets
import json
import time
import threading

from Database import *

db = Database()

#u_n = db.GetUsernameFromDiscordID(344132856685002764)
#print(u_n)

CONNECTIONS = {}
BOT = None

PINGS = {}



async def main_loop(websocket, path):
    global BOT
    try:
        #print(websocket.remote_address)
        username = await websocket.recv()
        print(username,"is trying to connect")
        await websocket.send(json.dumps({"connected":True}))
        password = await websocket.recv()
        print(username,password)
        valid = db.CheckUsernameAndPassword(username,password)
        print("IS Valid?",valid)
        await websocket.send(json.dumps({"login_success":valid}))
        if(not valid):
            await websocket.close()
            return
        
        
        if(username == "ErisBot"):
            BOT = websocket
            await bot_loop(websocket)
        else:
            CONNECTIONS[websocket] = username
            print(CONNECTIONS)
            await client_loop(websocket)
        
    except:
        print("dc from",CONNECTIONS[websocket])
        del CONNECTIONS[websocket]
        
        print(CONNECTIONS)

async def client_loop(websocket):
    global PINGS
    async for message in websocket:
        data = json.loads(message)
        print("Got message: ",data)
        # Responses
        if(data["command"] == "ping_response"):
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

        # Triggers
        elif(data["command"] == "update_notifications"):
            print(data)
            status = db.UpdateUserRepoSettings(CONNECTIONS[websocket],"https://24.210.238.51:8443/svn/ErisTesting/",data["settings"])
            await websocket.send(json.dumps({"update_notifications_status":status}))

async def bot_loop(websocket):
    global PINGS
    #print(dir(websocket))
    async for message in websocket:
        data = json.loads(message)
        data["target"] = db.GetUsernameFromDiscordID(data["id"])
        if(data["command"] == "ping"):
            await websocket.send("True")
            
            PINGS = {}

            
            for conn in CONNECTIONS:
                print("Pinging",CONNECTIONS[conn])
                PINGS[CONNECTIONS[conn]] = time.time()
                await conn.send(json.dumps({"command":"ping"}))
            pings = {}

        elif(data["command"] == "switch"):
            print("Recieved switch command")
            if(db.CheckIfRepoExists(data["repo"])):
                if(db.CheckIfUserHasRepoAccess(data["target"],data["repo"])):
                    status = db.SetUserCurrentRepo(data["target"],data["repo"])
                    await websocket.send(json.dumps({"success":status}))
                else:
                    await websocket.send(json.dumps({"success":False,"reason":"You do not have access to this repo"}))
            else:
                await websocket.send(json.dumps({"success":False,"reason":"That repo does not exist within our system"}))

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
            repo = db.GetUserCurrentRepo(data["target"])
            if(repo == None):
                await websocket.send(json.dumps({"success":False,"reason":"You do not have a repo selected"}))
                continue
            data["repo"] = repo
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
            repo = db.GetUserCurrentRepo(data["target"])
            if(repo == None):
                await websocket.send(json.dumps({"success":False,"reason":"You do not have a repo selected"}))
                continue
            data["repo"] = repo
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
            repo = db.GetUserCurrentRepo(data["target"])
            if(repo == None):
                await websocket.send(json.dumps({"success":False,"reason":"You do not have a repo selected"}))
                continue
            data["repo"] = repo
            await client.send(json.dumps(data))



async def main():
    async with websockets.serve(main_loop, "192.168.1.231", 6969):
        await asyncio.Future()

asyncio.run(main())
