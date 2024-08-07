# Telegram info stealer monitoring (private project)

## TODO and Ideas for future improvement
- [ ] Compressed file handle -> RAR, ZIP: Ongoing
- [x] Add Alerting Webhook to team
- [ ] Handle duplicated data
- [ ] Compressed file with password : Ongoing
- [x] Extract Stealer Information
- [ ] Adding more telegram dork and google dork
- [x] Remove hardcoded search keyword 

Not only we can monitoring info stealer sample data if we can leverage and monitoring the chat, to find the keyword such as tool name
or selling prices, text behavior or any user

## Overview
The control flow of telegram monitoring script

![Telegram Monitoring Control Flow](images/teleFlow.svg)

## Installation
Require using python3, to install package that required please run the command below after clone the repo

``` shell
pip install -r requirement.txt
```

Why we install cryptg: https://stackoverflow.com/questions/64047589/why-is-telethon-so-slow-to-send-files, I amaze by this knowledge -> when install this package,
telethon decrypt data using C rather than Python -> which is much much faster
Or you can just use the FastTelethonHelper

## How to use it / Configuration

**Create .env** file and has these information, these information can generate using telegram api webpage (https://core.telegram.org/api/obtaining_api_id -> show how you can get the api_hash and app_id).  

``` conf
api_hash="your_api_hash"
api_id="your_app_id"
phone_number = "your_phone_number"
download_path="path"
webhook_url='' # Add your URL Webhook right here, but use '' not ""
splunk_host=''
splunk_port=''
splunk_token='' # This is HEC Token 
```
**Download path is the path that you will store the leak data you crawl from the telegram channel**

Create a file name **monitored_wordlist.txt** and put your keyword to monitor from these data leak for example:
```text
@your_company_email
@other_email
some general keyword with newline (enter)
```
## Using Docker

Docker is easier to deploy because the dependecies won't be an issues and the code won't have to rely on the platform -> banana code could run fine :"> 

```shell
docker build -t telegram-monitoring .
```

```shell
docker run -it telegram-monitoring 
```

It will prompt you to "Please enter your phone (or bot token):" you need to enter your phone number and then provide the script with the code that has been send to your Telegram account

## Russian Info Stealer 

Here are the few telegram channel that has the above information: (the list will get update and verify weekly) 
- https://t.me/+YZ9oDLRW0Q82NWQy (HelloKitty Cloud) info-stealer - Redline and Meta
- https://t.me/txtbaseurl (TXTBaseURL) Login Credentials 
- https://t.me/FreeLogPassForAll Login credentials - centralized a lot of source in here
- https://t.me/tor_log (Tor Log)
- https://t.me/cbanke_logs (cBanke) Login credentials - info-stealer
- https://t.me/RedlineViper (Redline) Redline logs
- https://t.me/BorwitaFreeLogs (Redline)
- https://t.me/CRONCLOUD Don't know yet but will crawl later
- https://t.me/URLPASSWORD Login credentials - with GB of data
- https://t.me/MoonCombo Login credentials - with GB of data
- https://t.me/FREE_RDP_BIN (RDP and VPS) Free RDP, Login Credentials
- https://t.me/DarkBotnetGT (DarkBotnet GT) Free RDP, Login Credentials
- https://t.me/FreeRDPvpsBIN Free RDP
- https://t.me/freevpsusa Free RDP
- https://t.me/cloudtxt 
- https://t.me/URLPASSWORD -> 
- https://t.me/urllogpas -> 
- https://t.me/fr33d4t4 -> Logs need to go to URL to download
- https://t.me/baseleak ->
- https://t.me/llinkcloud -> Logs with GB of data, but base 2020-2022 -> still good
- https://t.me/breachdetector (Dark web monitoring and logs) -> good channels
- https://t.me/DarkfeedNews (Dark net information) -> picture not txt
- https://t.me/BoldCloud (Logs but old) -> need to ingest old data
- https://t.me/RedlineLogsGroup (Look like some cool shit)
- 

# How to find these channel or Telegram channel in general
- https://telegra.ph/Tips-how-to-find-private-hidden-personal-groups-and-channels---TelegramPrivateChatLeaks-08-10
In this post there are few thing I like about it
- About the invitation link of Telegram 
- Using google dork, and telegram dork to find channel that private

Combine with the keyword and understanding of Telegram channel URL we can craft few dork to search for these leak channel. There are some basic search queries:
- site:t.me/joinchat access
- site:t.me/joinchat logs
- site:t.me/joinchat txt 
- site:t.me/joinchat 
- t.me/joinchat/+
- t.me/joinchat/AAAA
- intext:t.me/ 
- intext:t.me/joinchat {keyword}
- site:t.me/ {keyword}

Some keyword that might relevant: 
redline, logs, cloudlogs, logsfree, free logs, hacking software, rat, ddos, trojan, 
botnet, infect, virus, spyware, cloud extractor, bltools, pegasus, cve, dcrat, venom,
aurora, stealer, free stealer, dropper, binder, blackhat, fud, asyncrat


## How does it work 

The script will use telethon to interact with telegram download any TXT, RAR, CSV, ZIP file in chat or channel that you have join by using the API Hash and API ID that you generated by following this document (https://docs.telethon.dev/en/stable/basic/signing-in.html)

Search for keyword which is your email handle, domain or anything that important to you and output to a file or any channel that you like (Telegram, Tea,s chat, Discord by using webhook)

## Extract Stealer Information 

Refs: https://github.com/milxss/universal_stealer_log_parser/tree/main -> use this git repo to do all kind of stealer information extraction