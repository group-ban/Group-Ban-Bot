# Group Ban Bot

<div align='center'>
<img width='300px' src='https://github.com/group-ban/group-ban.github.io/blob/master/dist/img/GB.png?raw=true'>
<br/>
<b style='margin-bottom:20px;'>An Moderator bot for Bale written in Python.</b>

[![Python Version](https://img.shields.io/badge/Python-3.8_|_3.9_|_3.10_|_3.11_-red?logo=python&style=plastic)](https://python.org)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/f7933dec85524c57842bbc033ded6d2e)](https://codacy.com/gh/group-ban/group-ban-bot/dashboard)
[![Project License](https://img.shields.io/github/license/group-ban/Group-Ban-Bot?style=plastic)](https://opensource.org/licenses/MIT)
[![Website](https://img.shields.io/badge/website-up-green?logo=github&style=plastic)](https://groupban.ir)

</div>

## Installation

GroupBan can be hosted only on cPanel.

### cPanel hosting

1. Create a new Python app
2. Clone this repo in `YourApp/public` directory
    ```console
    $ git clone https://github.com/group-ban/group-ban-bot
    $ cd group-ban-bot
    ```
3. Create a Bale bot account, grant the necessary intents, and invite the bot to the Chat
4. Rename `config-simple.json` to `config.json` and Put your bot information in the config file
5. Create a MySql database
6. install dependencies using pip
    ```console
    $ pip install -r requirements.txt
    ```
7. Start the bot
    ```console
    $ python3 bot.py
    ```
    
# Contributing

Contributions to GroupBan are always welcome, whether it be improvements to the documentation or new functionality, please feel free to make the change. 
