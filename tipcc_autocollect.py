import asyncio
import json
import random

#from aiohttp_socks import ProxyType, ProxyConnector, ChainProxyConnector
import aiohttp
import art
import discord

proxies = ["syd","tor","par","fra","lin","nrt","ams","waw","lis","sin","mad","sto","lon","iad","atl","chi","dal","den","lax","mia","nyc","sea","phx"]

print("\033[0;35m")
art.tprint('QuartzWarrior', font="smslant")

with open("config.json", 'r') as f:
    config = json.load(f)

client = discord.Client()

if config["TOKEN"] == "":
    config["TOKEN"] = input("What is your discord token?\n\n-> ")
    with open("config.json", 'w') as f:
        json.dump(config, f)

if config["FIRST"] == "True":
    config["CPM"] = int(input("What is your CPM (Characters Per Minute)?\nThis is to make the phrase drop collector "
                              "more legit.\nA decent CPM would be 310. Remember, the higher the faster!\n\n-> "))
    config["FIRST"] = "False"
    with open("config.json", 'w') as f:
        json.dump(config, f)
        
if config["id"] == 0:
    config["id"] = int(input("What is your main accounts id?\n\nIf you are sniping from your main, put your main accounts' id.\n\n-> "))
    with open("config.json", 'w') as f:
        json.dump(config, f)
        
if config["channel_id"] == 0:
    config["channel_id"] = int(input("What is the channel id where you want your alt to tip your main?\n(Remember, the tip.cc bot has to be in the server with this channel.)\n\nIf None, send 1.\n\n-> "))
    with open("config.json", 'w') as f:
        json.dump(config, f)

async def tip(amount: str):
    amount = ''.join(i for i in amount if not i.isdigit())
    amount = amount.replace(".", "").replace(", ", "").replace(" ", "")
    channel = client.get_channel(config["channel_id"])
    if channel is None:
        print("Channel is invalid.")
        config["channel_id"] = 0
        with open("config.json", 'w') as f:
            json.dump(config, f)
        return
    elif config["channel_id"] == 1:
        return
    user = client.get_user(config["id"])
    if user is None:
        print("Main account is invalid.")
        config["id"] = 0
        with open("config.json", 'w') as f:
            json.dump(config, f)
        return
    elif config["id"] == 0 or config["id"] == client.user.id:
        return
    try:
        await channel.send(f"$tip {user.mention} all {amount}")
    except discord.HTTPException:
        print("An HTTPException occured. The message has not been sent.")
        return
    except discord.Forbidden:
        print(f"The alt account does not have permission to send messages in {channel.name}.")
        return

@client.event
async def on_ready():
    print(f"Logged in as {client.user.name}#{client.user.discriminator} ({client.user.id})")


@client.event
async def on_message(message):
    if message.author.id == 617037497574359050:
        if message.embeds:
            embed = message.embeds[0]
            try:
                if "ended" in embed.footer.text.lower() and "Trivia time - " not in embed.title:
                    await tip(embed.description.split('**')[1])
                elif "An airdrop appears" in embed.title:
                    comp = message.components
                    comp = comp[0].children
                    button = comp[0]
                    if "Enter airdrop" in button.label:
                        await button.click()
                        print(f"Entered airdrop for {embed.description.split('**')[1]} {embed.description.split('**')[2].split(')')[0].replace(' (','')}")
                elif "Phrase drop!" in embed.title:
                    content = embed.description.replace("\n", "").replace("**", "")
                    content = content.split("*")
                    try:
                        content = content[1].replace("​", "").replace("\u200b", "")
                    except IndexError:
                        pass
                    else:
                        length = len(content) / config["CPM"] * 60
                        async with message.channel.typing():
                            await asyncio.sleep(length)
                        await message.channel.send(content)
                        print(f"Entered phrasedrop for {embed.description.split('**')[1]} {embed.description.split('**')[2].split(')')[0].replace(' (','')}")
                elif "appeared" in embed.title:
                    comp = message.components
                    comp = comp[0].children
                    button = comp[0]
                    if "envelope" in button.label:
                        await button.click()
                        print(f"Claimed envelope for {embed.description.split('**')[1]} {embed.description.split('**')[2].split(')')[0].replace(' (','')}")
            except AttributeError:
                pass
            except discord.HTTPException:
                return
            except discord.NotFound:
                return

try:
    client.run(config["TOKEN"])
except discord.LoginFailure:
    print("Invalid token, restart the program.")
    config["TOKEN"] = ""
    with open("config.json", 'w') as f:
        json.dump(config, f)
