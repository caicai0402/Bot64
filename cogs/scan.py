import sys
from discord import Message, RawReactionActionEvent
from discord.utils import get
from discord.ext.commands import Cog, Bot, Context, CommandError, group, guild_only, has_guild_permissions

from libs.check import Check
from libs.utils import Utils
from libs.flag import MessageFlag, PenaltyPolicyFlag
from libs.scanner import Scanner
from libs.database import Database
from libs.emoji import EmojiHelper
from libs.logger import MessageLogger
from libs.penalty import PenaltyAction
class Scan(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.bot_category = None
        self.bot_channel = None
        self.db = Database()
        self.scanner = Scanner()
        self.utils = Utils(bot=self.bot)
        self.logger = MessageLogger(bot=self.bot)
        self.penalty_action = PenaltyAction(bot=self.bot)
    
    '''Deal with every guild messages'''

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        # await self.createBotChannels(message=message)

        if Check.is_self_message(self_id=self.bot.user.id, message=message) or Check.is_dm_message(message=message):
            return None
        
        message_flag = self.scanner.scan(message=message)
        print(message_flag) # debug
        if message_flag == MessageFlag.Safe:
           return None
        
        await self.penalty_action.handle_penalty(message=message, message_flag=message_flag)
    
    '''Administrators can take penalty actions manually'''

    @Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent) -> None:
        # Check if the reaction is added in a guild, and not by the bot itself.
        if payload.event_type != 'REACTION_ADD' or payload.guild_id == None or payload.user_id == self.bot.user.id:
            return None

        # Get log channel
        log_channel_id = self.db.get_log_channel_id(guild_id=payload.guild_id)
        log_channel = None if log_channel_id == None else await self.utils.fetch_text_channel(channel_id=log_channel_id)

        # Trigger action only when the added reaction is in the logs channel AND the message is an embed.
        if log_channel == None or payload.channel_id != log_channel_id:
            return None
        log_message = await log_channel.fetch_message(payload.message_id)
        if len(log_message.embeds) == 0:
            return None

        # Check if the reaction is added by an administrator.
        admin = await self.utils.fetch_guild_member(guild=log_channel.guild, member_id=payload.user_id)
        if admin == None or not admin.permissions_in(channel=log_channel).administrator:
            return None
        
        # Check if the reaction maps to a valid penalty action.
        penalty_action = EmojiHelper.get_penalty_actions(emoji=payload.emoji)
        if penalty_action == None:
            return None
        
        try:
            member_id = log_message.embeds[0].footer.text.split(' ')[1]
            reason = 'Execute by admin'
            penalty_func = self.penalty_action.get_penalty_func(policy=penalty_action)
            await penalty_func(guild=log_channel.guild, member_id=member_id, log_channel_id=log_channel_id, reason=reason)
        except:
           await self.logger.log_message(channel_id=log_channel_id, content='Error: failed to take the penalty action.')
        
        await EmojiHelper.remove_penalty_actions(message=log_message, member=self.bot.user)
        await log_message.add_reaction('👌')

    '''Bot commands'''
    
    @group()
    @guild_only()
    @has_guild_permissions(administrator=True)
    async def config(self, ctx: Context) -> None:
        '''[Bot64 configurations]'''

        if ctx.invoked_subcommand == None:
            await ctx.send_help(ctx.command)

    @config.command()
    async def show(self, ctx: Context) -> None:
        '''[Shows Bot64 scanner configurations in this guild]'''

        guild_id = ctx.guild.id
        guild_config = self.db.get_guild_config(guild_id=guild_id)
        
        log_channel_id = guild_config['log_channel_id']
        mute_role_id = guild_config['mute_role_id']
        suspicious_policy = guild_config['suspicious_policy']
        malicious_policy = guild_config['malicious_policy']

        guild_config['log_channel'] = f'<#{log_channel_id}>' if log_channel_id != None else None
        guild_config['mute_role'] = f'<@&{mute_role_id}>' if mute_role_id != None else None
        guild_config['suspicious_policy'] = suspicious_policy.name
        guild_config['malicious_policy'] = malicious_policy.name
        
        del guild_config['_id']
        del guild_config['log_channel_id']
        del guild_config['mute_role_id']

        embed = self.utils.create_embed(title='Guild Config', color='random', fields=guild_config, author=ctx.author, inline=False)
        await ctx.send(embed=embed)
    
    @config.command()
    async def log(self, ctx: Context, channel_id: str=None) -> None:
        '''<channel_id> [Sets log channel]'''

        if channel_id == None:
            await ctx.send_help(ctx.command)
            return
        elif channel_id == 'None':
            channel_id = None
        elif not Check.is_integer(channel_id):
            await ctx.send('`channel_id` must be an integer (without sign) or \'None\'.')
            return
        else:
            channel_id = int(channel_id)
            channel = await self.utils.fetch_text_channel(channel_id=channel_id)
            if channel == None:
                await ctx.send('The channel is not a valid text channel.')
                return None
            elif channel.guild.id != ctx.guild.id:
                await ctx.send('The text channel is not in this guild.')
                return None
        
        self.db.set_log_channel_id(guild_id=ctx.guild.id, log_channel_id=channel_id)
        await self.show(ctx)
    
    @config.command()
    async def mute(self, ctx: Context, role_id: str=None) -> None:
        '''<role_id> [Sets mute role]'''

        if role_id == None:
            await ctx.send_help(ctx.command)
            return None
        elif role_id == 'None':
            role_id = None
        elif not Check.is_integer(role_id):
            await ctx.send('`role_id` must be an integer (without sign) or \'None\'.')
            return None
        else:
            role_id = int(role_id)
            role = await self.utils.fetch_guild_role(guild=ctx.guild, role_id=role_id)
            if role == None:
                await ctx.send('The role is not a valid role in this guild.')
                return None
        
        self.db.set_mute_role_id(guild_id=ctx.guild.id, mute_role_id=role_id)
        await self.show(ctx)
    
    async def __set_policy(self, ctx: Context, message_flag: MessageFlag, policy: str=None) -> None:
        if policy == None or not Check.is_penalty_policy(policy):
            await ctx.send_help(ctx.command)
            policies_str = ', '.join([f"'{flag.name}'" for flag in PenaltyPolicyFlag])
            await ctx.send('`policy` must be in ' + policies_str)
            return None
        
        policy = PenaltyPolicyFlag[policy]
        guild_id = ctx.guild.id
        if message_flag == MessageFlag.Suspicious:
            self.db.set_suspicious_policy(guild_id=guild_id, suspicious_policy=policy)
        elif message_flag == MessageFlag.Malicious:
            self.db.set_malicious_policy(guild_id=guild_id, malicious_policy=policy)
        else:
            raise NotImplementedError('Internal error occurred.')
        await self.show(ctx)

    @config.command()
    async def suspicious(self, ctx: Context, policy: str=None) -> None:
        '''<policy> [Sets suspicious policy]'''

        await self.__set_policy(ctx=ctx, message_flag=MessageFlag.Suspicious, policy=policy)
    
    @config.command()
    async def malicious(self, ctx: Context, policy: str=None) -> None:
        '''<policy> [Sets malicious policy]'''

        await self.__set_policy(ctx=ctx, message_flag=MessageFlag.Malicious, policy=policy)

    @config.error
    @log.error
    @mute.error
    @suspicious.error
    @malicious.error
    async def config_error(self, ctx: Context, error: CommandError):
        exception = error.original
        print(exception, file=sys.stderr)
        await ctx.send(f'An error occurred:\n```{str(exception)}```')

def setup(bot: Bot) -> None:
    bot.add_cog(Scan(bot))