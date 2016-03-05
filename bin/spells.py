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
import random
import math

from particles import *
from helpers   import Sheet, load_image

ARROWS = Sheet("./data/image/objects/arrows.png")
LIGHT = [ARROWS.get_at((0,20,18,63),True),ARROWS.get_at((20,20,18,63),True)]
SW = ARROWS.get_at((59,19,30,11),True)
ICONS =  Sheet("./data/image/menu/buttons.png")
SH = ICONS.get_at((102, 69, 26, 26),True)
SH.set_colorkey((128,128,128))
PARTPIC = Sheet("./data/image/environment/particles.png")
MAGIC = [PARTPIC.get_at((0,6,7,7),True), PARTPIC.get_at((8,6,5,5),True), \
         PARTPIC.get_at((14,6,5,5),True)]
PUP = Sheet("./data/image/objects/magic.png")

class Spell(pygame.sprite.Sprite):
    
    def __init__(self, pos, player, particle_emitter, screen, target, size, soundm):
        pygame.sprite.Sprite.__init__(self)
        self.player = player
        self.particle_emitter = particle_emitter
        self.screen = screen
        self.target = target
        self.image = pygame.surface.Surface(size)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.placed = False
        self.price = 0
        self.targeted = []
        self.effect_time = 30
        self.timer = self.effect_time
        self.enchanted = False
        self.image.fill((0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        self.color = (0, 255, 10)
        self.was = False
        self.a = 0
        self.pic = ICONS.get_at((3,3,1,1),True).convert()
        self.pic_r = self.pic.get_rect()
        self.immunity = False
        self.flashy = True
        self.override = False
        self.soundm = soundm
        self.buffsound = "spell"

    def effect(self):
        if self.was and self.a<=30:
            return
        if self.flashy:
            t = self.targeted[0]
            x = t.rect.centerx
            y = t.rect.centery + t.image.get_height()/2
            self.particle_emitter.add(ImPart([x,y], [random.uniform(-0.5,0.5), -0.5],
            random.choice(MAGIC), 10))
        if not self.was:
            self.a += 10
            self.pic.set_alpha(self.a)
            if self.a>=250:
                self.was = True
        elif self.was and self.a>30:
            self.a -= 10
            self.pic.set_alpha(self.a)
        self.screen.blit(self.pic,self.pic_r)

    def buff(self):
        """
        Do some magic crap.
        """
        pass
   
    def undo_buff(self):
        """
        Undo some magic crap.
        """
        pass

    def start_effect(self):
        """
        Particle fun
        """
        pass

    def hide(self):
        """
        Hides spell. It's still active,
        but it doesn't show it
        """
        self.image = pygame.surface.Surface((25, 25))
        self.image.fill((0, 0, 0))
        self.image.set_colorkey((0, 0, 0))

    def place(self):
        """
        Place the spell if player has enough magicka,
        and collision requirements are OK
        """
        self.image.fill((0, 0, 0))
        self.image.set_colorkey((0, 0, 0))

        pos = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        self.rect.center = pos
        
        # Checks if colliding with target(s)
        col_1 = pygame.sprite.spritecollide(self, self.target, False)

        if not col_1:
            self.color = (255, 10, 10)
        else:
            self.color = (0, 255, 10)

        pygame.draw.ellipse(self.screen, self.color, self.rect, 1)
        
        if click[0] == 1:
            # When all requirements are valid, place the spell
            # and take magicka from player
            if col_1:
                if not self.player["magicka"] < self.price:
                    for target in col_1:
                        if self.immunity and target.immune:
                            temp = Error([target.rect.x, target.rect.y-8], \
                                         20, (255, 255, 255), "IMMUNE TO SPELL")
                            self.particle_emitter.add(temp)
                            break                        
                        if target.enchanted:
                            temp = Error([target.rect.x, target.rect.y-8], \
                                         [0, -0.1], 20, (255, 255, 255), "ALREADY ENCHANTED", \
                                         25)
                            self.particle_emitter.add(temp)
                        elif not target.enchanted or self.override:
                            self.placed = True   
                            self.player.buying = False
                            self.player["magicka"] -= self.price
                            self.player.sp += 1
                            self.targeted.append(target)
                            self.pic_r.center = target.rect.center
                            self.start_effect()
                            self.soundm.play_sound(self.buffsound)
                            break

                elif self.player["magicka"] < self.price:
                    temp = Error([self.rect.x, self.rect.y-8], \
                                  20, (255, 255, 255), "INSUFFICIENT RESOURCES!")
                    self.particle_emitter.add(temp)

            elif not col_1 :
                temp = Error([self.rect.x, self.rect.y-8], 20, \
                             (255, 255, 255), "CAN'T FIND A TARGET!")
                self.particle_emitter.add(temp)
    
        # If player has clicked RMB, cancel the spell
        if click[2] == 1:
            self.player.buying = False
            self.kill()

    def optional(self):
        pass

    def update(self):
        if self.player.paused<0:
            return
        if not self.placed:
            self.place()
        else:
            if not self.enchanted:
                self.buff()
                self.enchanted = True
            else:
                # For Meteor
                self.optional()
                self.effect()
                if not self.timer == 0:
                    self.timer -= 1

                else:
                    self.timer = 0
                    self.undo_buff()

                for tower in self.targeted:
                    # Draw the timebar
                    m_time = pygame.rect.Rect((tower.rect.x, tower.rect.y-6), \
                                              (tower.image.get_width(), 5))
                    m_time.centerx = tower.rect.centerx
                    unit = (tower.image.get_width()*self.timer)/ \
                            self.effect_time
                    time = pygame.rect.Rect((m_time.x, m_time.y), \
                                            (unit+1, 5))
                    pygame.draw.rect(self.screen, (171, 155, 45), m_time)
                    pygame.draw.rect(self.screen, (227, 205, 59), time)
                    pygame.draw.rect(self.screen, (104, 96, 43), m_time, 1)


class Kill(Spell):

    def __init__(self, pos, player, particle_emitter, screen, target, size=(50, 23), sound=None):
        Spell.__init__(self, pos, player, particle_emitter, screen, target, size, sound)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.effect_time = 0
        self.timer = self.effect_time
        self.price = 5
        self.previous_val = []
        self.flashy = False

    def start_effect(self):
        self.particle_emitter.add(Smoke(self.particle_emitter, self.rect.center,
        40))

    def buff(self):
        # Changes the values of targeted towers and saves
        # default ones
        for n in xrange(len(self.targeted)):
            tower = self.targeted[n]
            self.player["gold"] += tower.price_gold/2
            if tower.copy!=None: tower.copy.kill()
            tower.kill()
        self.hide()

    def undo_buff(self):
        # Returns values of targeted towers to default
        # ones, does harakiri
        self.targeted = []
        self.kill()


class TyrStaff(Spell):

    def __init__(self, pos, player, particle_emitter, screen, target, size=(50, 23), sound=None):
        Spell.__init__(self, pos, player, particle_emitter, screen, target, size, sound)
        self.effect_time = 0
        self.timer = self.effect_time
        self.price = 0
        self.previous_val = []
        self.flashy = False
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.pup = True

    def buff(self):
        for n in xrange(len(self.targeted)):
            tower = self.targeted[n]
            tower.rage = True
            self.image = PARTPIC.get_at((0,81,37,25), True)
            self.rect = self.image.get_rect()
            self.rect.centerx = tower.rect.centerx
            self.rect.centery = tower.rect.centery + tower.image.get_height()/2 - 5
        self.player.charges -= 1

    def undo_buff(self):
        self.targeted = []


class LStaff(Kill):

    def __init__(self, pos, player, particle_emitter, screen, target, size=(50, 23), sound=None):
        Kill.__init__(self, pos, player, particle_emitter, screen, target, size, sound)
        self.flashy = False
        self.price = 0

    def buff(self):
        for n in xrange(len(self.targeted)):
            tower = self.targeted[n]
            self.player["magicka"] += tower.price_gold
            if tower.copy!=None: tower.copy.kill()
            tower.kill()
        self.player.charges -= 1
        self.hide()


class SpeedUp(Spell):

    def __init__(self, pos, player, particle_emitter, screen, target, size=(50, 23), sound=None):
        Spell.__init__(self, pos, player, particle_emitter, screen, target, size, sound)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.effect_time = 300
        self.timer = self.effect_time
        self.price = 10
        self.previous_val = []
        self.pic = ICONS.get_at((36,36,26,26),True).convert()
        self.pic.set_alpha(0)
        self.pic_r = self.pic.get_rect()

    def buff(self):
        # Changes the values of targeted towers and saves
        # default ones
        for n in xrange(len(self.targeted)):
            tower = self.targeted[n]
            self.previous_val.append([tower.delay])
            tower.delay -= tower.delay/4
            tower.shooting_timer = 0
            tower.enchanted = True
        self.hide()

    def undo_buff(self):
        # Returns values of targeted towers to default
        # ones, does harakiri
        for n in xrange(len(self.targeted)):
            tower = self.targeted[n]
            tower.delay = self.previous_val[n][0]
            tower.enchanted = False

        self.previous_val = self.targeted = []
        self.kill()

class Eye(Spell):

    def __init__(self, pos, player, particle_emitter, screen, target, size=(50, 23), sound=None):
        Spell.__init__(self, pos, player, particle_emitter, screen, target, size, sound)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.effect_time = 300
        self.timer = self.effect_time
        self.price = 10
        self.previous_val = []
        self.pic = ICONS.get_at((69,36,26,26),True).convert()
        self.pic.set_alpha(0)
        self.pic_r = self.pic.get_rect()

    def buff(self):
        # Changes the values of targeted towers and saves
        # default ones
        for n in xrange(len(self.targeted)):
            tower = self.targeted[n]
            self.previous_val.append([tower.range])
            tower.range += tower.range/2
            tower.enchanted = True
            if tower.copy!=None: tower.copy.range = tower.range
        self.hide()

    def undo_buff(self):
        # Returns values of targeted towers to default
        # ones, does harakiri
        for n in xrange(len(self.targeted)):
            tower = self.targeted[n]
            tower.range = self.previous_val[n][0]
            tower.enchanted = False
            if tower.copy!=None: tower.copy.range = tower.range

        self.previous_val = self.targeted = []
        self.kill()


class FireArrows(Spell):

    def __init__(self, pos, player, particle_emitter, screen, target, size=(50, 23), sound=None):
        Spell.__init__(self, pos, player, particle_emitter, screen, target, size, sound)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.effect_time = 200
        self.timer = self.effect_time
        self.price = 20
        self.previous_val = []
        self.pic = ICONS.get_at((168,36,26,26),True).convert()
        self.pic.set_alpha(0)
        self.pic_r = self.pic.get_rect()
        self.immunity = True

    def buff(self):
        # Changes the values of targeted towers and saves
        # default ones
        for n in xrange(len(self.targeted)):
            tower = self.targeted[n]
            self.previous_val.append([tower.damage])
            tower.damage += 5
            tower.arrow = tower.arrows["fire"]
            tower.enchanted = True
        self.hide()

    def undo_buff(self):
        # Returns values of targeted towers to default
        # ones, does harakiri
        for n in xrange(len(self.targeted)):
            tower = self.targeted[n]
            tower.damage = self.previous_val[n][0]
            tower.arrow = tower.arrows["normal"]
            tower.enchanted = False

        self.previous_val = self.targeted = []
        self.kill()


class Frost(Spell):

    def __init__(self, pos, player, particle_emitter, screen, target, size=(50, 23), sound=None):
        Spell.__init__(self, pos, player, particle_emitter, screen, target, size, sound)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.effect_time = 200
        self.timer = self.effect_time
        self.price = 25
        self.previous_val = []
        self.pic = ICONS.get_at((201,36,26,26),True).convert()
        self.pic.set_alpha(0)
        self.pic_r = self.pic.get_rect()
        self.immunity = True

    def buff(self):
        for n in xrange(len(self.targeted)):
            tower = self.targeted[n]
            self.previous_val.append([tower.passon])
            tower.passon = "ft"
            tower.enchanted = True
        self.player.charges -= 1
        self.hide()

    def undo_buff(self):
        for n in xrange(len(self.targeted)):
            tower = self.targeted[n]
            tower.passon = self.previous_val[n][0]
            tower.enchanted = False

        self.previous_val = self.targeted = []
        self.kill()


class Poison(Spell):

    def __init__(self, pos, player, particle_emitter, screen, target, size=(50, 23), sound=None):
        Spell.__init__(self, pos, player, particle_emitter, screen, target, size, sound)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.effect_time = 200
        self.timer = self.effect_time
        self.price = 30
        self.previous_val = []
        self.pic = ICONS.get_at((234,36,26,26),True).convert()
        self.pic.set_alpha(0)
        self.pic_r = self.pic.get_rect()
        self.immunity = True

    def buff(self):
        for n in xrange(len(self.targeted)):
            tower = self.targeted[n]
            self.previous_val.append([tower.passon])
            tower.passon = "pt"
            tower.enchanted = True
        self.hide()

    def undo_buff(self):
        for n in xrange(len(self.targeted)):
            tower = self.targeted[n]
            tower.passon = self.previous_val[n][0]
            tower.enchanted = False

        self.previous_val = self.targeted = []
        self.kill()


class Meteor(pygame.sprite.Sprite):

    def __init__(self, pos, radius, target, screen, player, deg=0):
        pygame.sprite.Sprite.__init__(self)
        self.pos = pos
        self.image = ARROWS.get_at((17, 6, 18, 13), False)
        self.rect = self.image.get_rect()
        self.deg = deg
        self.r = radius
        if deg==0:
            self.rect.centerx = pos[0]
            self.rect.centery = pos[1]
        else:
            rad = self.deg*math.pi/180
            velx = math.sin(rad)*self.r
            vely = math.cos(rad)*self.r
            self.rect.centerx = self.pos[0]+velx
            self.rect.centery = self.pos[1]-vely
        self.hit = []
        self.target = target
        self.lol = self.image.copy()
        self.lol.set_alpha(50)
        self.player = player
        self.screen = screen

    def update(self):
        if self.player.paused < 0:
            return
        col = pygame.sprite.spritecollide(self, self.target, False)
        if not col: self.hit = []
        for i in col:
            if not i in self.hit:
                self.hit.append(i)
                i.health -= 15
        self.deg += 2
        rad = self.deg*math.pi/180
        velx = math.sin(rad)*self.r
        vely = math.cos(rad)*self.r
        self.rect.centerx = self.pos[0]+velx
        self.rect.centery = self.pos[1]-vely
        self.screen.blit(self.lol, self.rect)


class Orbiting(Spell):

    def __init__(self, pos, player, particle_emitter, screen, target, size=(50, 23), sound=None):
        Spell.__init__(self, pos, player, particle_emitter, screen, target, size, sound)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.effect_time = 200
        self.timer = self.effect_time
        self.price = 50
        self.previous_val = []
        self.pic = ICONS.get_at((300,36,26,26),True).convert()
        self.pic.set_alpha(0)
        self.pic_r = self.pic.get_rect()
        self.met1 = None
        self.met2 = None

    def optional(self):
        if self.met1 and self.met2:
            self.met1.update()
            self.met2.update()

    def buff(self):
        for n in xrange(len(self.targeted)):
            tower = self.targeted[n]
            self.previous_val.append([tower.passon])
            g = None
            for i in self.groups(): g = i
            self.met1 = Meteor([tower.rect.centerx, tower.rect.centery], \
                              tower.range, tower.creeps, self.screen, self.player, 0)
            self.met2 = Meteor([tower.rect.centerx, tower.rect.centery], \
                              tower.range, tower.creeps, self.screen, self.player, 180)
            g.add(self.met1,self.met2)
            tower.enchanted = True

    def undo_buff(self):
        for n in xrange(len(self.targeted)):
            tower = self.targeted[n]
            tower.enchanted = False
        self.met1.kill()
        self.met2.kill()
        self.targeted = []
        self.kill()


class AutoThunder(pygame.sprite.Sprite):

    def __init__(self, particle_emitter, target, player):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.surface.Surface((150,150))
	self.image.fill((0,0,0))
        self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.player = player
        self.rect.y = 0
        self.particle_emitter = particle_emitter
        self.shoot_timer = 250
        self.target = target
    
    def place(self):
        if len(self.target)==0:
            self.shoot_timer = 250
            return
        c = random.choice(self.target.sprites())
        self.rect.center = c.rect.center

    def update(self):
        if self.player.paused < 0:
            return
        if self.shoot_timer <= 0:
            self.place()
            col = pygame.sprite.spritecollide(self, self.target, False)
            for creep in col:
                if creep.rect.y <0: continue
                self.particle_emitter.add(Lightning([creep.rect.centerx, \
                creep.rect.centery-15],self.target,creep.id, self.player))
            self.shoot_timer = 250
        else: self.shoot_timer -= 1
   
class Lightning(pygame.sprite.Sprite):
    
    def __init__(self, pos, bastards, bid, player):
        pygame.sprite.Sprite.__init__(self)
        self.images = LIGHT
        self.image = pygame.surface.Surface((1,1))
        self.image.fill((0,0,0))
        self.image.set_colorkey((0,0,0))
        self.t = 3
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.aind = -1
        self.bid = bid
        self.player = player
        self.bastards = bastards

    def update(self):
        if self.player.paused < 0:
            return
        if self.t==0:
            self.t=3
            if self.aind==1:
                self.kill()
                return
            self.aind += 1
            oldc = self.rect.center
            self.image = self.images[self.aind]
            self.rect = self.image.get_rect(center=oldc)
            col = pygame.sprite.spritecollide(self, self.bastards, False)
            for creep in col:
                if creep.id == self.bid:
                    creep.health-=25
        else:
            self.t-=1


class Thunder(Spell):

    def __init__(self, pos, player, particle_emitter, screen, target, size=(150, 150), sound=None):
        Spell.__init__(self, pos, player, particle_emitter, screen, target, size, sound)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.effect_time = 0
        self.timer = self.effect_time
        self.price = 75
        self.previous_val = []
        self.pic = ICONS.get_at((234,36,26,26),True).convert()
        self.pic.set_alpha(0)
        self.pic_r = self.pic.get_rect()
        self.override = False
        self.flashy = False
        self.buffsound = "lightning"

    def place(self):
        """
        Place the spell if player has enough magicka,
        and collision requirements are OK
        """
        self.image.fill((0, 0, 0))
        self.image.set_colorkey((0, 0, 0))

        pos = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        self.rect.center = pos

        # Checks if colliding with target(s)
        col_1 = pygame.sprite.spritecollide(self, self.target, False)

        if not col_1:
            self.color = (255, 10, 10)
        else:
            self.color = (0, 255, 10)

        pygame.draw.ellipse(self.screen, self.color, self.rect, 1)

        if pos[1] >= 600: return #User can't accidentally place spells
        if click[0] == 1:
            if col_1:
                if not self.player["magicka"] < self.price:
                    self.placed = True   
                    self.player.buying = False
                    self.player.sp += 1
                    self.player["magicka"] -= self.price
                    for target in col_1:    
                        self.targeted.append(target)
                        self.pic_r.center = target.rect.center
                        self.start_effect()
                        if self.override: break

                elif self.player["magicka"] < self.price:
                    temp = Error([self.rect.x, self.rect.y-8], \
                                  20, (255, 0, 0), "INSUFFICIENT RESOURCES!")
                    self.particle_emitter.add(temp)

            elif not col_1 :
                temp = Error([self.rect.x, self.rect.y-8], 20, \
                             (255, 0, 0), "CAN'T FIND A TARGET!")
                self.particle_emitter.add(temp)
        if click[2] == 1:
            self.player.buying = False
            self.kill()

    def buff(self):
        for n in xrange(len(self.targeted)):
            creep = self.targeted[n]
            self.particle_emitter.add(Lightning([creep.rect.centerx, \
            creep.rect.centery-15],self.target,creep.id,self.player))
        self.hide()

    def undo_buff(self):
        self.previous_val = self.targeted = []
        self.kill()


class Sword(Thunder):
    def __init__(self, pos, player, particle_emitter, screen, target, size=(25, 25), sound=None):
        Spell.__init__(self, pos, player, particle_emitter, screen, target, size, sound)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.effect_time = 0
        self.timer = self.effect_time
        self.price = 55
        self.previous_val = []
        self.override = True
        self.flashy = False
        self.buffsound = "swords"

    def buff(self):
        for n in xrange(len(self.targeted)):
            creep = self.targeted[n]
            self.particle_emitter.add(Bullet2([creep.rect.centerx,\
            creep.rect.centery-50],5,creep.rect.center,self.target,SW, \
            25,creep.id,0,False))
            self.particle_emitter.add(Bullet2([creep.rect.centerx,\
            creep.rect.centery-50],5,creep.rect.center,self.target,SW, \
            25,creep.id,90,False))
            self.particle_emitter.add(Bullet2([creep.rect.centerx,\
            creep.rect.centery-50],5,creep.rect.center,self.target,SW, \
            25,creep.id,180,False))
            self.particle_emitter.add(Bullet2([creep.rect.centerx,\
            creep.rect.centery-50],5,creep.rect.center,self.target,SW, \
            25,creep.id,270,False))
        self.hide()

    def undo_buff(self):
        self.previous_val = self.targeted = []
        self.kill()


class Confusion(Thunder):
    def __init__(self, pos, player, particle_emitter, screen, target, size=(200, 200), sound=None):
        Spell.__init__(self, pos, player, particle_emitter, screen, target, size, sound)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.effect_time = 0
        self.timer = self.effect_time
        self.price = 100
        self.previous_val = []
        self.override = False
        self.flashy = False

    def buff(self):
        for n in xrange(len(self.targeted)):
            creep = self.targeted[n]
            if creep.point!=0:
                creep.point-=1
                creep.back = True
        self.hide()

    def undo_buff(self):
        self.previous_val = self.targeted = []
        self.kill()


class JHeart(Thunder):
    def __init__(self, pos, player, particle_emitter, screen, target, size=(200, 200), sound=None):

        Spell.__init__(self, pos, player, particle_emitter, screen, target, size, sound)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.effect_time = 0
        self.timer = self.effect_time
        self.price = 0
        self.previous_val = []
        self.override = False
        self.flashy = False

    def buff(self):
        for n in xrange(len(self.targeted)):
            creep = self.targeted[n]
            if creep.clist["jt"] != True and creep.clist["ft"] != True:
                creep.clist["jt"] = True
                w, h = creep.image.get_size()
                r = pygame.Rect(0, 0, w, h)
                self.particle_emitter.add(ImPart(creep.rect.center, [0,0], \
                                      FROZEN.get_at(r,True), 60, onFall=True))
        self.player.charges -= 1
        self.kill()

    def undo_buff(self):
        self.previous_val = self.targeted = []
        self.kill()


class Spikes(pygame.sprite.Sprite):

    def __init__(self, pos, creeps):
        pygame.sprite.Sprite.__init__(self)
        self.images = [PUP.get_at((0,0,26,23), True), \
                       PUP.get_at((33,0,26,23), True), \
                       PUP.get_at((65,0,26,23), True), \
                       PUP.get_at((97,0,26,23), True), \
                       PUP.get_at((129,0,26,23), True)]
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.cr = creeps
        self.done = []
        self.at = 0
        self.i = 0
        self.a = 255
        self.start = False

    def update(self):
        key = pygame.key.get_pressed()
        if key[pygame.K_SPACE] and not self.start:
            self.start = True
        if not self.start: return
        if self.at < 3: self.at += 1
        if self.at == 2 and self.i != 4:
            self.i += 1
            self.at = 0
            self.image = self.images[self.i].convert()
            if self.i == 1:
                col = pygame.sprite.spritecollide(self, self.cr, False)
                for creep in col:
                   if not creep.id in self.done:
                       creep.health -= 30
                       self.done.append(creep.id)
        elif self.at >= 2 and self.i == 4:
            self.a -= 15
            if self.a < 80: 
                self.kill()
            self.image.set_alpha(self.a)


class Spiky(Thunder):

    def __init__(self, pos, player, particle_emitter, screen, targets, size=(32, 32), sound=None):

        Thunder.__init__(self, pos, player, particle_emitter, screen, targets[0], size, sound)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.effect_time = 0
        self.timer = self.effect_time
        self.price = 0
        self.previous_val = []
        self.override = False
        self.flashy = False
        self.cr = targets[1]

    def buff(self):
        g = self.groups()[0]
        x, y = self.rect.x, self.rect.y
        g.add(Spikes(self.rect.center, self.cr))
        self.player.charges -= 1
        self.kill()
        self.hide()

    def undo_buff(self):
        self.previous_val = self.targeted = []
        self.kill()


class Whirpool(pygame.sprite.Sprite):

    def __init__(self, pos, creeps, screen):
        pygame.sprite.Sprite.__init__(self)
        self.images = [PUP.get_at((0,29,35,23), True), \
                       PUP.get_at((36,29,35,23), True), \
                       PUP.get_at((72,29,35,23), True), \
                       PUP.get_at((108,29,35,23), True)]
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.cr = creeps
        self.screen = screen
        self.done = []
        self.at = 0
        self.i = 0
        self.start = False
        self.timer = 400
        self.effect_time = 400

    def update(self):
        if self.timer <= 0:
            self.kill() 
            return
        else:
            self.timer -= 1
        if self.at < 6: self.at += 1
        if self.at <= 5:
            if self.i <= 2: self.i += 1
            else: self.i = 0
            self.at = 0
            self.image = self.images[self.i].convert()
        col = pygame.sprite.spritecollide(self, self.cr, False)
        for creep in col:
            if creep.rect.centery < self.rect.centery:
                creep.health -= 1
                self.done.append(creep.id)
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


class Whiry(Spiky):

    def __init__(self, pos, player, particle_emitter, screen, targets, size=(35, 23), sound=None):
        Spiky.__init__(self, pos, player, particle_emitter, screen, targets, size, sound=None)
        
    def buff(self):
        g = self.groups()[0]
        x, y = self.rect.x, self.rect.y
        g.add(Whirpool(self.rect.center, self.cr, self.screen))
        self.player.charges -= 1
        self.kill()
        self.hide()

class ThorsThingie(pygame.sprite.Sprite):
    def __init__(self, pos, goal, creeps, pemit, player):
        pygame.sprite.Sprite.__init__(self)
        self.goal = goal
        self.creeps = creeps
        self.image = load_image("./data/image/objects/mchammer.png")
        self.rect = self.image.get_rect()
        self.rect.centerx = pos[0]
        self.rect.centery = pos[1]
        self.speed = 1
        self.particle_emitter = pemit
        self.player = player
    
    def update(self):
        if self.player.paused < 0:
            return
        col = pygame.sprite.spritecollide(self, self.creeps, False)
        if self.rect.centery>=(self.goal[1]-64):
            if col:
                for i in col:
                    i.health -= 100
            height = self.image.get_height()
            for i in xrange(32):
                    speed_x = self.rect.x+2*i
                    self.particle_emitter.add(  
                    Particle([speed_x, self.rect.y+height], [ \
                    random.uniform(-0.5, 0), -1], \
                    random.randrange(1, 3), (109, 90, 57), 6, 0.7), 
                    Particle([speed_x+4, self.rect.y+height], [ \
                    random.uniform(0, 0.5), -1], \
                    random.randrange(1, 3), (85, 162, 10), 6, 0.7))
            self.kill()
        else:
            self.rect.centery+=self.speed
            self.speed += 1


class Hammer(Thunder):

    def __init__(self, pos, player, particle_emitter, screen, target, size=(64, 64), sound=None):
        Spell.__init__(self, pos, player, particle_emitter, screen, target, size, sound)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.effect_time = 0
        self.timer = self.effect_time
        self.price = 150
        self.previous_val = []
        self.override = False
        self.flashy = False
        self.buffsound = "hammer"

    def buff(self):
        self.particle_emitter.add(ThorsThingie([self.rect.centerx, \
        self.rect.centery-264], self.rect.center, self.target, self.particle_emitter, self.player))
        self.hide()

    def undo_buff(self):
        self.previous_val = self.targeted = []
        self.kill()


class Wave(pygame.sprite.Sprite):
    
    def __init__(self, pos, bastards, power, screen, sound, player):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.surface.Surface((128,128))
        self.image.set_alpha(0)
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.bastards = bastards
        self.power = power
        self.scr = screen
        self.rot = 0
        self.rsp = 1
        self.im = SH.convert()
        self.imr = self.im.get_rect()
        self.imr.center = pos
        self.a = 0
        self.flashing = False
        self.flash = pygame.surface.Surface((1024,640))
        self.flash.fill((0,252,255))
        self.flash.set_alpha(0)
        self.s = sound
        self.player = player

    def update(self):
        if self.player.paused < 0:
            return
        if self.rot>=180 and self.a<=0 and self.flashing:
            self.kill()
        if self.rot<180:
            self.rot = self.rsp
            c = self.imr.center
            self.im = pygame.transform.rotate(SH, self.rot)
            self.im.set_colorkey(self.im.get_at((0,0)))
            self.imr = self.im.get_rect()
            self.imr.center= c
            self.rsp += 5
            self.scr.blit(self.im, self.imr)
        else:
            if not self.flashing:
                self.flashing = True
                self.flash.set_alpha(255)
                self.a = 255
                col = pygame.sprite.spritecollide(self, self.bastards, False)
                for creep in col:
                    creep.health -= self.power*10
                self.s.play_sound("shockwave")
            else:
                self.a -= 50
                self.flash.set_alpha(self.a)
            self.scr.blit(self.flash, (0,0))


class Shockwave(Thunder):

    def __init__(self, pos, player, particle_emitter, screen, target, size=(128, 128), sound=None):
        Spell.__init__(self, pos, player, particle_emitter, screen, target, size, sound)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.effect_time = 0
        self.timer = self.effect_time
        self.price = 200
        self.previous_val = []
        self.override = False
        self.flashy = False
        self.buffsound = None

    def place(self):
        """
        Place the spell if player has enough magicka,
        and collision requirements are OK
        """
        self.image.fill((0, 0, 0))
        self.image.set_colorkey((0, 0, 0))

        pos = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        self.rect.center = pos

        # Checks if colliding with target(s)
        col_1 = pygame.sprite.spritecollide(self, self.target, False)

        if not col_1:
            self.color = (255, 10, 10)
        else:
            self.color = (0, 255, 10)

        pygame.draw.ellipse(self.screen, self.color, self.rect, 1)

        if click[0] == 1:
            if col_1:
                if not self.player["magicka"] < self.price and self.player.killed>0:
                    self.placed = True   
                    self.player.buying = False
                    self.player["magicka"] -= self.price
                    self.player.sp += 1
                    for target in col_1:    
                        self.targeted.append(target)
                        self.pic_r.center = target.rect.center
                        self.start_effect()
                        if self.override: break

                elif self.player["magicka"] < self.price:
                    temp = Error([self.rect.x, self.rect.y-8], \
                                  20, (255, 0, 0), "INSUFFICIENT RESOURCES!")
                    self.particle_emitter.add(temp)
                elif self.player.killed<1:
                    temp = Error([self.rect.x, self.rect.y-8], \
                                  20, (255, 0, 0), "INSUFFICIENT KILLS!")
                    self.particle_emitter.add(temp)

            elif not col_1 :
                temp = Error([self.rect.x, self.rect.y-8], 20, \
                             (255, 0, 0), "CAN'T FIND A TARGET!")
                self.particle_emitter.add(temp)
        if click[2] == 1:
            self.player.buying = False
            self.kill()

    def buff(self):
        power = self.player.killed
        self.particle_emitter.add(Wave(self.rect.center, self.target, \
                                       power, self.screen, self.sound, self.player))
        self.hide()

    def undo_buff(self):
        self.previous_val = self.targeted = []
        self.kill()


class Flame(pygame.sprite.Sprite):

    def __init__(self, creeps, player, cursor):
        pygame.sprite.Sprite.__init__(self)
        self.p = 0
        arrow = PUP.get_at((86,58,20,13),True)
        self.arrows = [arrow, pygame.transform.rotate(arrow, 90), \
                       pygame.transform.rotate(arrow, 180), \
                       pygame.transform.rotate(arrow, 270)]
        self.images = [PUP.get_at((9,53,20,28),True), \
                       PUP.get_at((30,53,20,28),True), \
                       PUP.get_at((51,53,20,28),True)]
        self.i = 0
        self.ai = 3
        self.image = arrow
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0
        self.cr = creeps
        self.placed = False
        self.player = player
        self.cursor = cursor
        self.cursor.visible = False
        self.speed = [0, 0]
        self.done = []

    def prepare(self):
        oc = self.rect.center
        if self.p==1:
            self.rect = self.image.get_rect(center=oc)
            self.speed[1] = -3
            self.rect.y = 640
        elif self.p==0:
            for i in xrange(len(self.images)):
                self.images[i] = pygame.transform.rotate(self.images[i], 270)
            self.rect = self.image.get_rect(center=oc)
            self.speed[0] = 3
            self.rect.x = 0
        elif self.p==3:
            for i in xrange(len(self.images)):
                self.images[i] = pygame.transform.rotate(self.images[i], 180)
            self.rect = self.image.get_rect(center=oc)
            self.speed[1] = 3
            self.rect.y = 0
        elif self.p==2:
            for i in xrange(len(self.images)):
                self.images[i] = pygame.transform.rotate(self.images[i], 90)
            self.rect = self.image.get_rect(center=oc)
            self.speed[0] = -3
            self.rect.x = 1024
        self.image = self.images[0]

    def place(self):
        pos = pygame.mouse.get_pos()
        if pos[1] >= 600: return
        self.rect.centerx = pos[0]
        self.rect.centery = pos[1]
        click = pygame.mouse.get_pressed()
        event = pygame.event.poll()
        if event.type == pygame.MOUSEBUTTONUP:
            if self.p == 3: self.p = 0
            else: self.p += 1
        elif event.type == pygame.MOUSEBUTTONDOWN:
            oc = self.rect.center
            if self.p == 0: self.p = 3
            else: self.p -= 1
        oc = self.rect.center
        self.image = self.arrows[self.p]
        self.rect = self.image.get_rect(center=oc)
        if click[0]==1:
            self.player.buying = False
            self.placed = True
            self.player.charges -= 1
            self.cursor.visible = True
            self.prepare()
        elif click[2]==1:
            self.player.buying = False
            self.cursor.visible = True
            self.kill()

    def update(self):
        if not self.placed:
            self.place()
        else:
            if self.p == 1 and self.rect.y <= 0:
                self.kill() 
            elif self.p == 3 and self.rect.y >= 632:
                self.kill()
            elif self.p == 0 and self.rect.x >= 1024:
                self.kill()
            elif self.p == 2 and self.rect.x <= 0:
                self.kill()
            col = pygame.sprite.spritecollide(self, self.cr, False)
            for creep in col:
                if not creep.id in self.done: 
                    creep.health -= 45; self.done.append(creep.id)
            if self.ai == 0:
                if self.i < 2: self.i += 1
                else: self.i = 0
                self.ai = 3
            else: self.ai -= 1
            self.image = self.images[self.i]
            self.rect.x += self.speed[0]*3
            self.rect.y += self.speed[1]*3
