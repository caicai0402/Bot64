# bot64

## Members

- B07902108 翁祖毅
- B07902079 張庭禎
- B07902002 連崇安
- B07902128 蘇聖祐
- B08208032 胡材溢
- B10902069 楊智翰
- B07902032 徐振棠
- B07902036 李國弘
- B08902111 孫梓翔

## Introduction

- Bot64 is a discord bot which monitors and filters dirty words and phishing links.
- Each message sent in the guild are examined by Bot64 and marked with 3 mutual exclusive flags: `Safe`, `Suspicious` or `Malicious`.
- For those discord members sending messages marked with the last 2 flags, i.e. `Suspicious` or `Malicious`, Bot64 would exert penalties on them according to the policies set by the guild administrators.
- Possible policies are `Ignore`, `Mute`, `Kick` or `Ban`.
    - `Ignore`: Bot64 simply ignores this behavior.
    - `Mute`: if the mute role is set, Bot64 would add the role to the discord member.
    - `Kick`: Bot64 kicks the discord member out of the guild. He/She can rejoin the guild at any time.
    - `Ban`: Bot64 bans the discord member. He/She cannot rejoin the guild before unbanned.

## Deployment

- Please provide the following environment variables:
    - `BOT_TOKEN`: Discord Bot Token. You can create one at [Discord Developer Portal](https://discord.com/developers/applications).
    - `MONGO_URL`: MongoDB connection URL. (In development stage, we use [MongoDB Atlas](https://www.mongodb.com) free tier to test our bot.)
- Run the following commands in your terminal:
```sh
git clone https://github.com/110-2-OO-Software-Design-Group-4/bot64.git
cd bot64
pip install -r requirements.txt
cp .env.example .env # Please add environment variables in '.env'
python3 main.py
```
## Caveats

- You need to invite the discord bot into a guild to make it works!
- Bot64 needs at least the following permissions: `MANAGE_ROLES`, `KICK_MEMBERS` and `BAN_MEMBERS` to work correctly.
- If you choose to set the mute role, please make sure Bot64 has a higher role than the mute role. Otherwise, it could not add the mute role to the discord member, due to Discord's default limit.
- You are responsible for setting the mute role properly to deny the discord members with the mute role to send messages in any channel.

## Algorithm of filter

- The input is the message of Discord, which is in `message.content`, after running the filter, the filter function would return one of three Flags: `Safe`, `Suspicious`, `Malicious`.
- There are two database that contents the sensitive words, phishing links, which were set in the `name.txt`, `link.txt`, respectively, all the data are sorted in advance. 
- When running the function:
    - The program would produce multiple substrings of the message content, every substrings starts with number or alphabet (and the former char must not be number or alphabet), there are three kinds of substrings:
        1. The length of substring is `Max(length of sensitive words in name.txt)` -> To search for multiple-word key
        2. The substring ends with chars that are not number or alphabet -> To search for single-word key
        3. The substring ends with space and '\n' -> To search for link
    - Using the binary-search algorithm, we search all the substrings in `name.txt`, search the third kind of substrings in `link.txt`. The sensitive score increases if the sentive word were found in substring.
    - The sensitive score is determined by:
        1. `Sensitive words`: `1 + len(Sensitive words) / 8`
        2. `Sensitive links`: `100000`
    - The final score of the message content is given by: `(Sensitive score)/log2(len(message content))`, and return the Flag:
        1. `Safe`: final score = 0
        2. `Suspicious`: 0 < final score < 0.5
        3. `Malicious`: final score >= 0.5
- Complexity analysis: Set the length of message `L`, the Number of keys in name.txt `N`, the Number of keys in link.txt `M`, the temporal complexity would be `L*log(Max(M, N))`, and the spacial complexity would be `Max(L, N, M)`
