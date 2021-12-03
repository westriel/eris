#https://discordpy.readthedocs.io/en/latest/api.html
#API for Discord.py


import discord
import asyncio
from datetime import *
import time

import asyncio
import websockets
import json

LAST_CHANNEL = {} # keeps track of the last place a useer messaged


class MyClient(discord.Client):

    
    #ON MESSAGE
    # Function is called whenever the bot sees a message
    async def on_message(self,message):
        if(message.content.startswith("e!")): # If message starts with e!
            LAST_CHANNEL[message.author.id] = message.channel
            LAST_CHANNEL[self.user.id] = message.channel
            await self.process_commands(message)
        if(message.author.id == self.user.id): # save last place bot messaged
            LAST_CHANNEL[self.user.id] = message.channel



    #PROCESS COMMANDS
    # Parse the command message, run the correct command
    async def process_commands(self,message):
        command = message.content.split()[0].lower()
        
        #ADMIN COMMANDS
        if(command == "e!ping"):
            pass
            #await self.ping(message)
        elif(command == "e!add_repo"):
            await self.admin_add_repo(message)
        elif(command == "e!add_user"):
            await self.admin_add_user(message)

        #USER COMMANDS
        elif(command == "e!switch"):
            await self.switch(message)
        elif(command == "e!commit"):
            await self.commit(message)
        elif(command == "e!update"):
            await self.update(message)
        elif(command == "e!checkout"):
            await self.checkout(message)
        elif(command == "e!add"):
            await self.add(message)
        elif(command == "e!remove"):
            await self.remove(message)

    # Admin command to add a repo to the database
    async def admin_add_repo(self,message):
        start = time.time()
        command = message.content.split()
        if(len(command) != 2):
           await message.channel.send("Invalid usage: `add_repo`")
           return
        print("Adding new repo:",command[1])
        await self.websocket.send(json.dumps({"command":"admin_add_repo","url":command[1],"id":str(message.author.id)}))

    # Admin command to grant a user access to a repo
    async def admin_add_user(self,message):
        start = time.time()
        command = message.content.split()
        if(len(command) < 3):
            await message.channel.send("Invalid usage: `add_user`")
            return
        print("Adding user(s):",command[2:],"to repo:",command[1])
        ids = [x.id for x in message.mentions]
        await self.websocket.send(json.dumps({"command":"admin_add_user","users":ids,"repo":command[1],"id":str(message.author.id)}))

    # Command to switch a user's current working repo
    async def switch(self,message):
        start = time.time()
        command = message.content.split()
        if(len(command) != 2):
            await message.channel.send("Invalid usage: `switch`")
            return
        print("Switching",message.author.name,"to repo",command[1])
        await self.websocket.send(json.dumps({"command":"switch","repo":command[1],"id":str(message.author.id)}))

    # Command to have the client commit your repo
    async def commit(self,message):
        start = time.time()
        msg = " ".join(message.content.split()[1:])
        print("Telling",message.author.name,"to commit")
        await self.websocket.send(json.dumps({"command":"commit","message":msg,"id":str(message.author.id)}))

    # Command to have the client update your repo
    async def update(self,message):
        start = time.time()
        #target = message.content.split()[1]
        print("Telling",message.author.name,"to update")
        await self.websocket.send(json.dumps({"command":"update","id":str(message.author.id)}))

    # Command to checkout a repo to the set working directory
    async def checkout(self,message):
        start = time.time()
        print("Telling",message.author.name,"to update")
        await self.websocket.send(json.dumps({"command":"checkout","id":str(message.author.id)}))

    # Command to ping all clients. Currently disabled
    async def ping(self,message):
        await self.websocket.send(json.dumps({"command":"ping","id":str(message.author.id)}))

    # Command to have a client add files to repo
    async def add(self,message):
        start = time.time()
        print("Sending add command")
        await self.websocket.send(json.dumps({"command":"add","id":str(message.author.id),"files":message.content.split()[1:]}))

    # Command to have a client remove files from a repo
    async def remove(self,message):
        start = time.time()
        print("Sending remove command")
        await self.websocket.send(json.dumps({"command":"remove","id":str(message.author.id),"files":message.content.split()[1:]}))
        
        
    #WHEN READY
    # Function runs when the bot first connects to Discord's server
    async def on_ready(self):
        await self.change_presence(activity=discord.Game(name = "game"))
        print("Successfully set Bot's game status")

        while(not self.is_closed()): #Main loop, gets messages from websocket and parses them
            try:
                #Connect to server
                self.websocket = await websockets.connect(uri)
                await self.websocket.send("888218725810049055")
                status = json.loads(await self.websocket.recv())

                default_list = json.loads(await self.websocket.recv())
                print(default_list)

                # Loop through sent messages
                async for message in self.websocket:
                    data = json.loads(message)
                    if(data["command"] == "send"): # If server told bot to send a message
                        try:
                            await LAST_CHANNEL[int(data["id"])].send(self.get_user(int(data["id"])).mention+ " "+data["message"])
                        except KeyError:
                            await LAST_CHANNEL[self.user.id].send(self.get_user(int(data["id"])).mention+ " "+data["message"])
                    elif(data["command"] == "ping_client"): # Ping response. Currently unused
                        pass
                        #await self.websocket.send(json.dumps({"command":"ping_response"}))
                    else:
                        print("UNHANDLED COMM:",data)
                                                                 

                    
            # If error occurs, wait 1 second and reconnect
            except Exception as e:
                print("Waiting due to:",e)
                
                await asyncio.sleep(1)
                

        
            


    #CONNECTION
    async def on_connect(self):
        print("Bot has connected to server at time:",datetime.now())
    
    #DISCONNECTION
    async def on_disconnect(self):
        print("Bot has disconnected from server at time:",datetime.now())

# Set variables needed for bot to run
uri = "ws://192.168.1.231:6969"
print("Starting Bot")
bot = MyClient(intents=discord.Intents.all())
file = open("TOKEN.txt",'r')
TOKEN = file.read()
file.close()

# Start Bot
bot.run(TOKEN)
