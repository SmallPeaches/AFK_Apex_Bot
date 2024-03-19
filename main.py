import logging
import os
import sys
import yaml
from datetime import datetime
from logging import handlers
from bot_functions import ApexBot
from time import sleep
from psutil import process_iter


def launch_bot(config):
    apex_bot = ApexBot(config['resolution'])
    while True:
        if "r5apex.exe" in [p.name() for p in process_iter()]:
            interact = config['interact_key']
            tactical = config['tactical_key']
            apex_bot.kd_lowering(interact_key=interact.lower(), tactical_key=tactical.lower())
        else:
            logging.info("Apex is not running.")
        sleep(5)

if __name__ == "__main__":
    config = yaml.safe_load(open("config.yaml"))
    logging.getLogger().setLevel(logging.INFO)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO) 
    console_handler.setFormatter(logging.Formatter("[%(asctime)s][%(levelname)s]: %(message)s"))
    
    os.makedirs('logs',exist_ok=True)
    logname = f'logs/apexbot-{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.log'
    file_handler = logging.FileHandler(logname, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter("[%(asctime)s][%(levelname)s]: %(message)s"))
    
    logging.getLogger().addHandler(console_handler)
    logging.getLogger().addHandler(file_handler)
    
    launch_bot(config)