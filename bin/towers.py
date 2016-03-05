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
import math
import random

from helpers       import Sheet
from particles     import *


TOWERS = Sheet("./data/image/objects/towers.png")
SHIELD = [TOWERS.get_at((350,5,40,55), True), \
          pygame.rect.Rect(0,0,40,55)]
ARROWS = Sheet("./data/image/objects/arrows.png")
parts = Sheet("./data/image/environment/particles.png")
GORE = [parts.get_at((40,3,5,5), True), parts.get_at((36,13,6,4), True), \
        parts.get_at((42,19,2,6), True), parts.get_at((33,19,6,6), True)] 
PATH = [0, 1, 2, 9, 10, 18, 20, 27, 28, 29, 36, \
        37, 45, 46, 47, 68, 61, 62, 70, 71, 79, 80]
class Dummy(pygame.sprite.Sprite):
    
    def __init__(self, pos, image, screen, range):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.screen = screen
        self.range = range

    def update(self):
        pos = pygame.mouse.get_pos()
        c = pygame.Surface((self.range*2,self.range*2))
        c.set_alpha(65)
        c.fill((0,0,0))
        c.set_colorkey((0,0,0))
        pygame.draw.circle(c,(100,200,50),(self.range,self.range), \
                           self.range-10)
        r = c.get_rect()
        r.center = self.rect.center
        if self.rect.collidepoint(pos):
            self.screen.blit(c, r)
            pygame.draw.circle(self.screen,(100,150,50),self.rect.center, \
                               self.range-10, 2)

class Tower(pygame.sprite.Sprite):

    def __init__(self, pos, range, screen, bullet_group, creeps, bgt, \
                 tiles=None, banned_tiles=None, player=None, particle_emitter=None, p=1, soundm=None):
        pygame.sprite.Sprite.__init__(self)
        self.id = id(self)
        self.pos = pos
        self.range = range
        self.screen = screen
        self.bullet_group = bullet_group        
        self.creeps = creeps
        self.player = player
        self.alive = True
        self.available_creeps = []
        self.damage = 1
        self.delay = 10
        self.health = 10
        self.image = pygame.surface.Surface((64,64))
        if tiles!=None:
            self.needed = tiles[0]
            self.others = tiles[1]
            self.banned = banned_tiles
        self.particle_emitter = particle_emitter
        self.name = ''
        self.placed = False
        self.price_gold = 20
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.shooting_timer = 0
        self.arrows = {"normal":ARROWS.get_at((0, 0, 16, 5), False), \
                       "fire":ARROWS.get_at((17, 0, 16, 5), False)}
        self.arrow = self.arrows["normal"]
        self.enchanted = False
        self.show_p = p
        self.t = ["ground"]
        self.c = [(109, 90, 57),(85, 162, 10)]
        self.immune = False
        self.m = 1
        self.passon = False
        self.bgt = bgt
        self.passedon = []
        self.copy = None
        self.soundm = soundm
        self.behind = True
        self.rage = False

    def bonus(self):
        pass

    def shoot(self, object):
        """
        When the delay time has passed, shoot the
        given object
        """
        if self.shooting_timer == self.delay:
            pas = self.passon
            if object in self.passedon: pas = False
            effect = None
            if self.passon == "ft" and pas: effect="icy"
            temp = Bullet(self.rect.center, 6, object.rect.center, \
                          self.creeps, self.arrow, self.damage, pas, \
                          self.passedon,effect)
            self.bullet_group.add(temp)
            if self.soundm!=None:
                self.soundm.play_sound("arrow")
            self.shooting_timer = 0
        else:
            self.shooting_timer += 1

    def search(self):
        """
        Search for a creep, or shoot the existing target
        """
        # If no creep is locked, search for one and add it
        if not len(self.available_creeps) > 0:
            for i in self.creeps:
                x = abs(self.rect.centerx-i.rect.x)
                y = abs(self.rect.centery-i.rect.y)
                d = math.sqrt(x*x+y*y)
                if d <= self.range and i.t in self.t:                
                    self.available_creeps.append(i)
                if len(self.available_creeps)==self.m:
                    return
        else:
            # If the creep is locked and alive, shoot!
            for i in self.available_creeps:
                x = abs(self.rect.centerx-i.rect.x)
                y = abs(self.rect.centery-i.rect.y)
                d = math.sqrt(x*x+y*y)
                if i.alive == False:
                    try:
                        self.available_creeps.remove(i) 
                        if self.rage: self.damage += 0.2
                    except:
                        pass

                # When the creep gets out of the range, remove it from the list
                if not d <= self.range: 
                    try:
                        self.available_creeps.remove(i)
                    except:
                        pass

                    # If the creep has been hit by magical bullet, remove it from list
                    try:
                        self.passedon.remove(i)
                    except:
                        pass

                # If everything is fine, shoot the creep
                else:
                    self.shoot(i)

    def on_collision(self, creep):
        """
        Used for boats; will be destroyed on
        collision with creeps.
        """
        #self.kill()

    def place(self):
        if self.player==None:
            self.placed = True
            return

        """
        Place the tower if player has enough money,
        and collision requirements are OK
        """
        pos = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        self.rect.center = pos

        self.behind = True

        w, h = self.image.get_width(), self.image.get_height()
        r = pygame.Rect(self.rect.x, self.rect.y+h*(2.0/3.0), w, h*(1.0/3.0))

        # Checks all needed collisions
        col_build_tiles = pygame.sprite.spritecollide(self, self.needed, False)
        col_banned_tiles = False
        
        for group in self.banned:
            col = pygame.sprite.spritecollide(self, group, False)
            for i in col:
                if r.colliderect(i.rect):
                    col_banned_tiles = True
                    break
                else:
                    if i.n in PATH:
                        self.behind = False

        col_other_towers = pygame.sprite.spritecollide(self, self.others, False)
        col_other_towers_final = False

        for tower in col_other_towers:
            if not tower.id == self.id:
                if r.colliderect(tower.rect):
                    col_other_towers_final = True
                    break
                else:
                    pass

        if click[0] == 1:
            # When all requirements are valid, place the tower
            # and take gold from player
            if col_build_tiles and not col_banned_tiles and not \
               col_other_towers_final and not self.rect.y > \
               (19*32-self.image.get_height()):
                res = True
                if self.name != 'SG':
                    if self.player["gold"] < self.price_gold:
                        res = False
                else:
                    if self.player.charges <= 0:
                        res = False
                    else:
                        self.player.charges -= 1
                if res:
                    self.placed = True   
                    self.player.buying = False
                    self.player["gold"] -= self.price_gold
                    self.player.tw += 1
                    height = self.image.get_height()
                    if self.show_p != 0:
                        for i in xrange(int(self.image.get_width()/5)):
                            speed_x = self.rect.x+5*i
                            self.particle_emitter.add(  
                            Particle([speed_x, self.rect.y+height], [ \
                                 random.uniform(-0.5, 0), -1], \
                                 random.randrange(1, 3), self.c[0], 6, 0.7), 
                            Particle([speed_x+4, self.rect.y+height], [ \
                                 random.uniform(0, 0.5), -1], \
                                 random.randrange(1, 3), self.c[1], 6, 0.7))
                    if self.soundm!=None:
                        self.soundm.play_sound("build")
                    if self.behind:
                        self.copy = Dummy([self.rect.x, self.rect.y], self.image, \
                                           self.screen, self.range)
                        self.bgt.add(self.copy)
                        self.image = pygame.surface.Surface(self.image.get_size())
                        self.image.fill((0,0,0))
                        self.image.set_colorkey((0,0,0))
                else:
                    temp = Error([self.rect.x, self.rect.y-8], \
                                  20,(255,255,255), "INSUFFICIENT RESOURCES!")
                    self.particle_emitter.add(temp)

            # When the tower is off the limits, warn the player
            elif col_banned_tiles or \
                     col_other_towers_final or self.rect.y > \
                 (19*32-self.image.get_height()):
                temp = Error([self.rect.x, self.rect.y-8], 20, \
                             (255, 255, 255), "CAN'T PLACE IT HERE!")
                self.particle_emitter.add(temp)
    
        # If player has clicked RMB, cancel the tower
        if click[2] == 1:
            self.player.buying = False
            self.alive = False
            self.kill()

    def update(self):
        if self.alive:
            if self.player.paused<0:
                return
            if not self.placed:
                self.place()
            else:
                col = []
                if self.copy!=None:
                    col = pygame.sprite.spritecollide(self.copy, self.creeps, False)
                else:
                    col = pygame.sprite.spritecollide(self, self.creeps, False)
                for i in col:
                    if self.placed:
                        self.on_collision(i)
                        continue
                self.search()
                self.bonus()
                if self.copy!=None:
                    return
            pos = pygame.mouse.get_pos()
            c = pygame.Surface((self.range*2,self.range*2))
            c.set_alpha(65)
            c.fill((0,0,0))
            c.set_colorkey((0,0,0))
            pygame.draw.circle(c,(100,200,50),(self.range,self.range), \
                               self.range-10)
            r = c.get_rect()
            r.center = self.rect.center
            if self.rect.collidepoint(pos):
                self.screen.blit(c, r)
                pygame.draw.circle(self.screen,(100,150,50),self.rect.center, \
                                   self.range-10, 2)
        else:
            pass


class StoneGiant(Tower):

    def __init__(self, pos, range, screen, bullet_group, creeps, \
                 bgt, tiles, banned_tiles, player, particle_emitter, p=1, sound=None):
        Tower.__init__(self, pos, 100, screen, bullet_group, \
                       creeps, bgt, tiles, banned_tiles, player, particle_emitter, p, sound)
        self.damage = 75
        self.delay = 16
        self.images = [TOWERS.get_at((108, 66, 50, 78), True), \
                       TOWERS.get_at((159, 66, 50, 78), True), \
                       TOWERS.get_at((210, 66, 50, 78), True)]
        self.image = self.images[0]
        self.at = 16
        self.ai = 0
        self.immune = True
        self.t = ["ground", "air", "magic", "water"]
        self.price_gold = 0
        self.arrows = {"normal":ARROWS.get_at((55, 33, 13, 29), False)}
        self.arrow = self.arrows["normal"]
        self.can = False
        self.timer = 3000
        self.name = "SG"
        self.effect_time = 3000

    def shoot(self, object):
        if self.shooting_timer == self.delay:
            if not self.can: return
            pas = self.passon
            if object in self.passedon: pas = False
            effect = None
            if self.passon == "ft" and pas: effect="icy"
            temp = Bullet(self.rect.center, 2, object.rect.center, \
                          self.creeps, self.arrow, self.damage, pas, \
                          self.passedon,effect)
            self.bullet_group.add(temp)
            if self.soundm!=None:
                self.soundm.play_sound("arrow")
            self.shooting_timer = 0
            self.can = False
        else:
            self.shooting_timer += 1


    def bonus(self):
        self.timer -= 2
        if self.timer <= 0:
            self.particle_emitter.add(Smoke(self.particle_emitter, \
                                            self.rect.center, 40))
            self.kill()
            return
        if len(self.available_creeps)!=0:
            if self.at == 0:
                self.at = 16
                if self.ai >= 2:
                    self.ai = 0; self.can = True;
                else: self.ai += 1
                if self.copy == None:
                    self.image = self.images[self.ai]
                else:
                    self.copy.image = self.images[self.ai]
            else: self.at -= 1
        elif len(self.available_creeps)==0 and self.ai!=0:
            self.ai = 0
            if self.copy == None:
                self.image = self.images[0]
            else:
                self.copy.image = self.images[0]
        m_time = pygame.rect.Rect((self.rect.x, self.rect.y-6), \
                                              (self.image.get_width(), 5))
        m_time.centerx = self.rect.centerx
        unit = (self.image.get_width()*self.timer)/ \
                self.effect_time
        time = pygame.rect.Rect((m_time.x, m_time.y), \
                                            (unit+1, 5))
        pygame.draw.rect(self.screen, (171, 155, 45), m_time)
        pygame.draw.rect(self.screen, (227, 205, 59), time)
        pygame.draw.rect(self.screen, (104, 96, 43), m_time, 1)


class IndianTent(Tower):

    def __init__(self, pos,screen, bullet_group, creep, bgt, player, pem, sound=None):
        Tower.__init__(self, pos, 200, screen, bullet_group, \
                       creep, bgt, player=player, particle_emitter=pem, soundm=sound)
        self.damage = 10
        self.delay = 13
        self.image = TOWERS.get_at((317, 14, 27, 39), True)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.t = ["water"]

    def update(self):
        if self.player.paused<0:
            return
        self.search()


class GoblinTower(Tower):

    def __init__(self, pos,screen, bullet_group, creep, bgt, player, pem, sound=None):
        Tower.__init__(self, pos, 80, screen, bullet_group, \
                       creep, bgt, player=player, particle_emitter=pem, soundm=sound)
        self.damage = 10
        self.delay = 13
        self.image = TOWERS.get_at((0, 65, 20, 58), True)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.t = ["ground"]
        self.see = True

    def update(self):
        if self.player.paused<0:
            return
        if self.see:
            self.search()


class IceTower(Tower):

    def __init__(self, pos,screen, bullet_group, creep, bgt, player, pem, sound=None):
        Tower.__init__(self, pos, 80, screen, bullet_group, \
                       creep, bgt, player=player, particle_emitter=pem, soundm=sound)
        self.damage = 10
        self.delay = 13
        self.image = TOWERS.get_at((24, 65, 27, 73), True)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.passon = "ft"
        self.t = ["ground"]
        self.see = True

    def update(self):
        if self.player.paused<0:
            return
        if self.see:
            self.search()


class BadassTower(Tower):

    def __init__(self, pos,screen, bullet_group, creep, bgt, player, pem, sound=None):
        Tower.__init__(self, pos, 130, screen, bullet_group, \
                       creep, bgt, player=player, particle_emitter=pem, soundm=sound)
        self.damage = 10
        self.delay = 13
        self.image = TOWERS.get_at((58, 63, 34, 124), True)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.passon = "ft"
        self.t = ["ground", "awesome"]
        self.see = True

    def update(self):
        if self.player.paused<0:
            return
        self.search()


class ArrowTower(Tower):

    def __init__(self, pos, range, screen, bullet_group, creeps, \
                 bgt, tiles, banned_tiles, player, particle_emitter, p=1, sound=None):
        Tower.__init__(self, pos, range, screen, bullet_group, \
                       creeps, bgt, tiles, banned_tiles, player, particle_emitter, p, sound)
        self.damage = 5
        self.delay = 14
        self.image = TOWERS.get_at((0, 0, 31, 54), True)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.price_gold = 20
        self.t = ["water","ground","air"]


class SpearTower(Tower):

    def __init__(self, pos, range, screen, bullet_group, creeps, \
                 bgt, tiles, banned_tiles, player, particle_emitter, p=1, sound=None):
        Tower.__init__(self, pos, range, screen, bullet_group, \
                       creeps, bgt, tiles, banned_tiles, player, particle_emitter, p, sound)
        self.damage = 8
        self.delay = 16
        self.image = TOWERS.get_at((71, 0, 30, 53), True)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.price_gold = 30
        self.arrows = {"normal":ARROWS.get_at((35, 0, 21, 5), False), \
                       "fire":ARROWS.get_at((57, 0, 21, 5), False)}
        self.arrow = self.arrows["normal"]


class DwarfMine(Tower):

    def __init__(self, pos, range, screen, bullet_group, creeps, \
                 bgt, tiles, banned_tiles, player, particle_emitter, p=1, sound=None):
        Tower.__init__(self, pos, range, screen, bullet_group, \
                       creeps, bgt, tiles, banned_tiles, player, particle_emitter, p, sound)
        self.damage = 11
        self.delay = 18
        self.gdelay = 200
        self.gt = 0
        self.image = TOWERS.get_at((34, 24, 36, 30), True)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.price_gold = 50
        self.arrows = {"normal":ARROWS.get_at((0, 6, 16, 13), False), \
                       "fire":ARROWS.get_at((17, 6, 18, 13), False)}
        self.arrow = self.arrows["normal"]

    def bonus(self):
        if self.player.lpassed: return
        if self.gt==self.gdelay:
            if self.show_p:
                self.particle_emitter.add(MCluster(self.rect.center, \
                                    3, self.particle_emitter, "g"))
            self.player["gold"]+=3
            self.gt = 0
        else:
            self.gt += 1


class Lighthouse(Tower):

    def __init__(self, pos, range, screen, bullet_group, creeps, \
                 bgt, tiles, banned_tiles, player, particle_emitter, p=1, sound=None):
        Tower.__init__(self, pos, range, screen, bullet_group, \
                       creeps, bgt, tiles, banned_tiles, player, particle_emitter, p, sound)
        self.damage = 10
        self.delay = 13
        self.image = TOWERS.get_at((103, 0, 30, 63), True)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.price_gold = 35
        self.arrows = {"normal":ARROWS.get_at((35, 0, 21, 5), False), \
                       "fire":ARROWS.get_at((57, 0, 21, 5), False)}
        self.arrow = self.arrows["normal"]
        self.t = ["water","ground"]


class Smallship(Tower):

    def __init__(self, pos, range, screen, bullet_group, creeps, \
                 bgt, tiles, banned_tiles, player, particle_emitter, p=1, sound=None):
        Tower.__init__(self, pos, range, screen, bullet_group, \
                       creeps, bgt, tiles, banned_tiles, player, particle_emitter, p, sound)
        self.damage = 6
        self.delay = 14
        self.image = TOWERS.get_at((172,3,23,40), True)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.price_gold = 25
        self.t = ["water"]
        self.c = [(42, 112, 96),(17, 71, 60)]

    def bonus(self):
        pass

    def on_collision(self, i):
        i.health -= 30
        if self.show_p:
            for i in xrange(15):
                self.particle_emitter.add(
                ImPart(self.rect.center, [random.uniform(0,1),random.uniform(0,1)],
                       random.choice(GORE),9), \
                ImPart(self.rect.center, [random.uniform(0,-1),random.uniform(0,1)],
                       random.choice(GORE),9), \
                ImPart(self.rect.center, [random.uniform(0,-1),random.uniform(0,-1)],
                       random.choice(GORE),9), \
                ImPart(self.rect.center, [random.uniform(0,1),random.uniform(0,-1)],
                       random.choice(GORE),9))
        self.alive = False
        if self.copy!=None: self.copy.kill()
        self.kill()


class Longship(Tower):

    def __init__(self, pos, range, screen, bullet_group, creeps, \
                 bgt, tiles, banned_tiles, player, particle_emitter, p=1, sound=None):
        Tower.__init__(self, pos, range, screen, bullet_group, \
                       creeps, bgt, tiles, banned_tiles, player, particle_emitter, p, sound)
        self.damage = 12
        self.delay = 18
        self.image = TOWERS.get_at((138, 0, 27, 49), True)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.price_gold = 50
        self.t = ["water"]
        self.c = [(42, 112, 96),(17, 71, 59)]

    def bonus(self):
        pass
        
    def on_collision(self, i):
        i.health -= 60
        if self.show_p:
            for i in xrange(15):
                self.particle_emitter.add(
                ImPart(self.rect.center, [random.uniform(0,1),random.uniform(0,1)],
                       random.choice(GORE),9), \
                ImPart(self.rect.center, [random.uniform(0,-1),random.uniform(0,1)],
                       random.choice(GORE),9), \
                ImPart(self.rect.center, [random.uniform(0,-1),random.uniform(0,-1)],
                       random.choice(GORE),9), \
                ImPart(self.rect.center, [random.uniform(0,1),random.uniform(0,-1)],
                       random.choice(GORE),9))
        self.alive = False
        if self.copy!=None: self.copy.kill()
        self.kill()



class RuneStone(Tower):

    def __init__(self, pos, range, screen, bullet_group, creeps, \
                 bgt, tiles, banned_tiles, player, particle_emitter, p=1, sound=None):
        Tower.__init__(self, pos, range, screen, bullet_group, \
                       creeps, bgt, tiles, banned_tiles, player, particle_emitter, p, sound)
        self.damage = 12
        self.delay = 17
        self.image = TOWERS.get_at((234, 14, 26, 46), True)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.price_gold = 65
        self.arrows = {"normal":ARROWS.get_at((36, 9, 19, 7), False)}
        self.arrow = self.arrows["normal"]
        self.immune = True
        self.t = ["ground", "air", "magic"]


class ElfTree(Tower):

    def __init__(self, pos, range, screen, bullet_group, creeps, \
                 bgt, tiles, banned_tiles, player, particle_emitter, p=1, sound=None):
        Tower.__init__(self, pos, range, screen, bullet_group, \
                       creeps, bgt, tiles, banned_tiles, player, particle_emitter, p, sound)
        self.damage = 15
        self.delay = 19
        self.image = TOWERS.get_at((264, 5, 47, 56), True)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.price_gold = 75
        self.arrows = {"normal":ARROWS.get_at((56, 10, 16, 5), False)}
        self.arrow = self.arrows["normal"]
        self.immune = True
        self.t = ["ground", "air", "magic"]


class AsgardTower(Tower):

    def __init__(self, pos, range, screen, bullet_group, creeps, \
                 bgt, tiles, banned_tiles, player, particle_emitter, p=1, sound=None):
        Tower.__init__(self, pos, range, screen, bullet_group, \
                       creeps, bgt, tiles, banned_tiles, player, particle_emitter, p, sound)
        self.damage = 25
        self.delay = 21
        self.image = TOWERS.get_at((205, 4, 22, 55), True)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.price_gold = 90
        self.arrows = {"normal":ARROWS.get_at((76, 6, 10, 10), False)}
        self.arrow = self.arrows["normal"]
        self.immune = True
        self.t = ["ground", "air", "water", "magic"]
