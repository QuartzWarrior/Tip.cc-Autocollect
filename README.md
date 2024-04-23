# Tip.cc-AutoCollector

An autonomous tip.cc collector bot developed from scratch.

---

## Capabilities

### Core Features

- Autonomous Airdrop Collection ✉️
- Stealthy Phrasedrop Collection 🗣️
- Red Packet Acquisition 🧧

### Advanced Features

- Mathdrop Collection (supports all math functions + anti-detection) ➕➖✖️➗
- Triviadrop Collection (utilizes [OpenTDB](https://github.com/QuartzWarrior/OTDB-Source)) ❓

### Extra Features

- Word Filtering 🚫
- Auto Transfer of Earnings to Primary Account 💸
- Smart Delay: The bot waits 1/4 of the drop duration before claiming. ⏳
- Customizable Delay: Set your own delay time if smart delay is disabled. ⏰
- Earnings Threshold: Checks if earnings are above a certain amount before claiming. 💰
- Banned Words List: Avoids claiming drops with specified words. 🙊
- Drop Type Disabling: Choose to disable any specific drop type. ❌
- Auto Transfer of All Earnings: Automatically sends all earnings to the primary account. 💼

## Motivation

This bot was developed to address doubts and accusations of code plagiarism on the [Self-bots subreddit](https://www.reddit.com/r/Discord_selfbots/). Rest assured, it is an original creation. ✅

## Setup Guide

1. Install [Python](https://www.python.org/downloads/). 🐍
2. Open your terminal in the downloaded folder. 💻
3. Install dependencies:

- Linux: `python3 -m pip install -U -r requirements.txt`
- Windows: `py -m pip install -U -r requirements.txt`
<!-- markdownlint-disable-next-line MD029 -->
4. Update the banned words in `config.json` (Do not modify anything else, configuration happens when you run the script). 📝
<!-- markdownlint-disable-next-line MD029 -->
5. Run the script and follow the instructions to start earning! ▶️

- Linux: `python3 tipcc_autocollect.py`
- Windows: `py tipcc_autocollect.py`

## Configuration

- `config.json` contains all the configuration options for the bot. 📁
- `config.json` is automatically generated when you run the script. 🔄
- Do not modify `config.json` while the script is running. 🚫
<!-- markdownlint-disable MD033 -->
<details>
<summary>Configuration Options</summary>

```py
{
    "TOKEN": "", # Your Discord token
    "PRESENCE": "", # Your custom presence (online, idle, dnd, invisible)
    "CPM": 310, # Your average CPM (Characters per minute, find this [here](https://livechat.com/typing-speed-test/))
    "FIRST": true, # Do not change, just tells the program that you haven't run the script yet
    "id": 0, # Your main account's Discord ID, the bot will send earnings to this account
    "channel_id": 0, # The channel ID where you want to send your earnings to your main account in
    "TARGET_AMOUNT": 0.0, # The amount of earnings you want to reach before transferring to your main account
    "SMART_DELAY": true, # Whether to use smart delay or not, the bot will wait 1/4 of the drop duration before claiming
    "DELAY": 1, # The delay in seconds if smart delay is disabled
    "BANNED_WORDS": [ # The list of banned words, the bot will not claim drops with these words
        "bot",
        "ban"
    ],
    "WHITELIST": [], # The list of whitelisted guilds, the bot will only claim drops in these guilds
    "BLACKLIST": [], # The list of blacklisted guilds, the bot will not claim drops in these guilds
    "CHANNEL_BLACKLIST": [], # The list of blacklisted channels, the bot will not claim drops in these channels
    "IGNORE_USERS": [], # The list of users to ignore, the bot will not claim drops from these users
    "WHITELIST_ON": false, # Whether to use the whitelist or not
    "BLACKLIST_ON": false, # Whether to use the blacklist or not
    "CHANNEL_BLACKLIST_ON": false, # Whether to use the channel blacklist or not
    "IGNORE_DROPS_UNDER": 0.0, # The amount of earnings to ignore drops under
    "IGNORE_TIME_UNDER": 0.0, # The time to ignore drops under
    "IGNORE_THRESHOLDS": [], # The list of earnings thresholds to ignore drops under
    "DISABLE_AIRDROP": false, # Whether to disable airdrops or not
    "DISABLE_TRIVIADROP": false, # Whether to disable triviadrops or not
    "DISABLE_MATHDROP": false, # Whether to disable mathdrops or not
    "DISABLE_PHRASEDROP": false, # Whether to disable phrasedrops or not
    "DISABLE_REDPACKET": false # Whether to disable red packets or not
}
```

</details>
<!-- markdownlint-enable MD033 -->

## Disclaimer

---

> Tip.cc-AutoCollector was created for educational purposes only. The developers and contributors do not take any responsibility for your Discord account. ⚠️
