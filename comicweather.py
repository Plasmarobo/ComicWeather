#!/usr/bin/env python
"""A simple weather clock"""

import configparser
import json
import random
import sys
import urllib.request
from datetime import date, datetime
from os import listdir, path, system
import re
import socket
import pygame
import ptext
import RPi.GPIO as GPIO

class WeatherAPI(object):
    """A class that reads weather info and converts to tags"""

    def __init__(self, zipcode):
        self.zipcode = zipcode
        self.weather_codes = {
            "01": "sunny",
            "02": "partlycloudy",
            "03": "cloudy",
            "04": "cloudy",
            "09": "rain",
            "10": "rain",
            "11": "rain",
            "13": "snow",
            "50": "mist"
        }

    def get_weather(self):
        req = urllib.request.urlopen(
            "https://api.openweathermap.org/data/2.5/weather?zip=" +
            self.zipcode +
            ",us")
        json_str = req.read()
        req.close()
        weather = json.loads(json_str)["weather"]
        code = re.search('([0-9]+)', weather["icon"]).group(0)
        if code in self.weather_codes:
            return self.weather_codes[code]
        else:
            return "clear"

    def get_random(self):
        return random.sample(list(self.weather_codes.values()), 1)

    def set_zipcode(self, _zip):
        self.zipcode = _zip

class Seasons(object):
    """A class that determines the season based on the current system date"""

    def __init__(self):
        self.Y = 2000
        self.seasons = [
            ('winter', (date(self.Y,  1,  1), date(self.Y,  3, 20))),
            ('spring', (date(self.Y,  3, 21), date(self.Y,  6, 20))),
            ('summer', (date(self.Y,  6, 21), date(self.Y,  9, 22))),
            ('fall', (date(self.Y,  9, 23), date(self.Y, 12, 20))),
            ('winter', (date(self.Y, 12, 21), date(self.Y, 12, 31)))
        ]
    
    def get_season(self):
        now = date.today()
        now = now.replace(year=self.Y)
        return next(season for season, (start, end) in self.seasons if start <= now <= end)

class Locations(object):
    """A class that gets the location based on IP address"""

    def __init__(self, _zip):
        self.backup_zip = _zip
    
    def get_zipcode(self):
        try:
            req = urllib.request.urlopen('http://freegeoip.net/json/')
            json_str = req.read()
            req.close()
            location = json.loads(json_str)
            return location['zipcode']
        except:
            return self.backup_zip

class ImagePicker(object):
    """A class that selects an image based on a tag list"""
    
    def __init__(self, directory):
        #Underscore separate values with at least 1 tag and an index
        self.images = []
        for f in listdir(directory):
            self.add_entry(f)

    def add_entry(self, filename):
        tags = path.splitext(filename)[0].split("_")
        tags = tags[:-1]
        entry = {"file" : filename, "tags": tags}
        self.images.append(entry)

    def get_candidates(self, wanted_tags):
        candidates = []
        best_score = 0
        for image in self.images:
            image["score"] = 0
            for tag in image["tags"]:
                if tag in wanted_tags:
                    image["score"] += 1
                if image["score"] > best_score:
                    best_score = image["score"]

            if image["score"] > 0:
                candidates.append(image)
        candidates = [x for x in candidates if x["score"] >= best_score-1]
        return candidates

    def get_file(self, wanted_tags):
        return random.sample(self.get_candidates(wanted_tags), 1)[0]['file']

    def get_random(self):
        return random.sample(self.images, 1)[0]['file']

class ComicWeather(object):
    """A class to convert from weather to image"""
    SEC_TO_MSEC = 1000

    def __init__(self, config_file):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)

        config = configparser.SafeConfigParser()
        config.read(config_file)
        if not config:
            print("Malformed or Nonexistant config file {}".format(config_file))
            sys.exit(1)
            self.finished = True

        self.dns_host = config.get('dns', 'host')
        self.dns_port = int(config.get('dns', 'port'))

        self.image_directory = config.get('directories', 'images')
        self.configure_wifi_script = config.get('directories', 'wifi_setup_script')

        self.night_start = datetime.strptime(config.get('misc', 'night_mode_start'), "%H:%M")
        self.night_end = datetime.strptime(config.get('misc', 'night_mode_end'), "%H:%M")
        self.night_mode = False
        self.zip = config.get('misc', 'zip')
        self.check_interval = int(config.get('misc', 'check_interval_milliseconds')) * self.SEC_TO_MSEC
        
        self.text_offset = int(config.get('renderer', 'text_offset'))
        self.width = int(config.get('renderer', 'width'))
        self.height = int(config.get('renderer', 'height'))
        self.backlight_gpio = int(config.get('renderer', 'backlight_gpio'))

        GPIO.setup(self.backlight_gpio, GPIO.OUT)

        self.online = self.check_wifi()

        self.location = Locations(self.zip)
        self.weather = WeatherAPI(self.location.get_zipcode())
        self.season = Seasons()
        self.images = ImagePicker(self.image_directory)
        self.update_image()
        pygame.init()

        self.screen = pygame.display.set_mode((self.width, self.height))
        self.timer = pygame.time.get_ticks()
        self.font = pygame.font.SysFont(None, 28)
        self.wifi_symbol = pygame.transform.rotate(pygame.image.load("wifi-setup.png"), 90)
        self.finished = False

    def update_location(self):
        try:
            self.zip = self.location.get_zipcode()
        except:
            pass
        self.weather.set_zipcode(self.location.get_zipcode())

    def update_weather(self):
        try:
            self.weather_tag = self.weather.get_weather()
        except:
            self.weather_tag = self.weather.get_random()

    def update_image(self):
        self.timer = pygame.time.get_ticks()
        self.update_location()
        self.update_weather()
        self.current_image = pygame.image.load(self.image_directory + 
            self.images.get_file([
                self.weather_tag,
                self.season.get_season()
            ]))

    def update(self):
        if self.check_interval < (pygame.time.get_ticks() - self.timer):
            self.update_image()
            self.online = self.check_wifi()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.finished = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                (x, y) = event.pos
                self.handle_touch(x, y)
        self.render()

    def check_wifi(self):
        try:
            socket.setdefaulttimeout(1)
            socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            ).connect((
                self.dns_host,
                self.dns_port
            ))
            return True
        except Exception as exp:
            print(exp.message)
            pass
        return False

    def set_backlight(self, on):
        GPIO.output(self.backlight_gpio, GPIO.HIGHT if on else GPIO.LOW)

    def enter_setup_mode(self):
        # Call an external script to setup wifi config
        system(self.configure_wifi_script)

    def is_night(self):
        current_hour = datetime.now().hour
        current_minute = datetime.now().minute
        
        return ((current_hour > self.night_start.hour and
                current_minute > self.night_start.minute) or 
                (current_hour < self.night_end.hour and
                current_minute < self.night_end.minute))

    def set_night_mode(self, on):
        if on:
            self.night_mode = True
        else:
            # Enable the back light
            self.night_mode = False
            self.set_backlight(on)
        
    def render(self):
        if self.is_night and not self.night_mode:
            self.set_night_mode(True)
        elif not self.is_night and self.night_mode:
            self.set_night_mode(False)
        # Clear screen
        self.screen.fill((255,255,255))
        # Render Image
        rect = self.current_image.get_rect()
        self.screen.blit(self.current_image, rect)
        # Render Time + Info
        txt = datetime.strftime(datetime.now(), "%H:%M")
        ptext.draw(txt, centery=(self.height/2)+55, left=self.text_offset, owidth=0.2, ocolor=(0,0,0), color=(255,255,255), angle=90, fontsize=72)
        # Render warning if we're offline
        r = self.wifi_symbol.get_rect()
        if not self.online:
            self.screen.blit(self.wifi_symbol, (self.width-r.width,(self.height/2)-(r.height/2) ))
            # Wait
        pygame.display.flip()

    def handle_touch(self, x, y):
        r = self.wifi_symbol.get_rect()
        if r.top <= y and (r.top + r.height) >= y:
            if r.left <= x and (r.left + r.width) >= x:
                self.enter_setup_mode()
        self.update_image()

def main():
    print("Starting...")
    if len(sys.argv) != 2:
        print("Usage: {} CONFIG_FILE".format(sys.argv[0]))
        print()
        sys.exit(1)
    engine = ComicWeather(sys.argv[1])
    while not engine.finished:
        engine.update()
        engine.render()
    sys.exit(0)

main()
