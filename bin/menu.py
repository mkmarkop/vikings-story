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

import pygame, urllib,sys

from pygame.locals import *
from gui 	   import *
from helpers       import *
from levels        import *
from states        import State
from descriptions  import ac

A1 = "No creeps allowed!\nThey'll have 10%\nmore health."
A2 = "2 creeps allowed\nto pass."
A3 = "4 creeps allowed\nto pass.\nThey'll have 10%\nless health."
ACH = Sheet("./data/image/menu/achievements.png")
APIC = {"TUT": ACH.get_at((60,59,59,58),True), \
        "WIZ": ACH.get_at((0,0,59,58),True), \
        "LUC": ACH.get_at((60,118,59,58),True), \
        "SAI": ACH.get_at((120,0,59,58),True), \
        "BUI": ACH.get_at((120,118,59,58),True), \
        "PER": ACH.get_at((120,59,59,58),True), \
        "INV": ACH.get_at((60,0,59,58),True), \
        "SHI": ACH.get_at((0,59,59,58),True), \
        "UNL": ACH.get_at((0,118,59,58),True)}
x = Sheet("./data/image/menu/story.png")
SIC = Sheet("./data/image/menu/status_icons.png")
TALE = [x.get_at((0,0,312,241),True), x.get_at((0,245,312,275),True), \
        x.get_at((0,527,312,292),True)]
TXT = ["  In Rogheim, a tiny\nfraction of rebellious\nwarriors separated\nfrom your clan. They\n\
began pillaging and\nwreaking havoc, and soon\nafter they've even\ndefiled Hel's temple.", \
"  As Hel saw their sinful\ndeeds, her eyes shone\nwith anger. Then she\ndecided to punish whole\n\
Rogheim. She raised an\narmy of various\nmonsters to purge\nthe land of the defilers.", \
"  Among many veterans,\nyou were chosen to\nlead the defense against\nthe raging army. The\n\
destiny of Rogheim\nnow lies in your hands."]

class Menu(State):

    def __init__(self, key, manager):
        State.__init__(self,key,manager)
        self.cursor = self.manager.cursor
        self.pon = 0
        self.menu = Master([0,0],1024,768,self.screen,self.cursor,"./data/font/carolingia.ttf")
        self.menu_background = load_image("./data/image/menu/menu.PNG")
        self.sbg = load_image("./data/image/menu/storyBG.PNG")
        self.boxes = []
        self.page = 0
        icons = Sheet("./data/image/menu/status_icons.png")
        credit_text = "Programming, design and graphics\nby Marko Pranjic a.k.a mkmgames.\n \
                       \nMusic is from Celestial Aeon Project;\nYou can find it and download \
it from\nhttp://www.mattipaalanen.com/\n \nFor more info or contact, \
please visit\nhttp//vikingsstory.sourceforge.net"
        Button(self.menu,[395,155],(0,0,0),None,62,"New Game",self.menu.switch,"diff")
        Button(self.menu,[395,222],(0,0,0),None,62,"Continue",self.manager.set_state,"map")
        Button(self.menu,[395,294],(0,0,0),None,62,"Achievements",self.menu.switch,"achievements")
        Button(self.menu,[294,110],(0,0,0),None,52,"Easy",self.difficulty,4, \
               ["diff", "inf1"], hovfun=self.hovinfo, hovarg=A3)
        Button(self.menu,[294,177],(0,0,0),None,52,"Normal",self.difficulty,2, \
               ["diff", "inf1"], hovfun=self.hovinfo, hovarg=A2)
        Button(self.menu,[294,244],(0,0,0),None,52,"Ragnarok",self.difficulty,0, \
               ["diff", "inf1"], hovfun=self.hovinfo, hovarg=A1)
        Button(self.menu,[395,366],(0,0,0),None,62,"Options",self.menu.switch,"options")
        Button(self.menu,[395,438],(0,0,0),None,62,"Credits",self.menu.switch,"credits")
        Button(self.menu,[395,510],(0,0,0),None,62,"Quit",exit,None)
        Button(self.menu,[273,630],(0,0,0),None,32,"Back",self.menu.switch,"default",["credits"])
        Button(self.menu,[273,630],(0,0,0),None,32,"Back",self.menu.switch,"default",["diff", "inf1"])
        Button(self.menu,[273,630],(0,0,0),None,32,"Back",self.menu.switch,"default",["options","okbox"])
        Button(self.menu,[273,630],(0,0,0),None,32,"Back",self.menu.switch,"default",["achievements", "inf"])
        Button(self.menu,[343,630],(0,0,0),None,32,"Apply",self.change_settings,None,["options","okbox"])
        self.pic = Image(self.menu,[523,112],TALE[0],["intro","intro1"])
        ImageButton(self.menu,[230,613],SIC.get_at((0,19,38,53),False),self.flip, -1, ["intro1"])
        ImageButton(self.menu,[790,613],SIC.get_at((38,19,38,53),False),self.flip, 1, ["intro","intro1"])
        Textbox(self.menu,[300,155],(0,0,0),None,28,credit_text,3,["credits"])
        self.story = Textbox(self.menu,[224,120],(0,0,0),None,28,TXT[0],3,["intro","intro1"])
        self.dt = Textbox(self.menu,[392,484],(0,0,0),None,24,"",3, \
                          ["inf"])
        self.achievements = {
        "TUT":ImageButton(self.menu,[392,211], ACH.get_at((0,177,59,58),True), self.potatoes, \
                    None, ["achievements", "inf"], hovfun=self.desc, hovarg="TUT"),
        "WIZ":ImageButton(self.menu,[492,211], ACH.get_at((0,177,59,58),True), self.potatoes, \
                    None, ["achievements", "inf"], hovfun=self.desc, hovarg="WIZ"),
        "SAI":ImageButton(self.menu,[592,211], ACH.get_at((0,177,59,58),True), self.potatoes, \
                    None, ["achievements", "inf"], hovfun=self.desc, hovarg="SAI"),
        "LUC":ImageButton(self.menu,[392,290], ACH.get_at((0,177,59,58),True), self.potatoes, \
                    None, ["achievements", "inf"], hovfun=self.desc, hovarg="LUC"),
        "SHI":ImageButton(self.menu,[492,290], ACH.get_at((0,177,59,58),True), self.potatoes, \
                    None, ["achievements", "inf"], hovfun=self.desc, hovarg="SHI"),
        "BUI":ImageButton(self.menu,[592,290], ACH.get_at((0,177,59,58),True), self.potatoes, \
                    None, ["achievements", "inf"], hovfun=self.desc, hovarg="BUI"),
        "PER":ImageButton(self.menu,[392,370], ACH.get_at((0,177,59,58),True), self.potatoes, \
                    None, ["achievements", "inf"], hovfun=self.desc, hovarg="PER"),
        "INV":ImageButton(self.menu,[492,370], ACH.get_at((0,177,59,58),True), self.potatoes, \
                    None, ["achievements", "inf"], hovfun=self.desc, hovarg="INV"),
        "UNL":ImageButton(self.menu,[592,370], ACH.get_at((0,177,59,58),True), self.potatoes, \
                    None, ["achievements", "inf"], hovfun=self.desc, hovarg="UNL")
        }
        self.fs = Checkbox(self.menu,[395,154],(0,0,0),None,32,"Fullscreen",(0,1),["options","okbox"], \
                           self.manager.config["fullscreen"])
        self.fps = Checkbox(self.menu,[395,194],(0,0,0),None,32,"Show FPS",(0,1),["options","okbox"], \
                           self.manager.config["fps"])
        Label(self.menu,[395,234],(0,0,0),None,31,"Music:",["options","okbox"])
        self.bs = Scroll(self.menu, [500,234],(0,0,0),None,32,["options","okbox"], \
                         self.manager.config["bsound"]*100)
        Label(self.menu,[395,274],(0,0,0),None,31,"Sound:",["options","okbox"])
        self.sfx = Scroll(self.menu, [500,274],(0,0,0),None,32,["options","okbox"], \
                         self.manager.config["sfx"]*100)
        OKBox(self.menu,(0,0,0),None,22, "You will need to restart\nthe game so changes could\nbe applied.",3,self.menu.switch,"options")
        self.df = Textbox(self.menu,[525,110],(0,0,0),None,32,"",3, \
                          ["inf1"])
        self.cid = None
        self.cid1 = None
        self.check_ach()

    def difficulty(self, n):
        self.pon = n
        self.menu.switch("intro")
        
    def hovinfo(self, terminate, id, text):
        if self.menu.state=="okbox" or self.menu.state=="yesnobox":
            self.cid1 = None
            return
        if terminate!=1:
            self.cid1 = id
            self.df.change(text)
            self.menu.switch("inf1")
        elif terminate==1 and self.cid1==id:
            self.menu.switch("diff")
            self.cid1 = None

    def desc(self, terminate, id, text):
        if self.menu.state=="okbox" or self.menu.state=="yesnobox":
            self.cid = None
            return
        if terminate!=1:
            self.cid = id
            self.dt.change(ac[text])
            self.menu.switch("inf")
        elif terminate==1 and self.cid==id:
            self.menu.switch("achievements")
            self.cid = None
            
    def flip(self, a):
        if self.page==2 and a>0:
            self.new_game()
        elif self.page<=2 or a<0:
            self.page += a
            if self.page==0:
                self.menu.switch("intro")
            else:
                self.menu.switch("intro1")
            self.pic.change(TALE[self.page])
            self.story.change(TXT[self.page])

    def new_game(self):
        self.manager.player["gold"] = 20
        self.manager.player["passed"] = ["None"]
        self.manager.player["score"] = [0]
        self.manager.player["g_lev"] = [0]
        self.manager.player["unlocked"] = ["AT","RM"]
        self.manager.player["achiv"] = ["None"]
        self.manager.player["wospells"] = 0
        self.manager.player["wotower"] = 0
        self.manager.player["shipdied"] = 0
        self.manager.player["lootcoll"] = 0
        self.manager.player["retries"] = 0
        self.manager.player["credied"] = 0
        self.manager.player["allowed"] = self.pon
        self.manager.player["needless"] = ['None']
        self.manager.player["bpoints"] = 0
        self.manager.player["powerup"] = 'None'
        self.manager.player.save()
        self.manager.player.reset()
        self.manager.set_state("map")

    def check_ach(self):
        for i in self.achievements:
            if i in self.manager.player["achiv"]:
                self.achievements[i].change(APIC[i])
        return

    def potatoes(self):
        return

    def change_settings(self):
        bs = self.bs.get_value()/100
        sfx = self.sfx.get_value()/100
        fs = self.fs.get_value()
        oldfs = self.manager.config["fullscreen"]

        if fs!=oldfs and self.menu.state!="okbox":
            self.menu.switch("okbox")

        self.manager.config["fullscreen"] = fs
        self.manager.config["bsound"] = bs
        self.manager.config["sfx"] = sfx
        self.manager.config["fps"] = self.fps.get_value()
        self.manager.config.save()
        self.manager.sound_manager.change_volume("background", bs)
        self.manager.sound_manager.change_volume("sound", sfx)

    def update(self):
        self.screen.fill((0,0,0))
        if not self.manager.sound_manager.current == "menu" and \
           not self.menu.state in ["intro","intro1"]:
            self.manager.sound_manager.change_music("menu")
        if self.manager.sound_manager.current != "intro" and \
               self.menu.state in ["intro","intro1"]:
           self.manager.sound_manager.change_music("intro")
        if not self.menu.state in ["intro", "intro1"]:
            self.screen.blit(self.menu_background,(0,0))
        else:
            self.screen.blit(self.sbg,(0,0))
        self.menu.update()
