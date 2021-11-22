import asyncio
import websockets

import json
import time

from Database import *

COMMAND_QUEUE = []
CONNECTIONS = {}

BOT_ID = "888218725810049055"

db = Database()

async def handle_comms():
    while(True):
        if(len(COMMAND_QUEUE)):
            command = COMMAND_QUEUE.pop(0)
            print("Executing: ",command)
            websocket = command["websocket"]
            data = command["data"]
            try:
                # BOT COMMS
                    #ADMIN
                if(data["command"] == "ping"):
                    pass
                elif(data["command"] == "admin_add_repo"):
                    if(db.IsUserAdmin(data["id"])):
                        db.AddNewRepo(data["url"])
                        await CONNECTIONS[BOT_ID].send(json.dumps({"success":True}))
                    else:
                        await CONNECTIONS[BOT_ID].send(json.dumps({"success":False,"reason":"You are not an admin!"}))
                elif(data["command"] == "admin_add_user"):
                    print(data["repo"])
                    print(db.CheckIfRepoExists(data["repo"]))
                    if(not db.CheckIfRepoExists(data["repo"])):
                        await CONNECTIONS[BOT_ID].send(json.dumps({"success":False,"reason":"That repo does not exist within our system"}))
                    else:
                        for user in data["users"]:
                           if(not db.DoesUserHaveRepoAccess(user,data["repo"])):
                               db.GiveUserRepoAccess(user,data["repo"])
                        await CONNECTIONS[BOT_ID].send(json.dumps({"success":True}))
                
                    #USER
                elif(data["command"] == "switch"):
                    if(db.CheckIfRepoExists(data["repo"])):
                        if(db.CheckIfUserHasRepoAccess(data["id"],data["repo"])):
                            status = db.SetUserCurrentRepo(data["id"],data["repo"])
                            await websocket.send(json.dumps({"success":status}))
                        else:
                            await websocket.send(json.dumps({"success":False,"reason":"You do not have access to that repo"}))
                    else:
                        await websocket.send(json.dumps({"success":False,"reason":"That repo does not exist within our system"}))

                elif(data["command"] == "commit"):
                    repo = db.GetUserCurrentRepo(data["id"])
                    if(repo == None):
                        await websocket.send(json.dumps({"success":False,"reason":"You do not have a repo selected"}))
                    data["repo"] = repo
                    await CONNECTIONS[data["id"]].send(json.dumps(data))

                    data["command"] = "auto_update"
                    for user in db.GetAllUsersWithAccessToRepo(data["repo"],data["id"]):
                        if(user in CONNECTIONS):
                            data["id"] = user
                            await CONNECTIONS[user].send(json.dumps(data))

                elif(data["command"] == "update"):
                    repo = db.GetUserCurrentRepo(data["id"])
                    if(repo == None):
                        await websocket.send(json.dumps({"success":False,"reason":"You do not have a repo selected"}))
                    data["repo"] = repo
                    await CONNECTIONS[data["id"]].send(json.dumps(data))

                elif(data["command"] == "checkout"):
                    repo = db.GetUserCurrentRepo(data["id"])
                    if(repo == None):
                        await websocket.send(json.dumps({"success":False,"reason":"You do not have a repo selected"}))
                    data["repo"] = repo
                    await CONNECTIONS[data["id"]].send(json.dumps(data))

                elif(data["command"] == "add"):
                    repo = db.GetUserCurrentRepo(data["id"])
                    if(repo == None):
                        await websocket.send(json.dumps({"success":False,"reason":"You do not have a repo selected"}))
                    data["repo"] = repo
                    await CONNECTIONS[data["id"]].send(json.dumps(data))

                elif(data["command"] == "remove"):
                    repo = db.GetUserCurrentRepo(data["id"])
                    if(repo == None):
                        await websocket.send(json.dumps({"success":False,"reason":"You do not have a repo selected"}))
                    data["repo"] = repo
                    await CONNECTIONS[data["id"]].send(json.dumps(data))

                    


                #CLIENT COMMS
                elif(data["command"] == "ping_response"):
                    pass

                elif(data["command"] == "commit_response"):
                    await CONNECTIONS[BOT_ID].send(json.dumps({"commit_success":data["command_success"]}))
                elif(data["command"] == "update_response"):
                    await CONNECTIONS[BOT_ID].send(json.dumps({"update_success":data["command_success"]}))
                elif(data["command"] == "checkout_response"):
                    await CONNECTIONS[BOT_ID].send(json.dumps({"checkout_success":data["command_success"]}))
                elif(data["command"] == "add_response"):
                    await CONNECTIONS[BOT_ID].send(json.dumps({"add_success":data["command_success"]}))
                elif(data["command"] == "remove_response"):
                    await CONNECTIONS[BOT_ID].send(json.dumps({"remove_success":data["command_success"]}))
                elif(data["command"] == "auto_update_response"):
                    await CONNECTIONS[BOT_ID].send(json.dumps({"auto_update_success":data}))
        
                elif(data["command"] == "update_settings"):
                    db.UpdateUserRepoSettings(data["id"],data["repo"],data["settings"])


                #OTHER
                elif(data["command"] == "send_repo_list"):
                    repos = db.GetUserRepoList(data["id"])
                    await websocket.send(json.dumps({"command":"send_repo_list","repos":repos}))
                    
                else:
                    print("Unknown Command:",data)

            except Exception as e:
                print("COMMAND Error %d: %s" % (e.args[0], e.args[1]),command)
                

        else:
            await asyncio.sleep(.1)


async def main_loop(websocket, path):
    try:
        username = await websocket.recv()
        print(time.time(),username,"is trying to connect")
        valid = db.CheckUsername(username)
        if(valid == False):
            db.CreateUser(username)
            valid = True
        elif(valid == None):
            valid = False     
        await websocket.send(json.dumps({"login_success":valid}))
        if(not valid):
            print(username,"failed to connect")
            await websocket.close()
            return
        print(username,"connected")
        CONNECTIONS[username] = websocket
        print("CONNECTIONS:",CONNECTIONS)

        COMMAND_QUEUE.append({"websocket":websocket,"data":{"command":"send_repo_list","id":username}})

        async for message in websocket:
            data = json.loads(message)
            if("id" not in data):
                data["id"] = username
            COMMAND_QUEUE.append({"websocket":websocket,"data":data})
                

    except Exception as e:
        print(e)
        

        keys = list(CONNECTIONS.keys())
        vals = list(CONNECTIONS.values())
        

        position = vals.index(websocket)
        key = keys[position]
        print("DC from: ",key,":",CONNECTIONS[key])
        del CONNECTIONS[key]



async def main():
    async with websockets.serve(main_loop, "192.168.1.231", 6969):
        await asyncio.Future()

loop = asyncio.get_event_loop()
loop.create_task(main())
loop.create_task(handle_comms())
loop.run_forever()
    
