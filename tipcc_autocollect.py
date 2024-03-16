from asyncio import TimeoutError, sleep
from logging import (CRITICAL, DEBUG, ERROR, INFO, WARNING, Formatter,
                     StreamHandler, getLogger)
from math import acosh, asinh, atanh, ceil, cos, cosh, e, erf, exp
from math import fabs as abs
from math import factorial, floor
from math import fmod as mod
from math import (gamma, gcd, hypot, log, log1p, log2, log10, pi, pow, sin,
                  sinh, sqrt, tan, tau)
from re import compile
from time import time
from urllib.parse import quote, unquote

from aiohttp import ClientSession
from art import tprint
from discord import Client, HTTPException, LoginFailure, Message, NotFound
from discord.ext import tasks
from questionary import checkbox, select, text


class ColourFormatter(
    Formatter
):  # Taken from discord.py-self and modified to my liking.

    LEVEL_COLOURS = [
        (DEBUG, "\x1b[40;1m"),
        (INFO, "\x1b[34;1m"),
        (WARNING, "\x1b[33;1m"),
        (ERROR, "\x1b[31m"),
        (CRITICAL, "\x1b[41m"),
    ]

    FORMATS = {
        level: Formatter(
            f"\x1b[30;1m%(asctime)s\x1b[0m {colour}%(levelname)-8s\x1b[0m \x1b[35m%(name)s\x1b[0m %(message)s \x1b[30;1m(%(filename)s:%(lineno)d)\x1b[0m",
            "%d-%b-%Y %I:%M:%S %p",
        )
        for level, colour in LEVEL_COLOURS
    }

    def format(self, record):
        formatter = self.FORMATS.get(record.levelno)
        if formatter is None:
            formatter = self.FORMATS[DEBUG]

        if record.exc_info:
            text = formatter.formatException(record.exc_info)
            record.exc_text = f"\x1b[31m{text}\x1b[0m"

        output = formatter.format(record)

        record.exc_text = None
        return output


handler = StreamHandler()
formatter = ColourFormatter()

handler.setFormatter(formatter)
logger = getLogger("tipcc_autocollect")
logger.addHandler(handler)
logger.setLevel("INFO")


def cbrt(x):
    return pow(x, 1 / 3)


try:
    from ujson import dump, load
except ModuleNotFoundError:
    logger.warning("ujson not found, using json instead.")
    from json import dump, load
except ImportError:
    logger.warning("ujson not found, using json instead.")
    from json import dump, load
else:
    logger.info("ujson found, using ujson.")


channel = None


print("\033[0;35m")
tprint("QuartzWarrior", font="smslant")
print("\033[0m")

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
decimal_regex = compile(r"^-?\d+(?:\.\d+)$")


def validate_token(token):
    if token_regex.search(token):
        return True
    else:
        return False


def validate_decimal(decimal):
    if decimal_regex.match(decimal):
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
        logger.debug("Token saved.")

if config["FIRST"] == True:
    config["CPM"] = int(
        text(
            "What is your CPM (Characters Per Minute)?\nThis is to make the phrase drop collector more legit.\nRemember, the higher the faster!",
            default="310",
            qmark="->",
            validate=lambda x: (validate_decimal(x) or x.isnumeric()) and float(x) >= 0,
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
        validate=lambda x: ((validate_decimal(x) or x.isnumeric()) and float(x) >= 0)
        or x == "",
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
            validate=lambda x: (validate_decimal(x) or x.isnumeric()) or x == "",
            default="0",
            qmark="->",
        ).ask()
        if manual_delay != "":
            config["DELAY"] = float(manual_delay)
        else:
            config["DELAY"] = 0
    with open("config.json", "w") as f:
        dump(config, f, indent=4)
    logger.debug("Config saved.")

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
    logger.debug("ID saved.")

if config["channel_id"] == 0:
    config["channel_id"] = int(
        text(
            "What is the channel id where you want your alt to tip your main?\n(Remember, the tip.cc bot has to be in the server with this channel.)\n\nIf None, send 1.",
            validate=lambda x: x.isnumeric() and (17 <= len(x) <= 19 or int(x) == 1),
            default="1",
            qmark="->",
        ).ask()
    )
    with open("config.json", "w") as f:
        dump(config, f, indent=4)
    logger.debug("Channel ID saved.")

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
    logger.info(f"Logged in as {client.user.name}#{client.user.discriminator}")
    if config["channel_id"] != 1 and client.user.id != config["id"]:
        tipping.start()
        logger.info("Tipping started.")
    else:
        logger.warning("Disabling tipping as requested.")


@tasks.loop(minutes=10.0)
async def tipping():
    await channel.send("$bals top")
    logger.debug("Sent command: $bals top")
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
            logger.debug(f"Sent tip: {content}")
        if button_disabled:
            try:
                await answer.components[0].children[2].click()
                logger.debug("Clicked next page button")
                return
            except IndexError:
                try:
                    await answer.components[0].children[0].click()
                    logger.debug("Clicked first page button")
                    return
                except IndexError:
                    return
        else:
            await button.click()
            await sleep(1)
            answer = await channel.fetch_message(answer.id)


@tipping.before_loop
async def before_tipping():
    logger.info("Waiting for bot to be ready before tipping starts...")
    await client.wait_until_ready()


@client.event
async def on_message(original_message: Message):
    if original_message.content.startswith(
        ("$airdrop", "$triviadrop", "$mathdrop", "$phrasedrop", "$redpacket")
    ) and not any(word in original_message.content.lower() for word in banned_words):
        logger.debug(f"Detected drop: {original_message.content}")
        try:
            tip_cc_message = await client.wait_for(
                "message",
                check=lambda message: message.author.id == 617037497574359050
                and message.channel.id == original_message.channel.id
                and message.embeds
                and message.embeds[0].footer
                and (
                    "ends" in message.embeds[0].footer.text.lower()
                    or (
                        "Trivia time - " in message.embeds[0].title
                        and "ended" in message.embeds[0].footer.text.lower()
                    )
                )
                and str(original_message.author.id) in message.embeds[0].description,
                timeout=15,
            )
            logger.debug("Detected tip.cc message from drop.")
        except TimeoutError:
            logger.exception(
                "Timeout occurred while waiting for tip.cc message, skipping."
            )
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
            logger.info(
                f"Ignored drop for {embed.description.split('**')[1]} {embed.description.split('**')[2].split(')')[0].replace(' (','')}"
            )
            return
        if config["SMART_DELAY"]:
            logger.debug("Smart delay enabled, waiting...")
            drop_ends_in = embed.timestamp.timestamp() - time()
            if drop_ends_in < 0:
                logger.debug("Drop ended, skipping...")
                return
            delay = drop_ends_in / 4
            await sleep(delay)
            logger.info(f"Waited {round(delay, 2)} seconds before claiming.")
        elif config["DELAY"] != 0:
            logger.debug("Manual delay enabled, waiting...")
            await sleep(config["DELAY"])
            logger.info(f"Waited {config['DELAY']} seconds before claiming.")
        try:
            if (
                "ended" in embed.footer.text.lower()
                and "Trivia time - " not in embed.title
            ):
                logger.debug("Drop ended, skipping...")
                return
            elif "An airdrop appears" in embed.title and not config["DISABLE_AIRDROP"]:
                logger.debug("Airdrop detected, entering...")
                button = tip_cc_message.components[0].children[0]
                if "Enter airdrop" in button.label:
                    await button.click()
                    logger.info(
                        f"Entered airdrop for {embed.description.split('**')[1]} {embed.description.split('**')[2].split(')')[0].replace(' (','')}"
                    )
            elif "Phrase drop!" in embed.title and not config["DISABLE_PHRASEDROP"]:
                logger.debug("Phrasedrop detected, entering...")
                content = embed.description.replace("\n", "").replace("**", "")
                content = content.split("*")
                try:
                    content = content[1].replace("​", "").replace("\u200b", "").strip()
                except IndexError:
                    logger.exception("Index error occurred, skipping...")
                    pass
                else:
                    logger.debug("Typing and sending message...")
                    length = len(content) / config["CPM"] * 60
                    async with original_message.channel.typing():
                        await sleep(length)
                    await original_message.channel.send(content)
                    logger.info(
                        f"Entered phrasedrop for {embed.description.split('**')[1]} {embed.description.split('**')[2].split(')')[0].replace(' (','')}"
                    )
            elif "appeared" in embed.title and not config["DISABLE_REDPACKET"]:
                logger.debug("Redpacket detected, claiming...")
                button = tip_cc_message.components[0].children[0]
                if "envelope" in button.label:
                    await button.click()
                    logger.info(
                        f"Claimed envelope for {embed.description.split('**')[1]} {embed.description.split('**')[2].split(')')[0].replace(' (','')}"
                    )
            elif "Math" in embed.title and not config["DISABLE_MATHDROP"]:
                logger.debug("Mathdrop detected, entering...")
                content = embed.description.replace("\n", "").replace("**", "")
                content = content.split("`")
                try:
                    content = content[1].replace("​", "").replace("\u200b", "")
                except IndexError:
                    logger.exception("Index error occurred, skipping...")
                    pass
                else:
                    logger.debug("Evaluating math and sending message...")
                    answer = eval(content)
                    logger.debug(f"Answer: {answer}")
                    length = len(str(answer)) / config["CPM"] * 60
                    async with original_message.channel.typing():
                        await sleep(length)
                    await original_message.channel.send(answer)
                    logger.info(
                        f"Entered mathdrop for {embed.description.split('**')[1]} {embed.description.split('**')[2].split(')')[0].replace(' (','')}"
                    )
            elif "Trivia time - " in embed.title and not config["DISABLE_TRIVIADROP"]:
                logger.debug("Triviadrop detected, entering...")
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
                                logger.info(
                                    f"Entered triviadrop for {embed.description.split('**')[1]} {embed.description.split('**')[2].split(')')[0].replace(' (','')}"
                                )
                                return

        except AttributeError:
            logger.exception("Attribute error occurred")
            return
        except HTTPException:
            logger.exception("HTTP exception occurred")
            return
        except NotFound:
            logger.exception("Not found exception occurred")
            return
    elif original_message.content.startswith(
        ("$airdrop", "$triviadrop", "$mathdrop", "$phrasedrop", "$redpacket")
    ) and any(word in original_message.content.lower() for word in banned_words):
        logger.info("Banned word detected, skipping...")


if __name__ == "__main__":
    try:
        client.run(config["TOKEN"], log_handler=handler, log_formatter=formatter)
    except LoginFailure:
        logger.critical("Invalid token, restart the program.")
        config["TOKEN"] = ""
        with open("config.json", "w") as f:
            dump(config, f, indent=4)
