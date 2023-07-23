from re import M
import sys
from discord import Message, TextChannel
from discord.ext.commands import Bot
from typing import List, Optional

from libs.utils import Utils
from libs.database import Database
from libs.flag import MessageFlag

class MessageLogger:
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.db = Database()
        self.utils = Utils(bot=self.bot)
    
    async def log_message(self, channel_id: int, content: str) -> None:
        log_channel = await self.__get_log_channel(channel_id=channel_id)
        if log_channel == None:
            return None
        
        await log_channel.send(content=content)

    async def log_marked_message(self, channel_id: int, message: Message, message_flag: MessageFlag) -> Optional[Message]:
        log_channel = await self.__get_log_channel(channel_id=channel_id)
        if log_channel == None:
            return None

        embed = self.utils.create_embed(
            title=f'{message_flag.name} Message',
            color=self.__get_log_color(message_flag=message_flag),
            description=message.content,
            fields={ 'Message Link': f'[Click me]({message.jump_url})' },
            author=message.author,
            timestamp=message.created_at)
        
        message = await log_channel.send(embed=embed)
        return message

    async def __get_log_channel(self, channel_id: int) -> Optional[TextChannel]:
        if channel_id == None:
            return None
        log_channel = await self.utils.fetch_text_channel(channel_id=channel_id)
        if log_channel == None:
            print(f"Error: Log channel '{channel_id}' is invalid.", file=sys.stderr)
            return None
        return log_channel

    def __get_log_color(self, message_flag: MessageFlag) -> int:
        if message_flag == MessageFlag.Safe:
            return 0x6bcb77
        elif message_flag == MessageFlag.Suspicious:
            return 0xffd93d
        elif message_flag == MessageFlag.Malicious:
            return 0xff6b6b
        else:
            raise NotImplementedError
