from asyncio import sleep, TimeoutError
from re import compile
from aiohttp import ClientSession
from urllib.parse import quote, unquote
from art import tprint
from time import time
from discord import Client, LoginFailure, HTTPException, NotFound, Message
from discord.ext import tasks
from questionary import text, select, checkbox
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


def cbrt(x):
    return pow(x, 1 / 3)


try:
    from ujson import load, dump
except ModuleNotFoundError:
    from json import load, dump
except ImportError:
    from json import load, dump


channel = None


print("\033[0;35m")
tprint("QuartzWarrior", font="smslant")

try:
    with open("config.json", "r") as f:
        config = load(f)
except FileNotFoundError:
    config = {
        "TOKEN": "",
        "CPM": 310,
        "DELAY": 0,
        "SMART_DELAY": True,
        "IGNORE_DROPS_UNDER": 0.0,
        "DISABLE_AIRDROP": False,
        "DISABLE_TRIVIADROP": False,
        "DISABLE_MATHDROP": False,
        "DISABLE_PHRASEDROP": False,
        "DISABLE_REDPACKET": False,
        "BANNED_WORDS": ["bot", "ban"],
        "FIRST": True,
        "id": 0,
        "channel_id": 0,
    }
    with open("config.json", "w") as f:
        dump(config, f, indent=4)

token_regex = compile(r"[\w-]{24}\.[\w-]{6}\.[\w-]{27,}")


def validate_token(token):
    if token_regex.search(token):
        return True
    else:
        return False


if config["TOKEN"] == "":
    token_input = text(
        "What is your discord token?",
        qmark="->",
        validate=lambda x: validate_token(x),
    ).ask()
    if token_input is not None:
        config["TOKEN"] = token_input
        with open("config.json", "w") as f:
            dump(config, f, indent=4)

if config["FIRST"] == True:
    config["CPM"] = int(
        text(
            "What is your CPM (Characters Per Minute)?\nThis is to make the phrase drop collector more legit.\nRemember, the higher the faster!",
            default="310",
            qmark="->",
            validate=lambda x: x.isnumeric() and int(x) >= 0,
        ).ask()
    )
    config["FIRST"] = False
    config["DISABLE_AIRDROP"] = False
    config["DISABLE_TRIVIADROP"] = False
    config["DISABLE_MATHDROP"] = False
    config["DISABLE_PHRASEDROP"] = False
    config["DISABLE_REDPACKET"] = False
    disable_drops = checkbox(
        "What drop types do you want to disable? (Leave blank for none)",
        choices=[
            "airdrop",
            "triviadrop",
            "mathdrop",
            "phrasedrop",
            "redpacket",
        ],
        qmark="->",
    ).ask()
    if not disable_drops:
        disable_drops = []
    if "airdrop" in disable_drops:
        config["DISABLE_AIRDROP"] = True
    if "triviadrop" in disable_drops:
        config["DISABLE_TRIVIADROP"] = True
    if "mathdrop" in disable_drops:
        config["DISABLE_MATHDROP"] = True
    if "phrasedrop" in disable_drops:
        config["DISABLE_PHRASEDROP"] = True
    if "redpacket" in disable_drops:
        config["DISABLE_REDPACKET"] = True
    ignore_drops_under = text(
        "What is the minimum amount of money you want to ignore?",
        default="0",
        qmark="->",
        validate=lambda x: (x.isnumeric() and int(x) >= 0) or x == "",
    ).ask()
    if ignore_drops_under != "":
        config["IGNORE_DROPS_UNDER"] = float(ignore_drops_under)
    else:
        config["IGNORE_DROPS_UNDER"] = 0.0
    smart_delay = select(
        "Do you want to enable smart delay? (This will make the bot wait for the drop to end before claiming it)",
        choices=["yes", "no"],
        qmark="->",
    ).ask()
    if smart_delay == "yes":
        config["SMART_DELAY"] = True
    else:
        config["SMART_DELAY"] = False
        manual_delay = text(
            "What is the delay you want to use in seconds? (Leave blank for none)",
            validate=lambda x: x.isnumeric() or x == "",
            default="0",
            qmark="->",
        ).ask()
        if manual_delay != "":
            config["DELAY"] = float(manual_delay)
        else:
            config["DELAY"] = 0
    with open("config.json", "w") as f:
        dump(config, f, indent=4)

if config["id"] == 0:
    config["id"] = int(
        text(
            "What is your main accounts id?\n\nIf you are sniping from your main, put your main accounts' id.",
            validate=lambda x: x.isnumeric() and 17 <= len(x) <= 19,
            qmark="->",
        ).ask()
    )
    with open("config.json", "w") as f:
        dump(config, f, indent=4)

if config["channel_id"] == 0:
    config["channel_id"] = int(
        text(
            "What is the channel id where you want your alt to tip your main?\n(Remember, the tip.cc bot has to be in the server with this channel.)\n\nIf None, send 1.",
            validate=lambda x: x.isnumeric() and 17 <= len(x) <= 19,
            default="1",
            qmark="->",
        ).ask()
    )
    with open("config.json", "w") as f:
        dump(config, f, indent=4)

config["DISABLE_AIRDROP"] = config.get("DISABLE_AIRDROP", False)
config["DISABLE_TRIVIADROP"] = config.get("DISABLE_TRIVIADROP", False)
config["DISABLE_MATHDROP"] = config.get("DISABLE_MATHDROP", False)
config["DISABLE_PHRASEDROP"] = config.get("DISABLE_PHRASEDROP", False)
config["DISABLE_REDPACKET"] = config.get("DISABLE_REDPACKET", False)

banned_words = set(config["BANNED_WORDS"])

client = Client()


@client.event
async def on_ready():
    global channel
    channel = client.get_channel(config["channel_id"])
    print(
        f"Logged in as {client.user.name}#{client.user.discriminator} ({client.user.id})"
    )
    if config["channel_id"] != 1:
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
            button_disabled = button.disabled
        except:
            button_disabled = True
        for crypto in answer.embeds[0].fields:
            if "Estimated total" in crypto.name:
                continue
            if "DexKit" in crypto.name:
                content = f"$tip <@{config['id']}> all {crypto.name.replace('*', '').replace('DexKit (BSC)', 'bKIT')}"
            else:
                content = f"$tip <@{config['id']}> all {crypto.name.replace('*', '')}"
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
                and "ends" in message.embeds[0].footer.text.lower()
                and str(original_message.author.id) in message.embeds[0].description,
                timeout=15,
            )
        except TimeoutError:
            return
        embed = tip_cc_message.embeds[0]
        money = float(
            embed.description.split("≈")[1]
            .split(")")[0]
            .strip()
            .replace("$", "")
            .replace(",", "")
        )
        if money < config["IGNORE_DROPS_UNDER"]:
            print(
                f"Ignored drop for {embed.description.split('**')[1]} {embed.description.split('**')[2].split(')')[0].replace(' (','')}"
            )
            return
        if config["SMART_DELAY"]:
            drop_ends_in = embed.timestamp.timestamp() - time()
            if drop_ends_in < 0:
                return
            delay = drop_ends_in / 4
            await sleep(delay)
            print(f"Waited {round(delay, 2)} seconds before claiming.")
        elif config["DELAY"] != 0:
            await sleep(config["DELAY"])
            print(f"Waited {config['DELAY']} seconds before claiming.")
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
            dump(config, f, indent=4)
