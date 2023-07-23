from typing import Optional
from discord import Message, Emoji
from discord.abc import Snowflake

from libs.flag import PenaltyPolicyFlag

class EmojiHelper:
    penalty_actions = {
        '✅': PenaltyPolicyFlag.Ignore,
        '🔇': PenaltyPolicyFlag.Mute,
        '🦵': PenaltyPolicyFlag.Kick,
        '🚫': PenaltyPolicyFlag.Ban,
    }

    @staticmethod
    async def add_penalty_actions(message: Message) -> None:
        for emoji in EmojiHelper.penalty_actions.keys():
            await message.add_reaction(emoji=emoji)
    
    @staticmethod
    async def remove_penalty_actions(message: Message, member: Snowflake) -> None:
        for emoji in EmojiHelper.penalty_actions.keys():
            await message.remove_reaction(emoji=emoji, member=member)
    
    @staticmethod
    def get_penalty_actions(emoji: Emoji) -> Optional[PenaltyPolicyFlag]:
        if emoji.name in EmojiHelper.penalty_actions:
            return EmojiHelper.penalty_actions[emoji.name]
        return None