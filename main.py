import sys, traceback
from discord.ext import commands

from libs.env import Env
from libs.database import Database

description = 'Bot 64'
command_prefix = 'bot64!'
startup_extensions = ['scan', 'routine']
database = Database(endpoint=Env.MONGO_URL)

bot = commands.Bot(command_prefix=command_prefix, description=description)

@bot.event
async def on_ready() -> None:
    print('Logged in as')
    print(f'username: {bot.user.name if bot.user != None else None}')
    print(f'id: {bot.user.id if bot.user != None else None}')
    print('-' * 40)
    load_extensions()
    print('-' * 40)

def load_extensions() -> None:
    for extension in startup_extensions:
        try:
            bot.load_extension(name=f'cogs.{extension}')
            print(f'Successfully loaded extension \'{extension}\'')
        except Exception as e:
            exc = f'{type(e).__name__}: {e}'
            print(f'Failed to load extension \'{extension}\'\n{exc}')

@bot.event
async def on_command_error(_, exception: commands.CommandError) -> None:
    if isinstance(exception, commands.CommandInvokeError):
        exception = exception.original
    try:
        raise exception
    except:
        error_msg = traceback.format_exc()
        print(error_msg, file=sys.stderr)

if __name__ == '__main__':
    bot.run(Env.BOT_TOKEN)