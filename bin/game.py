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

from creeps        import *
from gui           import *
from helpers       import *
from towers        import *
from minis         import *
from spells        import *
from particles     import Weather, Butterfly
from states        import State
from descriptions  import descript as DESC
from descriptions  import illist   as DESC2
from pygame.locals import *

BUILDABLE = [[19,91,94,97],13]
STATICONS = Sheet("./data/image/menu/info_icons.png")
TYPES = [STATICONS.get_at((72,4,18,19),True), \
         STATICONS.get_at((91,4,18,19),True), \
         STATICONS.get_at((110,4,18,19),True)]
BUTTONS = Sheet("./data/image/menu/buttons.png")   
TEXT1 = "Welcome, brave warrior, to Viking's Story!\nTo begin, select the Arrow Tower and\nplace it anywhere near the path."
TEXT2 = "Excellent! You can get gold by either \nbuilding Dwarf Mines or passing levels.\nNow, click on the spell Remove and\nselect the tower."
TEXT3 = "You just used a spell. They're bought with\nMagicka which you get by killing creeps - it\nresets to zero after each level.\nNow, build another Arrow Tower."
TEXT4 = "The skull icon shows missed creeps/limit.\nThe sand clock displays time before wave.\nYou can (un)pause the game by pressing P.\nTry it now!"
TEXT5 = "When in trouble, try to pause\nand hover over spells and creeps.\nNow, press SPACE!"
SHIMENU = Sheet("./data/image/menu/ship_menu.png")
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

clickable = {"LOK": 3, \
             "TYR": 3, \
             "JOT": 2, \
             "DRA": 2, \
             "GIA": 1, \
             "WAT": 2, \
             "BIR": 3}

class TutBot:
    
    def __init__(self, player, rm, at):
        self.player = player
        self.rm = rm
        self.at = at
        self.text = TEXT1
        self.ended = False
        self.player = player
        self.at.flash()
        self.phase = 1
        self.p = 0
  
    def current(self):
        return self.text

    def update(self):
        if self.phase == 1 and self.player["magicka"]==0:
            self.player["magicka"] = 5

        key = pygame.key.get_pressed()
        if self.phase == 5 and key[K_SPACE] and not self.ended:
            self.ended = True
            self.text = ""
            self.player["gold"] = 60

        if self.phase == 1 and self.player["gold"]==0:
            self.at.flash()
            self.phase += 1
            self.text = TEXT2
            self.rm.flash()
        elif self.phase == 2 and self.player["magicka"]==0:
            self.rm.flash()
            self.phase += 1
            self.text = TEXT3
            self.at.flash()
            self.player["gold"] += 10
        elif self.phase == 3 and self.player["gold"]==0:
            self.at.flash()
            self.text = TEXT4
            self.phase += 1
        elif self.phase == 4 and (key[K_p] or key[K_PAUSE]):
            self.p += 1
            if self.p>=2 and self.player.paused>0:
                self.text = TEXT5
                self.phase += 1

class Game(State):

    def __init__(self, key, manager):
        State.__init__(self,key,manager)
        self.psurf = pygame.surface.Surface((1024,768))
        self.psurf.fill((0,0,0))
        self.psurf.set_alpha(200)
        self.paused = False
        self.prepared = False
        self.bullet_group = pygame.sprite.Group()
        self.creeps = pygame.sprite.LayeredUpdates()
        self.cursor = self.manager.cursor
        self.towers = pygame.sprite.OrderedUpdates()
        self.bgt = pygame.sprite.OrderedUpdates()
        self.needed_tiles = pygame.sprite.Group()
        self.needed_tiles1 = pygame.sprite.Group()
        self.banned_tiles = pygame.sprite.OrderedUpdates()
        self.banned_tiles1 = pygame.sprite.OrderedUpdates()
        self.player = self.manager.player
        self.weatherbg = pygame.surface.Surface((1024,640))
        self.weatherbg.fill((0,0,0))
        self.weatherbg.set_alpha(0)
        self.magic = pygame.sprite.Group()
        self.d = pygame.sprite.Group()
        self.buoyant = pygame.sprite.Group()
        self.default_text = ''
        self.before_mag = self.before_g = 0
        self.tpassed = 0
        self.tbot = None
        self.previous = 0
        self.ingame_menu = Master([0,596],1024,172,self.screen,self.cursor, \
        "./data/font/carolingia.ttf")
        self.ingame_menu_bg = load_image("./data/image/menu/ingame_menu.png")
        self.ship_menu = SHIMENU.get_at((0,0,157,61), True)
        self.ship_hp = SHIMENU.get_at((159,6,47,43), True)
        self.bonus_menu = load_image("./data/image/menu/bns_menu.png")
        self.particle_emitter = pygame.sprite.Group()
        self.spells = pygame.sprite.Group()
        self.wave = 0
        self.total = 0
        self.bars = pygame.surface.Surface((1024,768))
        self.bars.fill((0,0,0))
        self.bars.set_colorkey((0,0,0))
        self.wave_t = 0
        self.countdown = False
        self.moded = False
        self.totalc = 0
        self.unlock = ['Nothing','']
        self.map = None
        self.lname = None
        self.cid = None

    def inf(self, terminate, id, args):
        if self.ingame_menu.state in ["okbox", "yesnobox", \
                                      "pause", "pause1"]:
            self.cid = None
            return

        if terminate!=1:
            self.cid = id
            n = args[1]
            if args[0]==0:
                a = DESC[n][0]
                ps = [1, 1]
                if self.player["powerup"]=="BEO":
                    ps[1] = 1.1
                elif self.player["powerup"]=="GIF":
                    ps[0] = 0.9
                a = int(a*ps[0])
                self.gl.change(str(a))
                self.tal.change(str(DESC[n][1]*ps[1]))
                self.dt.change(str(DESC[n][2]))
                self.ingame_menu.switch("tinf")
            elif args[0]==1:
                self.ml.change(str(DESC[n][0]))
                self.tl.change(str(DESC[n][1]))
                self.dt.change(str(DESC[n][2]))
                self.ingame_menu.switch("sinf")
            elif args[0]==2:
                a = 1
                if self.player["allowed"]==0:
                    a = 1.1
                elif self.player["allowed"]==4:
                    a = 0.9
                self.hl.change(str(args[2])+"/"+str(int(DESC[n][0]*a)))
                self.t.change(TYPES[DESC[n][1]])
                self.dt.change(str(DESC[n][2]))
                self.ingame_menu.switch("cinf")
            elif args[0]==3:
                txt = DESC2[args[1]][1]
                txt = txt.split('\n')
                txt.remove(' ')
                self.dt.change('\n'.join(txt))
        elif terminate==1 and self.cid==id:
            self.ingame_menu.switch("default")
            self.cid = None
            self.dt.change(self.default_text)

    def fail(self):
        self.player["magicka"] = self.before_mag
        self.player["gold"] = self.before_g
        self.player.failed += 1
        self.player.reset()
        self.prepared = False
        self.ingame_menu.switch("default")


    def back(self):
        self.player["magicka"] = self.before_mag
        self.player["gold"] = self.before_g
        self.player.reset()
        self.prepared = False
        self.ingame_menu.switch("default")
        self.manager.states["menu"].check_ach()
        self.manager.set_state("map")

    def win(self):
        if not self.player.lpassed:
            self.ingame_menu.switch("default")
            self.player.paused = 1
            return
        lev = self.manager.level
        self.ingame_menu.switch("default")
        self.prepared = False
        if not self.lname in self.player["passed"]:
            score = self.do_score(False)
            if self.mode=="ship":
                b = self.player.collected*10
            elif self.mode=="normal" or self.mode=="timing":
                x = 1
                if self.player["powerup"]=="AND": x = 1.1
                b = int(lev["reward"]*x)
            self.player.reward("gold", b)
            if self.unlock[0]!='Nothing':
                if self.player.hasscroll or self.mode!="ship":
                    self.player["unlocked"].append(self.unlock[1])
            if self.lname=="Tutorial":
                self.player["achiv"].append("TUT")
                self.player.newa = True
            self.player["passed"].append(self.lname)
            self.player["score"].append(score)
            self.player["bpoints"] += score+1
            self.player["g_lev"].append(self.before_g)
        self.player.debonus()
        self.player.save()
        self.player.reset()
        self.manager.states["shop"].mix()
        self.manager.states["menu"].check_ach()
        self.manager.set_state("map")

    def buy_tower(self, tow):
        if not self.player.buying and self.player.paused>0:
            x = 1
            if self.player["powerup"]=="GIF":
                x = 0.9
            self.player.buying = True
            if tow[1]==0:
                potato = tow[0]([0,0],80,self.screen, \
                        self.bullet_group,self.creeps,self.bgt,[self.needed_tiles, \
                        self.towers],[self.banned_tiles], \
                        self.player, self.particle_emitter, 1, self.manager.sound_manager)
                potato.price_gold = int(potato.price_gold*x)
            else:
                potato = tow[0]([0,0],80,self.screen, \
                        self.bullet_group,self.creeps,self.bgt,[self.needed_tiles1, \
                        self.towers],[self.banned_tiles], \
                        self.player, self.particle_emitter, 1, self.manager.sound_manager)
                potato.price_gold = int(potato.price_gold*x)
            if self.player["powerup"]=="BEO":
                potato.attack = int(1.1*potato.damage)
            elif self.player["powerup"]=="PIP":
                potato.m = -1
            elif self.player["powerup"]=="HAM":
                print potato.range
                potato.range = int(1.2*potato.range)
                print potato.range
            self.towers.add(potato)
            del potato

    def power(self, arg):
       if self.player.charges <= 0 or self.player.buying or \
           self.player.paused<0: return
       self.player.buying = True
       self.cursor.spell()
       if arg=="TYR":
           potato = TyrStaff([0, 0], self.player, self.particle_emitter, \
                             self.screen, self.towers, sound=self.manager.sound_manager)
       elif arg=="LOK":
           potato = LStaff([0, 0], self.player, self.particle_emitter, \
                           self.screen, self.towers, sound=self.manager.sound_manager)
       elif arg=="JOT":
           potato = JHeart([0, 0], self.player, self.particle_emitter, \
                           self.screen, self.creeps, sound=self.manager.sound_manager)
       elif arg=="GIA":
           potato = StoneGiant([0,0],80,self.screen, \
                    self.bullet_group,self.creeps,self.bgt,[self.needed_tiles, \
                    self.towers],[self.banned_tiles], \
                    self.player, self.particle_emitter, 1, self.manager.sound_manager)
       elif arg=="BIR":
           potato = Spiky([0, 0], self.player, self.particle_emitter, \
                          self.screen, [self.banned_tiles, self.creeps], \
                          sound=self.manager.sound_manager)
       elif arg=="WAT":
           potato = Whiry([0, 0], self.player, self.particle_emitter, \
                          self.screen, [self.needed_tiles1, self.creeps], \
                          sound=self.manager.sound_manager)
       elif arg=="DRA":
           potato = Flame(self.creeps, self.player, self.cursor)
       self.magic.add(potato) 
       del potato

    def buy_spell(self, spl):
        if not self.player.buying and self.player.paused>0:
            self.player.buying = True
            self.cursor.spell()
            potato = spl([0, 0], self.player, self.particle_emitter, \
                                  self.screen, self.towers, sound=self.manager.sound_manager)
            if self.player["powerup"]=="ULL":
                potato.effect_time += 100
            self.spells.add(potato)
            del potato

    def buy_spell1(self, spl):
        if not self.player.buying and self.player.paused>0:
            self.player.buying = True
            self.cursor.spell()
            potato = spl([0, 0], self.player, self.particle_emitter, \
                                  self.screen, self.creeps, sound=self.manager.sound_manager)
            self.spells.add(potato)
            del potato

    def modus(self):
        level = self.manager.level
        x = level["start"][0]*32
        y = level["start"][1]*32
        if self.mode=="ship":
            self.moded = True
            tmp = Boat([x, y], self.screen, \
                       self.player, self.particle_emitter, self.banned_tiles)
            self.creeps.add(tmp)
            for tower in level["towers"]:
                tmp = IndianTent([tower[0]*32,tower[1]*32], self.screen, self.bullet_group, \
                                 self.creeps, self.bgt, self.player, self.particle_emitter, \
                                 sound=self.manager.sound_manager)
                self.towers.add(tmp)
            for b in level["barrels"]: 
                tmp = Barrel([b[0]*32,b[1]*32], self.player, self.creeps)
                self.particle_emitter.add(tmp)
            if not level["unlock"].split('-')[1] in self.player["unlocked"]:
                scr = level["scroll"]
                self.particle_emitter.add(Scrolly([scr[0]*32,scr[1]*32],self.player,self.creeps))
        elif self.mode=="warrior":
            self.dude = BonusWarrior([x, y], self.screen, level["waypoint"], self.cursor, \
                                     self.player, self.particle_emitter, self.inf, self.towers)
            self.creeps.add(self.dude)
            for t in level["towers"]:
                if t[0]==0:
                    tmp = GoblinTower([t[0]*32,t[1]*32], self.screen, self.bullet_group, \
                                 self.creeps, self.bgt, self.player, self.particle_emitter, \
                                 sound=self.manager.sound_manager)
                elif t[0]==1:
                    tmp = IceTower([t[0]*32,t[1]*32], self.screen, self.bullet_group, \
                                 self.creeps, self.bgt, self.player, self.particle_emitter, \
                                 sound=self.manager.sound_manager)
                elif t[0]==2:
                    tmp = BadassTower([t[0]*32,t[1]*32], self.screen, self.bullet_group, \
                                 self.creeps, self.bgt, self.player, self.particle_emitter, \
                                 sound=self.manager.sound_manager)
                if t[3]!=0: self.towers.add(tmp)
                else: self.bgt.add(tmp)
            surf = pygame.surface.Surface((53,53))
            surf.fill((0,0,0))
            surf.set_alpha(0)
            self.countdowns = [surf, surf, surf, surf]

    def next_wave(self):
        if not self.countdown or not self.mode in ["normal","timing"]: return

        level = self.manager.level

        self.wave += 1
        x = 0
        if self.player["powerup"]=="HOR":
            x = 5
        if self.wave >= self.total:
             self.countdown = False
        else:
             self.wave_t = level["wave_t"][self.wave]+x
        enemy = level["enemies"][self.wave-1]
        quantity = level["quantity"][self.wave-1]

        self.previous = 0
        if level["name"]=='6':
            wp = [[14,15],[8,15],[8,19]]
            r = random.choice([wp, level["waypoint"]]) #Trolling the player
        for i in range(quantity, 0, -1):
            x_point = level["start"][0]*32
            y_point = level["start"][1]*32
            if enemy=="goblin":
                if level["name"]=='6':
                    temp = Goblin([x_point,y_point-self.previous*i], \
                        self.bars,r,self.cursor, \
                        self.player, self.particle_emitter, self.inf)
                else:
                    temp = Goblin([x_point,y_point-self.previous*i], \
                        self.bars,level["waypoint"],self.cursor, \
                        self.player, self.particle_emitter, self.inf)
                self.previous = 45
            elif enemy=="skeleton":
                self.previous = 65
                temp = Skeleton([x_point,y_point-self.previous*i], \
                        self.bars,level["waypoint"],self.cursor, \
                        self.player, self.particle_emitter, self.inf)
            elif enemy=="wolf":
                self.previous = 30
                temp = Wolf([x_point,y_point-self.previous*i], \
                        self.bars,level["waypoint"],self.cursor, \
                        self.player, self.particle_emitter, self.inf)
            elif enemy=="boar":
                self.previous = 40
                temp = Boar([x_point,y_point-self.previous*i], \
                        self.bars,level["waypoint"],self.cursor, \
                        self.player, self.particle_emitter, self.inf)
            elif enemy=="troll":
                self.previous = 108
                if level["name"]=='6':
                    temp = Troll([x_point,y_point-self.previous*i], \
                        self.bars,r,self.cursor, \
                        self.player, self.particle_emitter, self.inf)
                else:
                    temp = Troll([x_point,y_point-self.previous*i], \
                        self.bars,level["waypoint"],self.cursor, \
                        self.player, self.particle_emitter, self.inf)
            elif enemy=="frostgiant":
                self.previous = 120
                temp = FrostGiant([x_point,y_point-self.previous*i], \
                        self.bars,level["waypoint"],self.cursor, \
                        self.player, self.particle_emitter, self.inf)
            elif enemy=="seaserpent":
                self.previous = 120
                temp = SeaSerpent([x_point,y_point-self.previous*i], \
                        self.bars,level["waypoint"],self.cursor, \
                        self.player, self.particle_emitter, self.inf)
            elif enemy=="warrior":
                self.previous = 100
                temp = Warrior([x_point,y_point-self.previous*i], \
                        self.bars,level["waypoint"],self.cursor, \
                        self.player, self.particle_emitter, self.inf)
            elif enemy=="lilkraken":
                self.previous = 60
                temp = LilKraken([x_point,y_point-self.previous*i], \
                        self.bars,level["waypoint"],self.cursor, \
                        self.player, self.particle_emitter, self.inf)
            elif enemy=="wyvern":
                self.previous = 140
                temp = Wyvern([x_point,y_point-self.previous*i], \
                        self.bars,level["waypoint"],self.cursor, \
                        self.player, self.particle_emitter, self.inf)
            if self.player["allowed"]==0:
                temp.health = int(temp.health*1.1)
                temp.mh = temp.health
            elif self.player["allowed"]==4:
                temp.health = int(temp.health*0.9)
                temp.mh = temp.health
            self.creeps.add(temp, layer=self.total-self.wave)
    
        for tower in self.towers:
            tower.creeps = self.creeps   

    def load_level(self):
        level = self.manager.level
        try:
            self.mode = level["mode"]
        except:
            self.mode = "normal"
        self.reset()

        try:
            self.unlock = level["unlock"].split('-')
        except:
            pass

        self.lname = level["name"]

        if self.lname == "Tutorial" and not "Tutorial" in self.player["passed"] and not 't' in self.player["needless"] and self.player["retries"]<1:
            self.tbot = TutBot(self.player, self.rm, self.at)
            self.default_text = self.tbot.current()
            self.dt.change(self.default_text)
        else:
            self.countdown = True

        if self.mode=="normal":
            x = 0
            if self.player["powerup"]=="HOR": x = 5
            self.wave_t = level["wave_t"][0]+x
            self.total = len(level["quantity"])
            for i in level["quantity"]:
                self.totalc += i

        self.map = map = level.map
        pat = []
        for i in map:
            if i.n in BUILDABLE[0]:
                self.needed_tiles.add(i)
            elif i.n == BUILDABLE[1]:
                self.needed_tiles1.add(i)
            elif not i.n in BUILDABLE:
                if i.n==11:
                    pat.append([i.rect.x,i.rect.y])
                self.banned_tiles.add(i)

        w = level["weather"]
        if w=="snow":
            self.d.empty()
            self.weatherbg.set_alpha(30)
            for x in range(1024/3):
                y = random.randint(10, 608)
                self.d.add(Weather([x*3,0-random.randint(0,304)],y,"snow"))
        elif w=="rain":
            self.d.empty()
            self.weatherbg.set_alpha(80)
            for x in range(1024/3):
                y = random.randint(10, 608)
                self.d.add(Weather([x*3,0-random.randint(0,304)],y,"rain", \
                           self.needed_tiles1, self.creeps, self.towers))
        elif w=="sunny":
            self.d.empty()
            self.weatherbg.set_alpha(0)
            if len(self.needed_tiles1)>0:
                for i in range(4):
                    self.particle_emitter.add(Fish(self.needed_tiles1))
            if len(pat)>0:
                for i in range(6):
                    self.particle_emitter.add(Butterfly(pat))
        if "float" in level.keys():
            for z in level["float"]:
                self.buoyant.add(Floater([z[0]*32,z[1]*32],z[2]))

        if self.mode!="normal" and not self.moded:
            self.modus()
        self.prepared = True
        self.player.reset()
        if self.mode=="normal":
            pup = self.player["powerup"]
            if pup != None and pup in clickable.keys():
                self.player.charges = clickable[pup]
        if level["name"] in self.player["passed"] and self.mode=="normal":
            x = self.player["passed"].index(level["name"])
            self.player["gold"] = self.player["g_lev"][x]
            self.scoring = True
            if not 'replay' in self.player["needless"]:
                self.passed.change('When replaying a level, you\nwill have the amount of gold\n\
you had when you passed it.\nAfter finishing the level, you\nplay with your current\namount.')
                self.player["needless"].append('replay')
                self.player.paused = -1
                self.ingame_menu.switch("okbox")
        elif not level["name"] in self.player["passed"] and level["name"] in DESC.keys():
                self.passed.change(DESC[level["name"]])
                self.player.paused = -1
                self.ingame_menu.switch("okbox")

        if self.player["powerup"]=="MJO":
            self.spells.add(AutoThunder(self.particle_emitter, self.creeps, self.player))

    def do_score(self, p):
        lev = self.manager.level
        score = 2
        if self.mode=="normal":
            if self.player["allowed"]==2:
                score = 2-self.player.passed
            elif self.player["allowed"]==4:
                score = 2-(self.player.passed+self.player.passed%2)//2
        elif self.mode=="ship":
            score = (self.player.collected*1.0)/(len(lev["barrels"])*1.0)
        if not p:
            pass
            return score
        t = ''
        x = self.player["passed"].index(self.lname)
        if score>self.player["score"][x]:
            bp = score - self.player["score"][x]
            self.player["score"][x] = score
            self.player["bpoints"] += bp+1
            t = 'You have beaten your old\nscore! +'+str(bp)+' Battle Points.'
        else:
            t = 'You have failed to beat your\nscore. You will be returned to\nmap.'
        self.player["gold"] = self.before_g
        return score

    def reset(self):
        self.scoring = False
        self.bullet_group.empty()
        self.creeps.empty() 
        self.towers.empty()
        self.needed_tiles.empty()
        self.banned_tiles.empty()
        self.needed_tiles1.empty()
        self.particle_emitter.empty()
        self.buoyant.empty()
        self.magic.empty()
        self.spells.empty()
        self.bgt.empty()
        self.wave = 0
        self.charge = None
        self.wave_t = 0
        self.unlock = ['Nothing','']
        self.total = 0
        self.countdown = False
        self.tpassed = 0
        self.totalc = 0
        self.moded = False
        self.lname = None
        self.before_mag = self.player["magicka"]
        self.before_g = self.player["gold"]
        self.previous = 0
        self.ingame_menu.reset_widgets()
        things = self.player["unlocked"]
        if self.mode=="ship":
            self.barr = Label(self.ingame_menu, [34, 135], (255,255,255),None,15, \
                              "Loading", ["default","yesnobox","okbox","pause", "pause1"])
            return
        elif self.mode=="warrior":
            self.bhp = Label(self.ingame_menu, [38, 141], (255,255,255),None,15, \
                             "Loading", ["default","yesnobox","okobox","pause", "pause1"])
            self.magicka_label = Label(self.ingame_menu,[382,141],(255,255,255),None,15, \
                              "Loading", ["default","yesnobox","okbox", "pause", "pause1"])
            return

        self.t = Image(self.ingame_menu, [246,87], TYPES[0], ["cinf"])
        self.gl = Label(self.ingame_menu,[271,64],(255,255,255),None,15, \
                        "Loading",["tinf"])
        self.tal = Label(self.ingame_menu,[271,89],(255,255,255),None,15, \
                        "Loading",["tinf"])
        self.ml = Label(self.ingame_menu,[271,64],(255,255,255),None,15, \
                        "Loading",["sinf"])
        self.tl = Label(self.ingame_menu,[271,89],(255,255,255),None,15, \
                        "Loading",["sinf"])
        self.hl = Label(self.ingame_menu,[271,64],(255,255,255),None,15, \
                        "Loading",["cinf"])
        self.dt = Textbox(self.ingame_menu,[350,54],(255,255,255),None,24,"",3, \
                          ["tinf","sinf","cinf","default"])
        self.gold_label = Label(self.ingame_menu,[285,24],(255,255,255),None,15, \
                                "Loading",["default","yesnobox","okbox","sinf", \
                                           "cinf","tinf","pause","pause1"])
        self.magicka_label = Label(self.ingame_menu,[372,24],(255,255,255),None,15, \
                                   "Loading",["default","yesnobox","okbox","sinf", \
                                              "cinf","tinf","pause","pause1"])
        self.passed_label = Label(self.ingame_menu,[635,24],(255,255,255),None,15, \
                                "Loading",["default","yesnobox","okbox","sinf", \
                                           "cinf","tinf","pause", "pause1"])
        self.wave_tl = Label(self.ingame_menu,[722, 24],(255,255,255),None,15, \
                            "",["default","yesnobox","okbox","sinf", \
                                "cinf","tinf","pause", "pause1"])
        Image(self.ingame_menu, [246,64], STATICONS.get_at((0,0,19,22)), ["tinf"])
        Image(self.ingame_menu, [246,89], STATICONS.get_at((20,0,22,22)), ["tinf"])
        Image(self.ingame_menu, [246,64], STATICONS.get_at((59,5,11,17)), ["sinf"])
        Image(self.ingame_menu, [246,89], STATICONS.get_at((129,0,14,21)), ["sinf"])
        Image(self.ingame_menu, [246,64], STATICONS.get_at((43,8,15,14)), ["cinf"])
        if "AT" in things:
            self.at = ImageButton(self.ingame_menu,[43,59],BUTTONS.get_at((33,0,32,32), \
                    False),self.buy_tower, [ArrowTower,0], ["default","yesnobox","okbox","sinf","cinf","tinf","pause", "pause1"], \
                    True, None, self.inf, [0,"AT"], key=K_1)
        if "RM" in things:
            self.rm = ImageButton(self.ingame_menu,[806,59],BUTTONS.get_at((0,33,32,32), \
                    True),self.buy_spell, Kill, ["default","yesnobox","okbox","sinf", \
                                                 "cinf","tinf","pause","pause1"], \
                    True, None, self.inf, [1,"RM"], key=K_r)
        if "ST" in things:
            ImageButton(self.ingame_menu,[77,59],BUTTONS.get_at((66,0,32,32), \
                    False),self.buy_tower, [SpearTower,0], ["default","yesnobox","okbox","sinf","cinf","tinf","pause", "pause1"], \
                    True, None, self.inf, [0,"ST"], key=K_2)
        if "DM" in things:
            ImageButton(self.ingame_menu,[111,59],BUTTONS.get_at((99,0,32,32), \
                    False),self.buy_tower, [DwarfMine,0], ["default","yesnobox","okbox","sinf","cinf","tinf","pause","pause1"], \
                    True, None, self.inf, [0,"DM"], key=K_3)
        if "SS" in things: 
            ImageButton(self.ingame_menu,[43,92],BUTTONS.get_at((132,0,32,32), \
                    False),self.buy_tower, [Smallship,1], ["default","yesnobox","okbox","sinf","cinf","tinf","pause","pause1"], \
                    True, None, self.inf, [0,"SS"], key=K_4)
        if "LH" in things: 
            ImageButton(self.ingame_menu,[77,92],BUTTONS.get_at((165,0,32,32), \
                    False),self.buy_tower, [Lighthouse,0], ["default","yesnobox","okbox","sinf","cinf","tinf","pause","pause1"], \
                    True, None, self.inf, [0,"LH"], key=K_5)
        if "LS" in things: 
            ImageButton(self.ingame_menu,[111,92],BUTTONS.get_at((198,0,32,32), \
                    False),self.buy_tower, [Longship,1], ["default","yesnobox","okbox","sinf","cinf","tinf","pause","pause1"], \
                    True, None, self.inf, [0,"LS"], key=K_6)
        if "RS" in things: 
            ImageButton(self.ingame_menu,[43,125],BUTTONS.get_at((231,0,32,32), \
                    False),self.buy_tower, [RuneStone,0], ["default","yesnobox","okbox","sinf","cinf","tinf","pause","pause1"], \
                    True, None, self.inf, [0,"RS"], key=K_7)
        if "EF" in things: 
            ImageButton(self.ingame_menu,[77,125],BUTTONS.get_at((264,0,32,32), \
                    False),self.buy_tower, [ElfTree,0], ["default","yesnobox","okbox","sinf","cinf","tinf","pause","pause1"], \
                    True, None, self.inf, [0,"EF"], key=K_8)
        if "GT" in things: 
            ImageButton(self.ingame_menu,[111,125],BUTTONS.get_at((297,0,32,32), \
                    False),self.buy_tower, [AsgardTower,0], ["default","yesnobox","okbox","sinf","cinf","tinf","pause","pause1"], \
                    True, None, self.inf, [0,"GT"], key=K_9)
        if "SU" in things: 
            ImageButton(self.ingame_menu,[839,59],BUTTONS.get_at((33,33,32,32), \
                    True),self.buy_spell, SpeedUp, ["default","yesnobox","okbox", \
                                                    "sinf","cinf","tinf","pause","pause1"], \
                    True, None, self.inf, [1,"SU"], key=K_s)
        if "EY" in things and self.player["powerup"]!="HAM": 
            ImageButton(self.ingame_menu,[872,59],BUTTONS.get_at((66,33,32,32), \
                    True),self.buy_spell, Eye, ["default","yesnobox","okbox", \
                                                "sinf","cinf","tinf","pause","pause1"], \
                    True, None, self.inf, [1,"EY"], key=K_e)
        if "FA" in things: 
            ImageButton(self.ingame_menu,[905,59],BUTTONS.get_at((165,33,32,32), \
                    True),self.buy_spell, FireArrows, ["default","yesnobox","okbox", \
                                                       "sinf","cinf","tinf","pause","pause1"], \
                    True, None, self.inf, [1,"FA"], key=K_a)
        if "FR" in things: 
            ImageButton(self.ingame_menu,[806,92],BUTTONS.get_at((198,33,32,32), \
                    True),self.buy_spell, Frost, ["default","yesnobox","okbox", \
                                                  "sinf","cinf","tinf","pause","pause1"], \
                    True, None, self.inf, [1,"FR"], key=K_f)
        if "PO" in things: 
            ImageButton(self.ingame_menu,[839,92],BUTTONS.get_at((231,33,32,32), \
                    True),self.buy_spell, Poison, ["default","yesnobox","okbox", \
                                                   "sinf","cinf","tinf","pause","pause1"], \
                    True, None, self.inf, [1,"PO"], key=K_l)
        if "OR" in things: 
            ImageButton(self.ingame_menu,[872,92],BUTTONS.get_at((297,33,32,32), \
                    True),self.buy_spell, Orbiting, ["default","yesnobox","okbox", \
                                                     "sinf","cinf","tinf","pause","pause1"], \
                    True, None, self.inf, [1,"OR"], key=K_o)
        if "TH" in things: 
            ImageButton(self.ingame_menu,[905,92],BUTTONS.get_at((0,66,32,32), \
                    True),self.buy_spell1, Thunder, ["default","yesnobox","okbox", \
                                                     "sinf","cinf","tinf","pause","pause1"], \
                    True, None, self.inf, [1,"TH"], key=K_t)
        if "SW" in things: 
            ImageButton(self.ingame_menu,[806,125],BUTTONS.get_at((66,66,32,32), \
                    True),self.buy_spell1, Sword, ["default","yesnobox","okbox", \
                                                   "sinf","cinf","tinf","pause","pause1"], \
                    True, None, self.inf, [1,"SW"], key=K_d)
        if "CO" in things: 
            ImageButton(self.ingame_menu,[839,113],BUTTONS.get_at((132,66,32,32), \
                    True),self.buy_spell1, Confusion, ["default","yesnobox","okbox", \
                                                       "sinf","cinf","tinf","pause","pause1"], \
                    True, None, self.inf, [1,"CO"], key=K_c)
        if "HM" in things: 
            ImageButton(self.ingame_menu,[872,125],BUTTONS.get_at((33,66,32,32), \
                    True),self.buy_spell1, Hammer, ["default","yesnobox","okbox", \
                                                    "sinf","cinf","tinf","pause","pause1"], \
                    True, None, self.inf, [1,"HM"], key=K_h)
        if "SH" in things: 
            ImageButton(self.ingame_menu,[905,125],BUTTONS.get_at((99,66,32,32), \
                    True),self.buy_spell1, Shockwave, ["default","yesnobox","okbox", \
                                                       "sinf","cinf","tinf","pause","pause1"], \
                    True, None, self.inf, [1,"SH"], key=K_w)
        if self.player["powerup"]=='None':
            pass
        else:
            pup = self.player["powerup"]
            if not pup in clickable.keys():
                ImageButton(self.ingame_menu,[495,15],ITEMS[pup], self.chill, \
                            None, ["default","yesnobox","okbox","sinf","cinf","tinf","pause","pause1"], \
                            True, None, self.inf, [3,pup])
            else:
                ImageButton(self.ingame_menu,[495,15],ITEMS[pup],self.power,pup, \
                           ["default","yesnobox","okbox","sinf","cinf","tinf","pause"], \
                           True, None, self.inf, [3,pup])
                self.charge = Label(self.ingame_menu,[510,32],(255,255,255),None,13,'x0', \
                                   ["default","yesnobox","okbox","sinf","cinf","tinf","pause","pause1"])
        tmp = Image(self.ingame_menu, [0,0], BOX.get_at((0,0,330,334),True), ["pause", "pause1"])
        tmp.rect.center = (512, 384)
        Button(self.ingame_menu,[400,-350],(0,0,0),None,32,"CONTINUE",self.unpause,None,["pause"])
        Button(self.ingame_menu,[400,-310],(0,0,0),None,32,"RESTART",self.fail,None,["pause"])
        Button(self.ingame_menu,[400,-270],(0,0,0),None,32,"OPTIONS",self.ingame_menu.switch,"pause1",["pause"])
        Button(self.ingame_menu,[400,-230],(0,0,0),None,32,"EXIT LEVEL",self.back,None,["pause"])
        Button(self.ingame_menu,[400,-190],(0,0,0),None,32,"QUIT GAME",exit,None,["pause"])
        Button(self.ingame_menu,[400,-110],(0,0,0),None,32,"Cancel",self.ingame_menu.switch,"pause",["pause1"])
        Button(self.ingame_menu,[540,-110],(0,0,0),None,32,"Apply",self.appli,None,["pause1"])
        self.fps = Checkbox(self.ingame_menu,[400,-350],(0,0,0),None,32,"Show FPS",(0,1),["pause1"], \
                            self.manager.config["fps"])
        Label(self.ingame_menu,[400,-310],(0,0,0),None,31,"Music:",["pause1"])
        self.bs = Scroll(self.ingame_menu, [500,-310],(0,0,0),None,32,["pause1"], \
                         self.manager.config["bsound"]*100)
        Label(self.ingame_menu,[400,-270],(0,0,0),None,31,"Sound:",["pause1"])
        self.sfx = Scroll(self.ingame_menu, [500,-270],(0,0,0),None,32,["pause1"], \
                         self.manager.config["sfx"]*100)
        self.failed =  YesNoBox(self.ingame_menu,(0,0,0),None,22, "",3,self.fail,self.back)
        self.passed = OKBox(self.ingame_menu,(0,0,0),None,22,"",3,\
                            self.win)

    def appli(self):
        self.change_settings()
        self.ingame_menu.switch("pause")

    def change_settings(self):
        bs = self.bs.get_value()/100
        sfx = self.sfx.get_value()/100
        self.manager.config["bsound"] = bs
        self.manager.config["sfx"] = sfx
        self.manager.config["fps"] = self.fps.get_value()
        self.manager.config.save()
        self.manager.sound_manager.change_volume("background", bs)
        self.manager.sound_manager.change_volume("sound", sfx)

    def chill(self):
        pass

    def unpause(self):
        self.player.paused *= -1

    def update(self):
        if not self.prepared:
            self.load_level()

        if self.player.paused>0 and self.ingame_menu.state not in \
                                    ["default", "okbox", "yesnobox"]:
            self.ingame_menu.switch("default")
        elif self.player.paused<0 and self.ingame_menu.state not in \
                                                 ["pause", "pause1"]:
            self.ingame_menu.switch("pause")

        if self.countdown and not self.wave==self.total and self.player.paused>0:
            self.wave_t -= 0.03
            time = self.wave_t
            s = time % 60
            m = time // 60
            self.wave_tl.change(str(int(m))+":"+str(int(s)))
            self.tpassed += self.wave_t
            if self.wave_t <= 0.03:
                 self.next_wave()

        elif self.countdown and self.wave==self.total:
            self.countdown = False

        if not self.manager.sound_manager.current == "game":
                    self.manager.sound_manager.change_music("game")

        if not self.player.buying and self.cursor.sp:
             self.cursor.spell()

        if self.mode in ["normal", "timing"]:
            if not self.player.lpassed:
                self.gold_label.change(str(self.player["gold"]))
                self.magicka_label.change(str(self.player["magicka"]))
                if self.charge != None:
                    self.charge.change('x'+str(self.player.charges))

            self.passed_label.change(str(self.player.passed)+"/"+str(self.player['allowed']))
            lev = self.manager.level

        if self.player.passed>self.player['allowed'] and self.ingame_menu.state!="yesnobox" \
        and self.mode=="normal":
            self.player.lpassed = True
            print "You suck."
            self.failed.stats(self.player["gold"], 0, 0, self.player.tw, self.player.sp, '-') 
            self.ingame_menu.switch("yesnobox")

        if self.player.killed>=(self.totalc-self.player['allowed']) and len(self.creeps)==0 and \
            self.ingame_menu.state!="okbox" and self.mode=="normal" and not self.countdown:
            self.player.lpassed = True
            self.ingame_menu.switch("okbox")
            x = 1
            if self.player["powerup"]=="AND": x = 1.1
            r = int(lev["reward"]*x)
            t = '-'
            sc = self.do_score(self.scoring)
            if self.unlock[0]!='Nothing':
                t = DESC[self.unlock[1]][2].split('\n')[0]
            self.passed.stats(self.player["gold"], r, sc, self.player.tw, self.player.sp, t)
            print "You don't suck?!"

        if self.mode == "ship":
            if self.player.lpassed and self.ingame_menu.state=="default":
                self.ingame_menu.switch("okbox")
                t = "You have passed the level!\nGold reward: BARELL X 10"
                t += "\n                = "+str(self.player.collected*10)
                if self.unlock[0]!='Nothing' and self.player.hasscroll:
                    t += "\n"+self.unlock[0]+" unlocked!"
                self.passed.change(t)
            elif len(self.creeps)==0 and self.ingame_menu.state=="default":
                self.ingame_menu.switch("yesnobox")
        elif self.mode == "warrior":
            if self.player.lpassed and self.ingame_menu.state=="default":
                self.ingame_menu.switch("okbox")
                t = "You have passed the level!\nGold reward: "+str(self.dude.health)
                if self.unlock[0]!='Nothing':
                    t += "\n"+self.unlock[0]+" unlocked!"
                self.passed.change(t)
            elif len(self.creeps)==0 and self.ingame_menu.state=="default":
                self.ingame_menu.switch("yesnobox")

        self.bars.fill((0,0,0))
        self.needed_tiles.update()
        self.needed_tiles.draw(self.screen)
        self.needed_tiles1.update()
        self.needed_tiles1.draw(self.screen)
        self.banned_tiles.update()
        self.banned_tiles.draw(self.screen)
        self.magic.draw(self.screen)
        if self.player.paused>0:
            self.magic.update()
            self.bullet_group.update()
            self.particle_emitter.update()
            self.buoyant.update()
            self.d.update()
        self.bullet_group.draw(self.screen)
        self.bgt.update()
        self.bgt.draw(self.screen)
        self.creeps.update()
        self.creeps.draw(self.screen)
        self.towers.update()
        self.towers.draw(self.screen)
        self.spells.update()
        self.spells.draw(self.screen)
        self.buoyant.draw(self.screen)
        self.particle_emitter.draw(self.screen)
        self.d.draw(self.screen)
        self.screen.blit(self.weatherbg,(0,0))
        self.screen.blit(self.bars,(0,0))

        if self.mode=="normal" or self.mode=="timing":
            self.screen.blit(self.ingame_menu_bg,self.ingame_menu.rect)
        elif self.mode=="ship" and len(self.creeps)>0:
            self.screen.blit(self.ship_menu, (0, 708))
            g = self.creeps.sprites()[0]
            pot = (int(43*(g.health*1.0/g.mh*1.0)))
            self.ship_hp = SHIMENU.get_at((159,6+(43-pot),47,pot), True)
            self.screen.blit(self.ship_hp, (94, 714+(43-pot)))
            self.barr.change(str(self.player.collected))
        elif self.mode=="warrior":
            self.screen.blit(self.bonus_menu, (0, 708))
            p = self.dude.give_cool()
            for i in range(4):
                self.countdowns[i].set_alpha(p[i])
                self.screen.blit(self.countdowns[i], (104+i*60, 708))
                self.bhp.change(str(self.dude.health))
                self.magicka_label.change(str(self.player["magicka"]))

        if self.tbot!=None and not self.tbot.ended:
            self.tbot.update()
            self.default_text = self.tbot.current()
            self.dt.change(self.default_text)
            if self.tbot.ended and not self.countdown:
                self.countdown = True
                self.default_text = ''
                self.dt.change('')
                self.before_g = 80
        self.ingame_menu.update()
	
