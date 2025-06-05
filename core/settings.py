import os
from environs import Env
from dataclasses import dataclass

@dataclass
class Bots:
    bot_token: str
    admin_id: id

@dataclass
class Settings:
    bots: Bots

def get_settings(path: str):
    absolute_path = os.path.join(os.getcwd(), path)
    print("Resolved path:", absolute_path)
    env = Env()
    env.read_env(absolute_path)
    return Settings(
        bots=Bots(
            bot_token=env.str('TOKEN'),
            admin_id=env.int('ADMIN_ID'),
        )
    )

settings = get_settings('core/configdata')
