#https://discordpy.readthedocs.io/en/latest/api.html
#API for Discord.py


import discord
import asyncio
from datetime import *
import time

import asyncio
import websockets
import json

LAST_CHANNEL = {}


class MyClient(discord.Client):

    
    #ON MESSAGE
    async def on_message(self,message):
        if(message.content.startswith("e!")):
            LAST_CHANNEL[message.author.id] = message.channel
            LAST_CHANNEL[self.user.id] = message.channel
            await self.process_commands(message)
        if(message.author.id == self.user.id):
            LAST_CHANNEL[self.user.id] = message.channel



    #PROCESS COMMANDS
    async def process_commands(self,message):
        command = message.content.split()[0].lower()
        #Command List Here
        #ADMIN COMMANDS
        if(command == "e!ping"):
            await self.ping(message)
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

    async def admin_add_repo(self,message):
        start = time.time()
        command = message.content.split()
        if(len(command) != 2):
           await message.channel.send("Invalid usage: `add_repo`")
           return
        print("Adding new repo:",command[1])
        await self.websocket.send(json.dumps({"command":"admin_add_repo","url":command[1],"id":str(message.author.id)}))


    async def admin_add_user(self,message):
        start = time.time()
        command = message.content.split()
        if(len(command) < 3):
            await message.channel.send("Invalid usage: `add_user`")
            return
        print("Adding user(s):",command[2:],"to repo:",command[1])
        ids = [x.id for x in message.mentions]
        await self.websocket.send(json.dumps({"command":"admin_add_user","users":ids,"repo":command[1],"id":str(message.author.id)}))


    async def switch(self,message):
        start = time.time()
        command = message.content.split()
        if(len(command) != 2):
            await message.channel.send("Invalid usage: `switch`")
            return
        print("Switching",message.author.name,"to repo",command[1])
        await self.websocket.send(json.dumps({"command":"switch","repo":command[1],"id":str(message.author.id)}))

        #await message.channel.send(str(resp))

    async def commit(self,message):
        start = time.time()
        msg = " ".join(message.content.split()[1:])
        print("Telling",message.author.name,"to commit")
        await self.websocket.send(json.dumps({"command":"commit","message":msg,"id":str(message.author.id)}))
        
    async def update(self,message):
        start = time.time()
        #target = message.content.split()[1]
        print("Telling",message.author.name,"to update")
        await self.websocket.send(json.dumps({"command":"update","id":str(message.author.id)}))

    async def checkout(self,message):
        start = time.time()
        #target = message.content.split()[1]
        print("Telling",message.author.name,"to update")
        await self.websocket.send(json.dumps({"command":"checkout","id":str(message.author.id)}))

    async def ping(self,message):
        await self.websocket.send(json.dumps({"command":"ping","id":str(message.author.id)}))

    async def add(self,message):
        start = time.time()
        print("Sending add command")
        await self.websocket.send(json.dumps({"command":"add","id":str(message.author.id),"files":message.content.split()[1:]}))

    async def remove(self,message):
        start = time.time()
        print("Sending remove command")
        await self.websocket.send(json.dumps({"command":"remove","id":str(message.author.id),"files":message.content.split()[1:]}))
        
        
    #WHEN READY
    async def on_ready(self):
        await self.change_presence(activity=discord.Game(name = "game"))
        print("Successfully set Bot's game status")

        while(not self.is_closed()):
            try:
        
                #async with websockets.connect(uri) as websocket:
                self.websocket = await websockets.connect(uri)
                print(type(self.websocket))
                await self.websocket.send("888218725810049055")
                status = json.loads(await self.websocket.recv())

                default_list = json.loads(await self.websocket.recv())
                print(default_list)

                async for message in self.websocket:
                    data = json.loads(message)
                    if(data["command"] == "send"):
                        #print(data["id"])
                        try:
                            await LAST_CHANNEL[int(data["id"])].send(self.get_user(int(data["id"])).mention+ " "+data["message"])
                        except KeyError:
                            await LAST_CHANNEL[self.user.id].send(self.get_user(int(data["id"])).mention+ " "+data["message"])
                    elif(data["command"] == "ping_client"):
                        await self.websocket.send(json.dumps({"command":"ping_response"}))
                    else:
                        print("UNHANDLED COMM:",data)
                                                                 

                    

            except Exception as e:
                print("Waiting due to:",e)
                
                await asyncio.sleep(1)
                

        
            


    #CONNECTION
    async def on_connect(self):
        print("Bot has connected to server at time:",datetime.now())
    
    #DISCONNECTION
    async def on_disconnect(self):
        print("Bot has disconnected from server at time:",datetime.now())


uri = "ws://192.168.1.231:6969"
print("Starting Bot")
bot = MyClient(intents=discord.Intents.all())
file = open("TOKEN.txt",'r')
TOKEN = file.read()
file.close()
#print(TOKEN)

bot.run(TOKEN)
