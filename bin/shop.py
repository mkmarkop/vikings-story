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

import pygame, random

from gui           import *
from helpers       import *
from descriptions  import illist as il
from particles     import Butterfly, ABoat
from states        import State

it = Sheet("./data/image/menu/shopitems.png")
ITEMS = {"HAM": it.get_at((1,1,32,32),True), \
         "MJO": it.get_at((67,100,32,32),True), \
         "AND": it.get_at((1,100,32,32),True), \
         "PIP": it.get_at((1,34,32,32),True), \
         "ULL": it.get_at((34,1,32,32),True), \
         "LOK": it.get_at((100,1,32,32),True), \
         "TYR": it.get_at((34,34,32,32),True), \
         "MIM": it.get_at((67,1,32,32),True), \
         "JOT": it.get_at((34,100,32,32),True), \
         "DRA": it.get_at((100,100,32,32),True), \
         "GIA": it.get_at((100,34,32,32),True), \
         "GIF": it.get_at((67,67,32,32),True), \
         "BEO": it.get_at((1,67,32,32),True), \
         "HOR": it.get_at((34,67,32,32),True), \
         "WAT": it.get_at((67,34,32,32),True), \
         "BIR": it.get_at((100,67,32,32),True)}
SIC = Sheet("./data/image/menu/status_icons.png")
         
class Shop(State):

    def __init__(self, key, manager):
        State.__init__(self,key,manager)
        self.cursor = self.manager.cursor
        self.player = self.manager.player
        self.menu = Master([0,0],1024,768,self.screen,self.cursor,"./data/font/carolingia.ttf")
        self.menu_background = load_image("./data/image/menu/shop.png")
        self.shopl = load_image("./data/image/menu/shoplayer.png")
        self.blargh = False
        self.effects = pygame.sprite.Group()
        p1 = [[64, 640], [96, 640], [128, 640], [160, 640], [192, 640], \
               [96, 672], [128, 672], [160, 672], [192, 672], [256, 640], \
               [298, 640], [320, 640], [256, 672], [290, 672], [320, 672], \
               [352, 672]]
        p2 = [[672, 160], [704, 160], [736, 160], [758, 160], [640, 192], \
              [672, 192], [704, 192], [736, 192]]
        pat = [p1, p2]
        for i in range(12):
            self.effects.add(Butterfly(random.choice(pat)))
        self.effects.add(ABoat())
        self.rects = []
        for i in range(6):
            self.rects.append(pygame.Rect(58+74*i+288, 23+64, 59, 58))
        self.cid = None
        self.mix()

    def mix(self):
        self.menu.reset_widgets()
        k = ITEMS.keys()
        for i in range(6):
            a = random.choice(k)
            k.remove(a)
            tmp = ImageButton(self.menu, [10+33*i, 10], ITEMS[a], self.buy, a, \
                              ["default"], True, None, self.inf, a)
            tmp.rect.center = self.rects[i].center
        Label(self.menu, [79+288, 116+64], (255,255,255),None, 18, str(self.player["bpoints"]))
        ImageButton(self.menu, [79+288, 564], SIC.get_at((76,0,19,19), \
                    True), self.back) 
        self.price = Label(self.menu, [359, 116+64+20], (255,255,255),None, 18, '')
        self.info = Textbox(self.menu,[79+288,264],(255,255,255),None,22,"",3)
        self.ib = OKBox(self.menu,(0,0,0),None,22,"Lorem ipsum lorem. Lorem ipsum\n"*6+"",3,\
self.back)

    def inf(self, terminate, id, arg):
        if self.menu.state=="okbox":
            self.cid = None
            return
        if terminate!=1:
            self.cid = id
            self.info.change(il[arg][1])
            self.price.change("-"+str(il[arg][0]))
        elif terminate==1 and self.cid==id:
            self.cid = None
            self.info.change("")
            self.price.change("")

    def buy(self, name):
        if self.player["powerup"]!='None': return
        if self.player["bpoints"]>=il[name][0]:
            self.player["bpoints"] -= il[name][0]
            self.player["powerup"] = name
            self.player.save()
        self.call("You have bought a power-up.\nYou'll be returned to the map.")
  
    def back(self):
        self.menu.switch("default")
        if not self.blargh:
            self.manager.states["menu"].check_ach()
            self.manager.set_state("map")
        else:
            self.blargh = False

    def call(self, text):
        self.ib.change(text)
        self.menu.switch("okbox")

    def potatoes(self):
        self.menu.switch("default")
        self.back()

    def update(self):
        if self.manager.sound_manager.current != "shop":
            self.manager.sound_manager.change_music("shop")
        self.screen.fill((0,0,0))
        if self.player["powerup"]!='None' and self.menu.state!="okbox":
            self.call("You've already visited the shop!\nAfter a victorius battle, you\nmay visit us again.")
        self.screen.blit(self.menu_background,(0,0))
        self.effects.draw(self.screen)
        self.effects.update()
        self.screen.blit(self.shopl,(288,64))
        self.menu.update()
        if not "shop" in self.player["needless"] and self.menu.state!="okbox":
            self.blargh = True
            self.player["needless"].append("shop")
            self.call("Welcome to our shop! Here you\ncan exchange your Battle Points\nfor various power-ups. You get\n\
Battle Points for each star\nafter completing a level. Our\navailable goods will always vary.")
