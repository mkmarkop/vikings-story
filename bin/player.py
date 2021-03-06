# -*- coding: utf-8 -*-

############################################################################
#                                                                          #
#   Viking's Story: an open source tower defense game                      #
#   Copyright (C) 2010  Marko Pranjic                                      #
#                                                                          #
#   This program is free software: you can redistribute it and/or modify   #
#   it under the terms of the GNU General Public License as published by   #
#   the Free Software Foundation, either version 3 of the License, or      #
#   (at your option) any later version.                                    #
#                                                                          #
#   This program is distributed in the hope that it will be useful,        #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of         #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
#   GNU General Public License for more details.                           #
#                                                                          #
#   You should have received a copy of the GNU General Public License      #
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.  #
#                                                                          #
############################################################################

from UserDict import UserDict
from helpers  import DictFile


class Player(UserDict):

    def __init__(self, name):
        """
        Class which serves as a placeholder for
        player's data
        """
        UserDict.__init__(self)
        self.dict_file = DictFile(name)
        temp = self.dict_file.read()
        for key, value in temp.items():
            self[key] = value
        self.buying = False
        self.passed = 0
        self.killed = 0
        self.lpassed = 0
        self.newa = False
        self.lost = False
        self.passed = 0
        self.failed = 0
        self.collected = 0
        self.charges = 0
        self.hasscroll = 0
        self.tw = 0
        self.sp = 0
        self.paused = 1
        self["magicka"] = 0

    def debonus(self):
        self["powerup"] = 'None'

    def reset(self):
        self.buying = False
        self.passed = 0
        self.lpassed = False
        self.paused = 1
        self.killed = 0
        self.passed = 0
        self.charges = 0
        self.lost = False
        self.sp = 0
        self.tw = 0
        self.collected = 0
        self.hasscroll = 0
        self["retries"] += self.failed
        self.failed = 0
        self["magicka"] = 0

    def reward(self, prize, prizet):
        if prize == "gold":
            self["gold"]+=prizet
        else:
            pass

    def save(self):
        """
        Saves all changes made to the player
        dictionary (self)
        """
        self.dict_file.change(self)
        self.dict_file.write()

class Config(UserDict):

    def __init__(self):
        UserDict.__init__(self)
        self.dict_file = DictFile("./data/profiles/config.mkm")
        temp = self.dict_file.read()
        for key, value in temp.items():
            self[key] = value

    def save(self):
        self.dict_file.change(self)
        self.dict_file.write()
