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

import pygame

from gui           import *
from helpers       import *
from levels        import *
from states        import State

LEVICONS = Sheet("./data/image/menu/levcons.png")
SCORE = [LEVICONS.get_at((0,116,25,11), True), \
         LEVICONS.get_at((26,116,25,11), True), \
         LEVICONS.get_at((0,128,25,11), True)]

class World(State):

    def __init__(self, key, manager):
        State.__init__(self,key,manager)
        self.cursor = self.manager.cursor
        self.player = self.manager.player
        self.menu = Master([0,0],1024,768,self.screen,self.cursor,"./data/font/carolingia.ttf")
        self.menu_background = load_image("./data/image/menu/map.PNG")
        self.levels = [[Level("lv01.mkm"), [195, 542]],[Level("lv02.mkm"), [215,469]], \
[Level("lv03.mkm"), [177,402]], [Level("lv04.mkm"), [165, 331]], \
[Level("lv05.mkm"), [209, 281]], [Level("lv06.mkm"), [268, 210]], \
[Level("lv07.mkm"),[255,125]], [Level("lv08.mkm"),[372,199]], \
[Level("lv09.mkm"),[481,234]], [Level("lv10.mkm"),[547,266]], \
[Level("lv11.mkm"),[687,261]], [Level("lv12.mkm"),[720,149]], \
[Level("lv13.mkm"),[875,125]], [Level("lv14.mkm"),[871,201]], \
[Level("lv15.mkm"),[840,252]], [Level("lv16.mkm"),[818,291]], \
[Level("lv17.mkm"),[761,382]], [Level("lv18.mkm"),[631,429]], \
[Level("lv19.mkm"),[616,477]], [Level("lv20.mkm"),[579,519]], \
[Level("indian1.mkm"),[149,154]], [Level("indian2.mkm"),[152,106]], \
[Level("warrior1.mkm"),[356,235]]]
        self.prepared = False

    def potatoes(self):
        self.menu.switch("default")

    def do(self, level):
        self.manager.change_level(level)
        self.prepared = False
        self.manager.set_state("game")

    def undo(self):
        self.manager.states["menu"].menu.switch("default")
        self.manager.set_state("menu")

    def prepare(self):
        self.menu.reset_widgets()
        Button(self.menu,[165,638],(0,0,0),None,32,"Back", \
               self.undo, None, ["default", "okbox"])
        OKBox(self.menu,(255,255,255),None,32,"Achievement unlocked!\nCheck it out on the main menu.", \
              3, self.potatoes)

        temp = None
        
        for n in xrange(len(self.levels)):
            level = self.levels[n]
            ldata = level[0]
            pos = level[1]
            img = LEVICONS.get_at((0, 0, 25, 28))
            hovimg = LEVICONS.get_at((26, 0, 25, 28))
            ps = self.player["passed"]
            if ldata["req"] in ps and not \
               ldata["name"] in self.player["passed"]: 
                 if 'B' in ldata["name"]:
                     img = LEVICONS.get_at((0, 87, 25, 28))
                     hovimg = LEVICONS.get_at((26, 87, 25, 28))
                 temp = ImageButton(self.menu, pos, img, self.do, level[0], \
                            ["default", "okbox"], False, hovimg)

            elif ldata["name"] in ps:
                 img = LEVICONS.get_at((0, 29, 25, 28))
                 hovimg = LEVICONS.get_at((26, 29, 25, 28))
                 ImageButton(self.menu, pos, img, self.do, level[0], \
                            ["default", "okbox"], False, hovimg)
                 x = ps.index(ldata["name"])
                 sc = self.player["score"][x]
                 if not 'B' in ldata["name"]:
                     Image(self.menu, [pos[0],pos[1]+30], SCORE[sc])
                 elif 'BInd' in ldata["name"]:
                     Image(self.menu, [pos[0],pos[1]+30], SCORE[int(sc*2)])

        if temp!=None: temp.flash()
        
        if '2' in self.player["passed"]:
             img = LEVICONS.get_at((0, 58, 25, 28))
             hovimg = LEVICONS.get_at((26, 58, 25, 28))
             tmp = ImageButton(self.menu, [143,457], img, self.manager.set_state, "shop", \
                        ["default", "okbox"], False, hovimg)

        if self.player.newa and self.menu.state!="okbox":
            self.menu.switch("okbox")
            self.player.newa = False

        self.prepared = True

    def update(self):
        if not self.prepared:
            self.prepare()

        if not self.manager.sound_manager.current == "menu":
            self.manager.sound_manager.change_music("menu")

        self.screen.blit(self.menu_background,(0,0))
        self.menu.update()
