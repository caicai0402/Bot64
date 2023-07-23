from typing import Any
from discord import Guild, Message
from discord.ext.commands import Bot

from libs.database import Database
from libs.utils import Utils
from libs.logger import MessageLogger
from libs.flag import MessageFlag, PenaltyPolicyFlag
from libs.emoji import EmojiHelper

class PenaltyAction:
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.db = Database()
        self.logger = MessageLogger(bot=self.bot)
        self.utils = Utils(bot=self.bot)
    
    def get_penalty_func(self, policy: PenaltyPolicyFlag) -> Any:
        penalty_func_map = {
            PenaltyPolicyFlag.Ignore: self.ignore,
            PenaltyPolicyFlag.Mute: self.mute,
            PenaltyPolicyFlag.Kick: self.kick,
            PenaltyPolicyFlag.Ban: self.ban
        }
        if policy not in penalty_func_map:
            raise NotImplementedError('Invalid penalty policy')
        return penalty_func_map[policy]
    
    async def handle_penalty(self, message: Message, message_flag: MessageFlag):
        guild_id = message.guild.id
        guild = await self.bot.fetch_guild(guild_id=guild_id)
        log_channel_id = self.db.get_log_channel_id(guild_id=guild_id)
        member_id = message.author.id
        
        reason = f'{message_flag.name} message'

        log_message = await self.logger.log_marked_message(channel_id=log_channel_id, message=message, message_flag=message_flag)
        if log_message != None:
            await EmojiHelper.add_penalty_actions(message=log_message)
        
        get_policy_func = self.db.get_suspicious_policy if message_flag == MessageFlag.Suspicious else self.db.get_malicious_policy
        policy = get_policy_func(guild_id=guild_id)
        
        await self.get_penalty_func(policy=policy)(guild=guild, member_id=member_id, log_channel_id=log_channel_id, reason=reason)
    
    async def ignore(self, *_) -> None:
        pass

    async def mute(self, guild: Guild, member_id: int, log_channel_id: int, reason: str) -> None:
        mute_role_id = self.db.get_mute_role_id(guild_id=guild.id)
        if mute_role_id == None:
            await self.logger.log_message(channel_id=log_channel_id, content='Error: mute role has not been set.')
            return None
        
        mute_role = await self.utils.fetch_guild_role(guild=guild, role_id=mute_role_id)
        if mute_role == None:
            await self.logger.log_message(channel_id=log_channel_id, content='Error: mute role is invalid.')
            return None

        applied = await self.utils.apply_role(guild=guild, member_id=member_id, role=mute_role)
        if applied == False:
            await self.logger.log_message(channel_id=log_channel_id, content='Error: failed to apply the mute role to the user.')
            return None
        
        await self.utils.dm_user(user_id=member_id, content=f'You have been muted in the guild `{guild.name}`. Reason: `{reason}`')
        await self.logger.log_message(channel_id=log_channel_id, content='Successfully apply the mute role to the user.')
    
    async def kick(self, guild: Guild, member_id: int, log_channel_id: int, reason: str) -> None:
        await self.utils.dm_user(user_id=member_id, content=f'You have been kicked from the guild `{guild.name}`. Reason: `{reason}`')
        kicked = await self.utils.kick_user(guild=guild, user_id=member_id, reason=reason)
        if kicked == False:
            await self.logger.log_message(channel_id=log_channel_id, content='Error: failed to kick the user from the guild.')
            return None
        await self.logger.log_message(channel_id=log_channel_id, content='Successfully kicked the user from the guild.')

    async def ban(self, guild: Guild, member_id: int, log_channel_id: int, reason: str) -> None:
        await self.utils.dm_user(user_id=member_id, content=f'You have been banned from the guild `{guild.name}`. Reason: `{reason}`')
        banned = await self.utils.ban_user(guild=guild, user_id=member_id, reason=reason, delete_message_days=7)
        if banned == False:
            await self.logger.log_message(channel_id=log_channel_id, content='Error: failed to ban the user from the guild.')
            return None
        await self.logger.log_message(channel_id=log_channel_id, content='Successfully banned the user from the guild.')