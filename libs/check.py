from discord import Message, DMChannel, TextChannel

from libs.flag import PenaltyPolicyFlag

class Check:
    @staticmethod
    def is_self_message(self_id: int, message: Message) -> bool:
        return self_id == message.author.id

    @staticmethod
    def is_dm_message(message: Message) -> bool:
        return isinstance(message.channel, DMChannel)

    @staticmethod
    def is_integer(value: str) -> bool:
        for c in value:
            if not c.isdigit():
                return False
        return True

    @staticmethod
    def is_penalty_policy(value: str) -> bool:
        return value in PenaltyPolicyFlag.__members__
