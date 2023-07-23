from decouple import config

class Env:
    BOT_TOKEN = config('BOT_TOKEN')
    MONGO_URL = config('MONGO_URL')