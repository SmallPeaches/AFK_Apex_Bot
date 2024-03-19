import time
import pyautogui
import pydirectinput
import pyscreeze
import logging
from time import sleep
from random import randint
from psutil import process_iter

from assetsmgr import AssetsManager

cnt = 0

def locateOnScreen(image, minSearchTime=0, **kwargs):
    """TODO - rewrite this
    minSearchTime - amount of time in seconds to repeat taking
    screenshots and trying to locate a match.  The default of 0 performs
    a single search.
    """
    start = time.time()
    while True:
        try:
            # the locateAll() function must handle cropping to return accurate coordinates,
            # so don't pass a region here.
            screenshotIm = pyscreeze.screenshot(region=None)
            global cnt
            # screenshotIm.save(f'logs/debug-{cnt}.png')
            cnt += 1
            retVal = pyscreeze.locate(image, screenshotIm, **kwargs)
            try:
                screenshotIm.fp.close()
            except AttributeError:
                # Screenshots on Windows won't have an fp since they came from
                # ImageGrab, not a file. Screenshots on Linux will have fp set
                # to None since the file has been unlinked
                pass
            if retVal or time.time() - start > minSearchTime:
                return retVal
        except pyscreeze.ImageNotFoundException:
            return None

class ApexBot:
    def __init__(self, resolution):
        self.in_game = False
        self.assets = AssetsManager('Game Assets', source_resolution='HD', target_resolution=resolution)
        self.res_w, self.res_h = [int(x) for x in resolution.split('x')]
        self.resolution = resolution
        self.scale_w, self.scale_h = self.res_w/1920, self.res_h/1080
        self.tries_to_find_fill_button = 0

    def xp_grinding(self):
        # CHECKS IF APEX IS CURRENTLY RUNNING
        if "r5apex.exe" not in [p.name() for p in process_iter()]:
            pass
        # STOPS PLAYER FROM BEING KICKED FOR AFKING BY JUMPING
        elif locateOnScreen(f"Game Assets/in_game_constant{self.resolution}.png", confidence=.8) is not None:
            self.in_game = True
            pydirectinput.press("space")
            sleep(randint(0, 10))
        # STARTS QUEUING
        elif locateOnScreen(f"Game Assets/ready_button{self.resolution}.png", confidence=.8) is not None:
            self.queue_into_game()
            self.in_game = False
        # GOES FROM DEATH SCREEN TO HOME SCREEN
        elif locateOnScreen(f"Game Assets/squad_eliminated_constant{self.resolution}.png", confidence=.8) is not None or locateOnScreen(f"Game Assets/leave_match_constant{self.resolution}.png", confidence=.8) is not None:
            self.go_to_lobby()
            self.in_game = False
        # CLICKS THE CONTINUE BUTTON THAT APPEARS WHEN APEX IS FIRST LAUNCHED
        elif locateOnScreen(f"Game Assets/continue_constant{self.resolution}.png", confidence=.8) is not None:
            pydirectinput.click()
            self.in_game = False
        # PRESSES ESCAPE WHEN A POPUP IS ON SCREEN
        elif locateOnScreen(f"Game Assets/escape{self.resolution}.png", confidence=.8) is not None:
            pydirectinput.press("escape")
            self.in_game = False
        # GETS USER BACK INTO THE GAME WHEN AN ERROR HAPPENS E.G. BEING DISCONNECTED
        elif locateOnScreen(f"Game Assets/continue_error{self.resolution}.png", confidence=.8) is not None or locateOnScreen(f"Game Assets/continue_error2_{self.resolution}.png", confidence=.8):
            pydirectinput.press("escape")
            self.in_game = False
        else:
            self.in_game = False

    def kd_lowering(self, interact_key, tactical_key):
        # CHECKS IF APEX IS CURRENTLY RUNNING
        # if "r5apex.exe" not in [p.name() for p in process_iter()]:
        #     pass

        # STOPS PLAYER FROM BEING KICKED FOR AFKING BY JUMPING AND USES THEIR TACTICAL TO MAKE THEM MORE VISIBLE
        if locateOnScreen(self.assets.get_asset_path('in_game_constant'), confidence=.8) is not None:
            logging.info("In game, press space and tactical key.")
            self.in_game = True
            pydirectinput.press("w", presses=1)
            sleep(randint(1,10))
            pydirectinput.press(tactical_key)
        
        # STARTS QUEUING
        elif locateOnScreen(self.assets.get_asset_path('ready_button'), confidence=.8) is not None:
            self.queue_into_game()
            self.in_game = False
        
        # TRIES TO SELECT HORIZON, THEN GIBBY
        elif locateOnScreen(self.assets.get_asset_path('gibraltar'), confidence=.8) is not None:
            try:
                button_cords = pyautogui.center(locateOnScreen(self.assets.get_asset_path('gibraltar'), confidence=.8))
                pydirectinput.click(button_cords.x, button_cords.y)
                logging.info("Gibraltar selected.")
            except:
                logging.info("Gibraltar cords were not found, skip.")
        
        # DROPS THE USER FROM THE LAUNCH SHIP IN AN AREA USUALLY DENSE WITH PLAYERS
        elif locateOnScreen(self.assets.get_asset_path('launch'), confidence=.7) is not None:
            # sleep(3)
            logging.info('Start launch.')
            pydirectinput.press(interact_key)
            pydirectinput.moveTo(990, 985, 0.5)
            pydirectinput.keyDown("w")
            sleep(15)
            pydirectinput.keyUp("w")
        
        # CLICKS THE CONTINUE BUTTON THAT APPEARS WHEN APEX IS FIRST LAUNCHED
        elif locateOnScreen(self.assets.get_asset_path('continue_constant'), confidence=.8) is not None:
            logging.info("Apex first launched, click continue.")
            pydirectinput.click()
            self.in_game = False
        
        # PRESSES ESCAPE WHEN A POPUP IS ON SCREEN
        elif locateOnScreen(self.assets.get_asset_path("escape"), confidence=.8) is not None:
            logging.info('Detect a popup, press escape.')
            pydirectinput.press("escape")
            self.in_game = False
        
        # GETS USER BACK INTO THE GAME WHEN AN ERROR HAPPENS E.G. BEING DISCONNECTED
        elif locateOnScreen(self.assets.get_asset_path("continue_error"), confidence=.8) is not None\
             or locateOnScreen(self.assets.get_asset_path("continue_error2_"), confidence=.8):
            logging.info('Error page detected, press escape.')
            pydirectinput.press("escape")
            self.in_game = False
        
        # GOES FROM DEATH SCREEN TO HOME SCREEN
        elif locateOnScreen(self.assets.get_asset_path('squad_eliminated_constant'), confidence=.4) is not None \
            or locateOnScreen(self.assets.get_asset_path('leave_match_constant'), confidence=.8) is not None:
            self.go_to_lobby()
            self.in_game = False
        
        else:
            logging.info("No action matched.")
            self.in_game = False

    # QUEUES FOR A MATCH FROM THE HOME SCREEN
    def queue_into_game(self):
        try:
            logging.info("Trying to queue into game")
            if locateOnScreen(self.assets.get_asset_path("fill_teammates"), confidence=.8) is not None:
                logging.info("Found fill teammates, disable.")
                self.tries_to_find_fill_button = 0
                fill_button_cords = pyautogui.center(
                    locateOnScreen(self.assets.get_asset_path("fill_teammates"), confidence=.8))
                pydirectinput.click(fill_button_cords.x, fill_button_cords.y)
                sleep(5)
                logging.info("Matchmaking.")
                ready_button_cords = pyautogui.center(
                    locateOnScreen(self.assets.get_asset_path('ready_button'), confidence=.8))
                pydirectinput.click(ready_button_cords.x, ready_button_cords.y)
            else:
                logging.warn("Fill teammates not found, try again.")
                self.tries_to_find_fill_button += 1
                sleep(1)

            if self.tries_to_find_fill_button >= 3:
                self.tries_to_find_fill_button = 0
                logging.warn("Fill teammates not found, force matchmaking.")
                # raise Exception("Fill button not found")
                ready_button_cords = pyautogui.center(
                    locateOnScreen(self.assets.get_asset_path('ready_button'), confidence=.8))
                pydirectinput.click(ready_button_cords.x, ready_button_cords.y)
        except:
            logging.error("Error in finding fill and or ready button and loading into game.")

    # ENTERS CLICKS AND KEYSTROKES IN CORRECT ORDER TO GO FROM THE DEATH SCREEN TO THE LOBBY
    def go_to_lobby(self):
        logging.info("Going to lobby.")
        pydirectinput.press("space")
        sleep(1)
        if locateOnScreen(self.assets.get_asset_path('yes_button'), confidence=.8) is not None:
            logging.info("Press yes button to confirm.")
            yes_button_cords = pyautogui.center(
                locateOnScreen(self.assets.get_asset_path('yes_button'), confidence=.8))
            pydirectinput.click(yes_button_cords.x, yes_button_cords.y)
        elif locateOnScreen(self.assets.get_asset_path('yes_button2_'), confidence=.8) is not None:
            logging.info("Press yes button to confirm.")
            yes_button_cords = pyautogui.center(
                locateOnScreen(self.assets.get_asset_path('yes_button2_'), confidence=.8))
            pydirectinput.click(yes_button_cords.x, yes_button_cords.y)
        else:
            logging.warn("Yes button not found.")
        sleep(7)
        # pydirectinput.click(850, 716)
        pydirectinput.press("space")
        sleep(2)
        pydirectinput.press("space")
        sleep(1)
        pydirectinput.press("space")
        sleep(1)
        pydirectinput.press("space")
