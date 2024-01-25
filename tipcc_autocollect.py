from asyncio import sleep, TimeoutError
from aiohttp import ClientSession
from urllib.parse import quote, unquote
from art import tprint
from discord import Client, LoginFailure, HTTPException, NotFound, Message
from discord.ext import tasks
from math import (
    sqrt,
    floor,
    ceil,
    fabs as abs,
    sin,
    cos,
    tan,
    pow,
    exp,
    log,
    log1p,
    log2,
    log10,
    cosh,
    sinh,
    pi,
    tau,
    e,
    factorial,
    gcd,
    gamma,
    fmod as mod,
    hypot,
    acosh,
    asinh,
    atanh,
    erf,
)


def round(x):
    return int(x // 1 + 0.5)


def cbrt(x):
    return pow(x, 1 / 3)


try:
    from ujson import load, dump
except ModuleNotFoundError:
    from json import load, dump


channel = None


print("\033[0;35m")
tprint("QuartzWarrior", font="smslant")

with open("config.json", "r") as f:
    config = load(f)

client = Client()

if config["TOKEN"] == "":
    config["TOKEN"] = input("What is your discord token?\n\n-> ")
    with open("config.json", "w") as f:
        dump(config, f)

if config["FIRST"] == "True":
    config["CPM"] = int(
        input(
            "What is your CPM (Characters Per Minute)?\nThis is to make the phrase drop collector "
            "more legit.\nA decent CPM would be 310. Remember, the higher the faster!\n\n-> "
        )
    )
    config["FIRST"] = "False"
    input("Want to disable any drop types? (Press enter to continue)\n\n-> ")
    print(
        "Drop types:\n\n$airdrop\n$triviadrop\n$mathdrop\n$phrasedrop\n$redpacket\n\n"
    )
    disable_drops = input(
        "What drop types do you want to disable? (Separate with spaces)\n\n-> "
    ).split(" ")
    for drop in disable_drops:
        if "airdrop" in drop.lower():
            config["DISABLE_AIRDROP"] = True
        if "triviadrop" in drop.lower():
            config["DISABLE_TRIVIADROP"] = True
        elif "mathdrop" in drop.lower():
            config["DISABLE_MATHDROP"] = True
        elif "phrasedrop" in drop.lower():
            config["DISABLE_PHRASEDROP"] = True
        elif "redpacket" in drop.lower():
            config["DISABLE_REDPACKET"] = True
    with open("config.json", "w") as f:
        dump(config, f)

if config["id"] == 0:
    config["id"] = int(
        input(
            "What is your main accounts id?\n\nIf you are sniping from your main, put your main accounts' id.\n\n-> "
        )
    )
    with open("config.json", "w") as f:
        dump(config, f)

if config["channel_id"] == 0:
    config["channel_id"] = int(
        input(
            "What is the channel id where you want your alt to tip your main?\n(Remember, the tip.cc bot has to be in the server with this channel.)\n\nIf None, send 1.\n\n-> "
        )
    )
    with open("config.json", "w") as f:
        dump(config, f)

config["DISABLE_AIRDROP"] = config.get("DISABLE_AIRDROP", False)
config["DISABLE_TRIVIADROP"] = config.get("DISABLE_TRIVIADROP", False)
config["DISABLE_MATHDROP"] = config.get("DISABLE_MATHDROP", False)
config["DISABLE_PHRASEDROP"] = config.get("DISABLE_PHRASEDROP", False)
config["DISABLE_REDPACKET"] = config.get("DISABLE_REDPACKET", False)

banned_words = config["BANNED_WORDS"]
banned_words = set(banned_words)


@client.event
async def on_ready():
    global channel
    channel = client.get_channel(config["channel_id"])
    print(
        f"Logged in as {client.user.name}#{client.user.discriminator} ({client.user.id})"
    )
    tipping.start()


@tasks.loop(minutes=10.0)
async def tipping():
    await channel.send("$bals top")
    answer = await client.wait_for(
        "message",
        check=lambda message: message.author.id == 617037497574359050
        and message.embeds,
    )
    try:
        pages = int(answer.embeds[0].author.name.split("/")[1].replace(")", ""))
    except:
        pages = 1
    if not answer.components:
        button_disabled = True
    for _ in range(pages):
        try:
            button = answer.components[0].children[1]
            if button.disabled:
                button_disabled = True
            else:
                button_disabled = False
        except:
            button_disabled = True
        for crypto in answer.embeds[0].fields:
            if "Estimated total" in crypto.name:
                pass
            else:
                if "DexKit" in crypto.name:
                    content = f"$tip <@{config['id']}> all {crypto.name.replace('*', '').replace('DexKit (BSC)', 'bKIT')}"
                    async with channel.typing():
                        await sleep(len(content) / config["CPM"] * 60)
                    await channel.send(content)
                else:
                    content = (
                        f"$tip <@{config['id']}> all {crypto.name.replace('*', '')}"
                    )
                    async with channel.typing():
                        await sleep(len(content) / config["CPM"] * 60)
                    await channel.send(content)
        if button_disabled:
            try:
                await answer.components[0].children[2].click()
                return
            except IndexError:
                try:
                    await answer.components[0].children[0].click()
                    return
                except IndexError:
                    return
        else:
            await button.click()
            await sleep(1)
            answer = await channel.fetch_message(answer.id)


@tipping.before_loop
async def before_tipping():
    print("Waiting for bot to be ready before tipping starts...")
    await client.wait_until_ready()


@client.event
async def on_message(original_message: Message):
    if original_message.content.startswith(
        ("$airdrop", "$triviadrop", "$mathdrop", "$phrasedrop", "$redpacket")
    ) and not any(word in original_message.content.lower() for word in banned_words):
        try:
            tip_cc_message = await client.wait_for(
                "message",
                check=lambda message: message.author.id == 617037497574359050
                and message.channel.id == original_message.channel.id
                and message.embeds
                and "Ends" in message.embeds[0].footer.text.lower()
                and str(original_message.author.id) in message.embeds[0].description,
                timeout=15,
            )
        except TimeoutError:
            return
        embed = tip_cc_message.embeds[0]
        try:
            if (
                "ended" in embed.footer.text.lower()
                and "Trivia time - " not in embed.title
            ):
                return
            elif "An airdrop appears" in embed.title and not config["DISABLE_AIRDROP"]:
                button = tip_cc_message.components[0].children[0]
                if "Enter airdrop" in button.label:
                    await button.click()
                    print(
                        f"Entered airdrop for {embed.description.split('**')[1]} {embed.description.split('**')[2].split(')')[0].replace(' (','')}"
                    )
            elif "Phrase drop!" in embed.title and not config["DISABLE_PHRASEDROP"]:
                content = embed.description.replace("\n", "").replace("**", "")
                content = content.split("*")
                try:
                    content = content[1].replace("​", "").replace("\u200b", "").strip()
                except IndexError:
                    pass
                else:
                    length = len(content) / config["CPM"] * 60
                    async with original_message.channel.typing():
                        await sleep(length)
                    await original_message.channel.send(content)
                    print(
                        f"Entered phrasedrop for {embed.description.split('**')[1]} {embed.description.split('**')[2].split(')')[0].replace(' (','')}"
                    )
            elif "appeared" in embed.title and not config["DISABLE_REDPACKET"]:
                button = tip_cc_message.components[0].children[0]
                if "envelope" in button.label:
                    await button.click()
                    print(
                        f"Claimed envelope for {embed.description.split('**')[1]} {embed.description.split('**')[2].split(')')[0].replace(' (','')}"
                    )
            elif "Math" in embed.title and not config["DISABLE_MATHDROP"]:
                content = embed.description.replace("\n", "").replace("**", "")
                content = content.split("`")
                try:
                    content = content[1].replace("​", "").replace("\u200b", "")
                except IndexError:
                    pass
                else:
                    answer = eval(content)
                    length = len(str(answer)) / config["CPM"] * 60
                    async with original_message.channel.typing():
                        await sleep(length)
                    await original_message.channel.send(answer)
                    print(
                        f"Entered mathdrop for {embed.description.split('**')[1]} {embed.description.split('**')[2].split(')')[0].replace(' (','')}"
                    )
            elif "Trivia time - " in embed.title and not config["DISABLE_TRIVIADROP"]:
                category = embed.title.split("Trivia time - ")[1].strip()
                bot_question = embed.description.replace("**", "").split("*")[1]
                async with ClientSession() as session:
                    async with session.get(
                        f"https://quartzwarrior.xyz/bots/tipcc_autocollect/{quote(category)}.csv"
                    ) as resp:
                        lines = (await resp.text()).splitlines()
                        for line in lines:
                            question, answer = line.split(",")
                            if bot_question.strip() == unquote(question).strip():
                                answer = unquote(answer).strip()
                                buttons = tip_cc_message.components[0].children
                                for button in buttons:
                                    if button.label.strip() == answer:
                                        await button.click()
                                print(
                                    f"Entered triviadrop for {embed.description.split('**')[1]} {embed.description.split('**')[2].split(')')[0].replace(' (','')}"
                                )
                                return

        except AttributeError:
            return
        except HTTPException:
            return
        except NotFound:
            return
    elif original_message.content.startswith(
        ("$airdrop", "$triviadrop", "$mathdrop", "$phrasedrop", "$redpacket")
    ) and any(word in original_message.content.lower() for word in banned_words):
        print("Banned word detected, skipping...")


if __name__ == "__main__":
    try:
        client.run(config["TOKEN"])
    except LoginFailure:
        print("Invalid token, restart the program.")
        config["TOKEN"] = ""
        with open("config.json", "w") as f:
            dump(config, f)
