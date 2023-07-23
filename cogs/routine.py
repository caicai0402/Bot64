from discord.ext.commands import Cog, Bot
from discord.ext import tasks

from libs.phishing import Phishing

class Routine(Cog):
    fetch_interval = 86400

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.fish = Phishing()

    @tasks.loop(seconds=fetch_interval)
    async def auto_fetch(self):
        Phishing.fetch()

def setup(bot: Bot) -> None:
    bot.add_cog(Routine(bot))