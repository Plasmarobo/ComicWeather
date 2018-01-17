#!/usr/bin/env python
"""A simple weather clock"""

import ConfigParser
import json
import random
import sys
import time
import urllib2
from datetime import date, datetime
from os import listdir
from os.path import isfile,join
import re
import socket
import pygame
import ptext

class WeatherAPI(object):
  """A class that reads weather info and converts to tags"""

  def __init__(zipcode):
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

  def get_weather:
    req = urllib2.urlopen("https://api.openweathermap.org/data/2.5/weather?zip=" + self.zipcode + ",us")
    json_str = req.read()
    req.close()
    weather = json.loads(json_str)["weather"]
    code = re.search('([0-9]+)',weather["icon"]).group(0)
    if weather_codes.contains_key(code)
      return weather_codes[code]
    else
      return "clear"

  def get_random:
    return random.sample(weather_codes.values())

class Seasons(object):
  """A class that determines the season based on the current system date"""

  def __init__:
    self.seasons = [
      ('winter', (date(Y,  1,  1),  date(Y,  3, 20))),
      ('spring', (date(Y,  3, 21),  date(Y,  6, 20))),
      ('summer', (date(Y,  6, 21),  date(Y,  9, 22))),
      ('fall',   (date(Y,  9, 23),  date(Y, 12, 20))),
      ('winter', (date(Y, 12, 21),  date(Y, 12, 31)))
    ]
    self.Y = 2000
  
  def get_season:
    if isinstance(date.now(), datetime):
      now = now.date()
    now = now.replace(year=self.Y)
    return next(season for season, (start, end) in self.seasons
        if start <= now <= end

class Location(object):
  """A class that gets the location based on IP address"""
  
  def get_zipcode:
    req = urllib2.urlopen('http://freegeoip.net/json/')
    json_str = req.read()
    req.close()
    location = json.loads(json_str)
    return location['zipcode']

class ImagePicker(object):
  """A class that selects an image based on a tag list"""
  
  def __init__(directory):
    #Underscore separate values with at least 1 tag and an index
    self.images = []
    for f in listdir(directory):
      self.add_entry(f)

  def add_entry(filename):
    tags = os.path.splitext(filename)[0].split("_")
    entry = {"file" : filename, "tags": tags }
    self.images.push(entry)
    
  def get_candidates(wanted_tags):
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
        candidates.push(image)
    candiates = [x for x in candiates if x["score"] >= best_score-1]
    return candiates

  def get_file(wanted_tags):
    return random.sample(self.get_candidates(wanted_tags))

class ComicWeather(object):
  """A class to convert from weather to image"""
  SEC_TO_MSEC = 1000

  def __init__(config_file):
    config = ConfigParser.SafeConfigParser().read(config_file)
    if not config:
      print("Malformed or Nonexistant config file {}".format(config_file))
      sys.exit(1)

    dns = dict(config.items('dns'))
    dirs = dict(config.items('directories'))
    misc = dict(config.items('misc'))
    renderer = dict(config.items('renderer')) 

    self.dns_host = dns['host']
    self.dns_port = dns['port']

    self.image_directory = dirs['images']
    self.configure_wifi_script = dirs['config_wifi_script']

    self.night_start = misc['night_mode_start']
    self.night_end = misc['night_mode_end']
    self.night_mode = False
    self.zip = misc['zip']
    self.check_interval = misc['check_interval'] * SEC_TO_MSEC

    self.width = renderer['width']
    self.height = renderer['height']
    self.backlight_gpio = renderer['backlight_gpio']

    self.online = self.check_wifi()
    if not self.online:
      self.enter_setup_mode()
    self.weather = WeatherAPI()
    self.season = Seasons()
    self.location = Location()
    self.images = ImagePicker(self.image_directory)
    self.current_image = Actor
    pygame.init()

    self.screen = pygame.display.set_mode((self.width, self.height))
    self.timer = pygame.time.get_ticks()
    self.font = pygame.font.SysFont(None, 28)

  def update::
    if check_interval < (pygame.time.get_ticks() - self.timer):
      self.timer = pygame.time.get_ticks()  
      try:
        zip = self.location.get_location()
      except Exception as ex:
        zip = self.zip
      try:
        self.weather_tag = self.weather.get_weather(zip)
      except Exception as ex:
        self.weather_tag = self.weather.get_random()
        self.season = self.season.get_season(date.now())
        self.current_image = pygame.image.load(self.images.get_file([self.weather, self.season]))

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        sys.exit(0)
      elif event.type == pygame.MOUSEBUTTONDOWN:
        x, y = event.pos
        self.handle_touch(x, y)
    self.render()

  def check_wifi:
    try:
      socket.setdefaulttimeout(1)
      socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((self.dns_host, self.dns_port))
      return True
    except Exception as ex:
      pass
    return False

  def enter_setup_mode:
    # Call an external script to setup wifi config
    os.system(self.configure_wifi_script)

  def is_night:
    now = datetime.datetime.now()
    return now.hour > self.night_start or now.hour < self.night_end

  def set_night_mode(on):
    if on:
      # Disable the back light
      self.night_mode = True
    else:
      # Enable the back light
      self.night_mode = False
      
  def render:
    if self.is_night and not self.night_mode:
      self.set_night_mode(True)
    elif not self.is_night and self.night_mode:
      self.set_night_mode(False)
      # Clear screen
      self.screen.fill(255,255,255)
      # Render Image
      rect = self.current_image.get_rect()
      self.screen.blit(self.current_image, rect)
      # Render Time + Info
      txt = 'TEST 12:34'
      off_x = 20
      off_y = 20
      ptext.draw(txt, (off_x, off_y), owidth=1., ocolor=(0,0,0), color=(255,255,255), angle=90)
      # Render warning if we're offline
      if not self.online:
        # Wait
    pygame.display.flip()

  def handle_touch(x,y):
    # For future use
    return

def main():
  if len(sys.argv) != 2:
    print("Usage: {} CONFIG_FILE".format(sys.argv[0]))
    print()
    sys.exit(1)
  engine = ComicWeather(sys.argv[1])





