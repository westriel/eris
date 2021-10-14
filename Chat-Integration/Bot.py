#https://discordpy.readthedocs.io/en/latest/api.html
#API for Discord.py


import discord
import asyncio
from datetime import *
import time

import asyncio
import websockets
import json


class MyClient(discord.Client):

    
    #ON MESSAGE
    async def on_message(self,message):
        if(message.content.startswith("e!")):
            await self.process_commands(message)



    #PROCESS COMMANDS
    async def process_commands(self,message):
        command = message.content.split()[0].lower()
        #Command List Here
        if(command == "e!ping"):
            await self.ping(message)
        elif(command == "e!commit"):
            await self.commit(message)
        elif(command == "e!update"):
            await self.update(message)
        elif(command == "e!checkout"):
            await self.checkout(message)


    async def commit(self,message):
        start = time.time()
        msg = " ".join(message.content.split()[2:])
        target = message.content.split()[1]
        print("Telling",target,"to commit")
        await self.websocket.send(json.dumps({"command":"commit","message":msg,"target":target}))
        print("Waiting for conf...")
        resp = json.loads(await self.websocket.recv())
        await message.channel.send(str(resp))
        
    async def update(self,message):
        start = time.time()
        target = message.content.split()[1]
        print("Telling",target,"to update")
        await self.websocket.send(json.dumps({"command":"update","target":target}))
        print("Waiting for conf...")
        resp = json.loads(await self.websocket.recv())
        await message.channel.send(str(resp))

    async def checkout(self,message):
        start = time.time()
        target = message.content.split()[1]
        print("Telling",target,"to update")
        await self.websocket.send(json.dumps({"command":"checkout","target":target}))
        print("Waiting for conf...")
        resp = json.loads(await self.websocket.recv())
        await message.channel.send(str(resp))

    async def ping(self,message):
        start = time.time()
        print("Sending ping command")
        await self.websocket.send(json.dumps({"command":"ping"}))
        print("Waiting for conf...")
        conf = await self.websocket.recv()
        print("Waiting for ping data...")
        bot_ping = time.time() - start
        ping_data = json.loads(await self.websocket.recv())
        #print(ping_data)
        #print("BOT:",bot_ping)
        print(ping_data)
        string = ""
        for data in ping_data:
            string += data + " : " + str(ping_data[data])+"s\n"
        string += "BOT : "+str(bot_ping)+"s"
        await message.channel.send(string)

    #WHEN READY
    async def on_ready(self):
        await self.change_presence(activity=discord.Game(name = "game"))
        print("Successfully set Bot's game status")

        
        #async with websockets.connect(uri) as websocket:
        self.websocket = await websockets.connect(uri)
        print(type(self.websocket))
        await self.websocket.send("ErisBot")
        status = json.loads(await self.websocket.recv())
        if(not status["username_valid"]):
            return
        await self.websocket.send("password")


    #CONNECTION
    async def on_connect(self):
        print("Bot has connected to server at time:",datetime.now())
    
    #DISCONNECTION
    async def on_disconnect(self):
        print("Bot has disconnected from server at time:",datetime.now())


uri = "ws://192.168.1.231:6969"
print("Starting Bot")
bot = MyClient()
file = open("TOKEN.txt",'r')
TOKEN = file.read()
file.close()
#print(TOKEN)

bot.run(TOKEN)