import asyncio
import websockets

import json
import time

from Database import *

COMMAND_QUEUE = []
CONNECTIONS = {}
PINGS = {}

file = open("SETTINGS.txt",'r')
SETTINGS = eval(file.read())
file.close()

# Discord ID of the bot. Needs to be changed before being launched
BOT_ID = SETTINGS["BOT_ID"]

db = Database()

# Helper function - gets the websocket associated with the ID
def GetIDFromSocket(websocket):
    return list(CONNECTIONS.keys())[list(CONNECTIONS.values()).index(websocket)]


# One of two main loops. Loops through commands in the queue
# Ueses a queue to ensure that commands are processed in order
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
                # Command that starts the pinging process. Currently unused
                if(data["command"] == "ping"):
                    PINGS = {}
                    for name in CONNECTIONS:
                        COMMAND_QUEUE.append({"websocket":CONNECTIONS[name],"data":{"command":"ping_client","id":name}})
                    COMMAND_QUEUE.append({"websocket":CONNECTIONS[BOT_ID],"data":{"command":"return_pings","id":data["id"]}})

                # Command that pings a client. Currently unused
                elif(data["command"] == "ping_client"):
                    PINGS[websocket] = time.time()
                    websocket.send(json.dumps({"command":"ping"}))

                # Command that sends the final ping list to the bot. Currently unused
                elif(data["command"] == "return_pings"):
                    msg = ""
                    for web in CONNECTIONS:
                        msg += GetIDFromSocket(CONNECTIONS[web]) + " : " + PINGS[web] + "\n"
                    await websocket.send(json.dumps({"command":"send","id":data["id"],"message":msg}))
                    
                # Interacts with the Database to add the repo to the repo list in the Database   
                elif(data["command"] == "admin_add_repo"):
                    if(db.IsUserAdmin(data["id"])):
                        db.AddNewRepo(data["url"])
                        await websocket.send(json.dumps({"command":"send","id":data["id"],"message":data["url"]+" was successfully added."}))
                    else:
                        await websocket.send(json.dumps({"command":"send","id":data["id"],"message":"Adding repo failed: `You are not an admin!`"}))

                # Interacts with the Database to grant a user access to a repo
                elif(data["command"] == "admin_add_user"):
                    print(data["repo"])
                    print(db.CheckIfRepoExists(data["repo"]))
                    if(not db.CheckIfRepoExists(data["repo"])):
                        await websocket.send(json.dumps({"command":"send","id":data["id"],"message":"Adding user to repo failed: `The provided repo does not exist within our system! Double check the full URL of the repo.`"}))
                    else:
                        for user in data["users"]:
                           if(not db.DoesUserHaveRepoAccess(user,data["repo"])):
                               db.GiveUserRepoAccess(user,data["repo"])
                               await websocket.send(json.dumps({"command":"send","id":user,"message":"has been granted access to "+data["repo"]}))
                
                    #USER
                # Interacts with the Database and sets the user's current repo
                elif(data["command"] == "switch"):
                    if(db.CheckIfRepoExists(data["repo"])):
                        if(db.CheckIfUserHasRepoAccess(data["id"],data["repo"])):
                            status = db.SetUserCurrentRepo(data["id"],data["repo"])
                            await websocket.send(json.dumps({"command":"send","id":data["id"],"message":"You have successfully switched to "+data["repo"]}))
                        else:
                            await websocket.send(json.dumps({"command":"send","id":data["id"],"message":"Switch failed: `You do not have acces to that repo!`"}))
                    else:
                        await websocket.send(json.dumps({"command":"send","id":data["id"],"message":"Switch failed: `That repo does not exist within our system! Double check the full URL of the repo.`"}))

                # Tells the user's client connection to run the commit command. Will also set notifications and sends auto_updates
                elif(data["command"] == "commit"):
                    repo = db.GetUserCurrentRepo(data["id"])
                    if(repo == None):
                        await websocket.send(json.dumps({"command":"send","id":data["id"],"message":"Commit failed: `You do not have a repo selected`"}))

                        continue
                    data["repo"] = repo
                    await CONNECTIONS[data["id"]].send(json.dumps(data))

                    await asyncio.sleep(1) # Wait one second to let the SVN Server catch up

                    data["command"] = "auto_update"
                    for user in db.GetAllUsersWithAccessToRepo(data["repo"],data["id"]):
                        if(user in CONNECTIONS and db.GetSettingValueFromUserAndRepo(user,"auto_update",data["repo"])):
                            data["id"] = user
                            await CONNECTIONS[user].send(json.dumps(data))

                        if(db.GetSettingValueFromUserAndRepo(user,"commit_update",data["repo"])):
                            print("Sending ping!")
                            await websocket.send(json.dumps({"command":"send","id":user,"message":"The repo "+data["repo"]+" has been updated"}))
                                
                # Tells the user's client connection to run the update command
                elif(data["command"] == "update"):
                    repo = db.GetUserCurrentRepo(data["id"])
                    if(repo == None):
                        await websocket.send(json.dumps({"success":False,"reason":"You do not have a repo selected"}))
                    data["repo"] = repo
                    await CONNECTIONS[data["id"]].send(json.dumps(data))

                # Tells the user's client connection to run the checkout command.
                elif(data["command"] == "checkout"):
                    repo = db.GetUserCurrentRepo(data["id"])
                    if(repo == None):
                        await websocket.send(json.dumps({"success":False,"reason":"You do not have a repo selected"}))
                    data["repo"] = repo
                    await CONNECTIONS[data["id"]].send(json.dumps(data))

                # Tells the user's client connection to run the add command.
                elif(data["command"] == "add"):
                    repo = db.GetUserCurrentRepo(data["id"])
                    if(repo == None):
                        await websocket.send(json.dumps({"success":False,"reason":"You do not have a repo selected"}))
                    data["repo"] = repo
                    await CONNECTIONS[data["id"]].send(json.dumps(data))

                # Tells the user's client connection to run the remove command
                elif(data["command"] == "remove"):
                    repo = db.GetUserCurrentRepo(data["id"])
                    if(repo == None):
                        await websocket.send(json.dumps({"success":False,"reason":"You do not have a repo selected"}))
                    data["repo"] = repo
                    await CONNECTIONS[data["id"]].send(json.dumps(data))

                    


                #CLIENT COMMS

                # Recieve the ping response from client. Currently unused
                elif(data["command"] == "ping_response"):
                    PINGS[websocket] = time.time() - PINGS[websocket]

                # Receive the commit response from client
                elif(data["command"] == "commit_response"):
                    if(data["command_success"]):
                        await CONNECTIONS[BOT_ID].send(json.dumps({"command":"send","id":GetIDFromSocket(websocket),"message":"Files successfully committed"}))
                    else:
                        await CONNECTIONS[BOT_ID].send(json.dumps({"command":"send","id":GetIDFromSocket(websocket),"message":"Commit failed: `"+data["reason"]+"`"}))

                # Receive the update response from client
                elif(data["command"] == "update_response"):
                    if(data["command_success"]):
                        await CONNECTIONS[BOT_ID].send(json.dumps({"command":"send","id":GetIDFromSocket(websocket),"message":"Repo successfully updated"}))
                    else:
                        await CONNECTIONS[BOT_ID].send(json.dumps({"command":"send","id":GetIDFromSocket(websocket),"message":"Update failed: `"+data["reason"]+"`"}))

                # Receive the checkout response from client
                elif(data["command"] == "checkout_response"):
                    if(data["command_success"]):
                        await CONNECTIONS[BOT_ID].send(json.dumps({"command":"send","id":GetIDFromSocket(websocket),"message":"Repo successfully checkout out"}))
                    else:
                        await CONNECTIONS[BOT_ID].send(json.dumps({"command":"send","id":GetIDFromSocket(websocket),"message":"Checkout failed: `"+data["reason"]+"`"}))

                # Receive the add response from client
                elif(data["command"] == "add_response"):
                    if(data["command_success"]):
                        await CONNECTIONS[BOT_ID].send(json.dumps({"command":"send","id":GetIDFromSocket(websocket),"message":"Files successfully added"}))
                    else:
                        await CONNECTIONS[BOT_ID].send(json.dumps({"command":"send","id":GetIDFromSocket(websocket),"message":"Add failed: `"+data["reason"]+"`"}))
                # Receive the remove response from client
                elif(data["command"] == "remove_response"):
                    if(data["command_success"]):
                        await CONNECTIONS[BOT_ID].send(json.dumps({"command":"send","id":GetIDFromSocket(websocket),"message":"Files successfully removed"}))
                    else:
                        await CONNECTIONS[BOT_ID].send(json.dumps({"command":"send","id":GetIDFromSocket(websocket),"message":"Remove failed: `"+data["reason"]+"`"}))

                # Receive the auto_update response from client. Will do nothing if user doesn't want notifications for auot updates
                elif(data["command"] == "auto_update_response"):
                    print("\n\nAUTO RESPONSE USER",GetIDFromSocket(websocket),"\n\n",db.GetSettingValueFromUserAndRepo(GetIDFromSocket(websocket),"update_update",data["repo"]),"\n\n")
                    if(data["command_success"] and db.GetSettingValueFromUserAndRepo(GetIDFromSocket(websocket),"update_update",data["repo"])):
                        await CONNECTIONS[BOT_ID].send(json.dumps({"command":"send","id":GetIDFromSocket(websocket),"message":"Your repo of "+data["repo"]+" was automatically updated"}))

                # Receive the commit response from client
                elif(data["command"] == "update_settings"):
                    db.UpdateUserRepoSettings(data["id"],data["repo"],data["settings"])


                #OTHER
                # Sends the repo list to the client on login
                elif(data["command"] == "send_repo_list"):
                    repos = db.GetUserRepoList(data["id"])
                    await websocket.send(json.dumps({"command":"send_repo_list","repos":repos}))
                    
                else:
                    print("Unknown Command:",data)

            # Key Error means that a command was executed but the user wasn't logged in
            except KeyError as e:
                print("User is not logged in on Client!",{"command":"send","id":str(e).replace("'",""),"message":"You are not logged in on the Eris Client!"})
                await CONNECTIONS[BOT_ID].send(json.dumps({"command":"send","id":str(e).replace("'",""),"message":"You are not logged in on the Eris Client!"}))


            except Exception as e:
                print("COMMAND Error %d: %s" % (e.args[0], e.args[1]),command)
 
                
        # If no commands, wait .1 seconds and check again
        else:
            await asyncio.sleep(.1)

# One of two main loops. This loop gets communications from the clients and bot and adds them to the queue
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
                
    # If an Exception occurs, assume the client disconnected and remove them from the movie
    except Exception as e:
        keys = list(CONNECTIONS.keys())
        vals = list(CONNECTIONS.values())
        

        position = vals.index(websocket)
        key = keys[position]
        print("DC from: ",key,":",CONNECTIONS[key])
        del CONNECTIONS[key]


# Function to encapsulate the websocket loop
async def main():
    async with websockets.serve(main_loop, SETTINGS["IP"], SETTINGS["PORT"]):
        await asyncio.Future()
# Add the lops to asyncio and start them
loop = asyncio.get_event_loop()
loop.create_task(main())
loop.create_task(handle_comms())
loop.run_forever()
    
