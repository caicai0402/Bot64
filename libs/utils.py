import random, traceback
from datetime import datetime
from typing import Union, Optional
from discord import TextChannel, Embed, Guild, User, Member, Role, Color
from discord.ext.commands import Bot

class Utils:
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def fetch_text_channel(self, channel_id: int) -> Optional[TextChannel]:
        try:
            channel = await self.bot.fetch_channel(channel_id=channel_id)
            return channel if isinstance(channel, TextChannel) else None
        except:
            traceback.print_exc()
        return None

    async def fetch_guild_role(self, guild: Guild, role_id: int) -> Optional[Role]:
        try:
            roles = await guild.fetch_roles()
            for role in roles:
                if role.id == role_id:
                    return role
        except:
            traceback.print_exc()
        return None
    
    async def fetch_guild_member(self, guild: Guild, member_id: int) -> Optional[Member]:
        try:
            member = await guild.fetch_member(member_id=member_id)
            return member
        except:
            traceback.print_exc()
        return None
    
    async def fetch_user(self, user_id: int) -> Optional[User]:
        try:
            user = await self.bot.fetch_user(user_id=user_id)
            return user
        except:
            traceback.print_exc()
        return None

    async def apply_role(self, guild: Guild, member_id: int, role: Role) -> bool:
        try:
            member = await self.fetch_guild_member(guild=guild, member_id=member_id)
            if member == None:
                return False
            await member.add_roles(role)
            return True
        except:
            traceback.print_exc()
        return False
    
    async def dm_user(self, user_id: int, content: str) -> None:
        try:
            user = await self.fetch_user(user_id=user_id)
            if user == None:
                return None
            dm_channel = user.dm_channel
            if dm_channel == None:
                dm_channel = await user.create_dm()
            await dm_channel.send(content=content)
        except:
            traceback.print_exc()
    
    async def kick_user(self, guild: Guild, user_id: int, reason: str=None) -> bool:
        try:
            user = await self.fetch_user(user_id=user_id)
            if user == None:
                return False
            await guild.kick(user=user, reason=reason)
        except:
            traceback.print_exc()
        return False
    
    async def ban_user(self, guild: Guild, user_id: int, reason: str=None, delete_message_days: int=7) -> bool:
        try:
            user = await self.fetch_user(user_id=user_id)
            if user == None:
                return False
            await guild.ban(user=user, reason=reason, delete_message_days=delete_message_days)
        except:
            traceback.print_exc()
        return False
    
    def create_embed(
        self,
        title: Optional[str]=None,
        color: Optional[str]=None,
        description: Optional[str]=None,
        fields: Optional[dict]=None,
        author: Optional[Union[User, Member]]=None,
        image: Optional[str]=None,
        thumbnail: Optional[str]=None,
        inline: bool=True,
        timestamp: Optional[datetime]=None):
        
        footer_prefix = ''
        embed_kwargs = dict()

        if title != None:
            embed_kwargs['title'] = title
        
        if color != None:
            if color == 'random':
                color = Color(value=random.randint(0x000000, 0xFFFFFF))
            embed_kwargs['color'] = color
        
        if description != None:
            embed_kwargs['description'] = description

        embed = Embed(**embed_kwargs)

        if fields != None:
            for key, value in fields.items():
                embed.add_field(name=key, value=value, inline=inline)
        
        if author != None:
            embed.set_author(name=f'{author.display_name}#{author.discriminator}', icon_url=author.avatar_url)
            footer_prefix = f'ID: {author.id} • '
        
        if image != None:
            embed.set_image(image)
        
        if thumbnail != None:
            embed.set_thumbnail(thumbnail)

        timestamp = timestamp.utcnow() if isinstance(timestamp, datetime) else datetime.utcnow()
        embed.set_footer(text=footer_prefix + timestamp.strftime('%Y-%m-%d %H:%M:%S') + ' (UTC+0)')
        
        return embed