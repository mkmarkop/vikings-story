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

from helpers       import Sheet
from particles     import *

PARTPIC = Sheet("./data/image/environment/particles.png")
GORE = [PARTPIC.get_at((7,0,5,5),True), PARTPIC.get_at((13,0,6,5),True), \
        PARTPIC.get_at((20,0,5,5),True)]
GORE1 = [PARTPIC.get_at((40,3,5,5), True), PARTPIC.get_at((36,13,6,4), True), \
        PARTPIC.get_at((42,19,2,6), True), PARTPIC.get_at((33,19,6,6), True)] 
TOXIC = [PARTPIC.get_at((0,14,5,5),True), PARTPIC.get_at((6,14,7,7),True), \
        PARTPIC.get_at((14,14,7,7),True), PARTPIC.get_at((22,14,7,7),True)]
WAVED = [PARTPIC.get_at((4,32,7,3),True), PARTPIC.get_at((16,32,11,4),True), \
         PARTPIC.get_at((30,32,15,5),True)]
WAVEU = [PARTPIC.get_at((4,38,7,3),True), PARTPIC.get_at((16,38,11,4),True), \
         PARTPIC.get_at((30,38,15,5),True)]

class Creep(pygame.sprite.Sprite):

    def __init__(self, position, screen, waypoints, cursor, \
                 player, particle_emitter, hfun, p=1):
        pygame.sprite.Sprite.__init__(self)
        self.id = id(self)
        self.position = position
        self.screen = screen
        self.waypoints = waypoints
        self.cursor = cursor
        self.player = player
        self.alive = True
        self.animation_index = 0
        self.default_timer_value = 5
        self.health = self.mh = 100
        self.image_set = {}
        self.image = pygame.surface.Surface((64,64))
        self.old_rotation = None
        self.rotation = None
        self.offsetnsy = 0
        self.point = 0
        self.rect = self.image.get_rect()
        self.shield = 0
        self.offsety = 0
        self.offsetx = 0
        self.rect.x = position[0]+self.offsetx
        self.rect.y = position[1]
        self.speed = 1.5
        self.timer = 0
        self.banana = 0
        self.offsetns = 0
        self.particle_emitter = particle_emitter
        self.show_p = p
        self.name = ""
        self.hfun = hfun
        self.t = "ground"
        self.move = True
        self.clist = {"ft":False,"fd":30,"pt":False,"pd":200,"m":False, \
                      "jt":False,"jd":60}
        self.back = False
        self.enchanted = False
        self.sp = [1, 2, 1, 2, 0]
        self.si = 0

    def check_cast(self):
        if (self.clist["jt"] and self.clist["jd"]==60) or \
           (self.clist["ft"] and self.clist["fd"]==30):
            self.move = False

        if not self.move:
            if self.clist["fd"] <= 0 and self.clist["ft"]:
                self.move = True
                self.clist["ft"] = False
                self.clist["fd"] = 30
            elif self.clist["fd"] > 0 and self.clist["ft"]:
                self.clist["fd"] -= 1

            if self.clist["jd"] <= 0 and self.clist["jt"]:
                self.move = True
                self.clist["jt"] = False
                self.clist["jd"] = 60
            elif self.clist["jd"] > 0 and self.clist["jt"]:
                self.clist["jd"] -= 1

        if self.clist["pt"]:
            if self.clist["pd"]!=0:
                self.health -= 0.25
                if self.clist["pd"]%20==0:
                    self.particle_emitter.add(AnimPart(
                    self.rect.center, [random.uniform(-0.5,0.5),-0.25],TOXIC,17))
                self.clist["pd"]-=1
            else:
                self.clist["pt"]=False
                self.clist["pd"] = 200

    def convert_rotation(self, angle):
        """
        Converts the given angles to sides
        of the world or x,y movement
        """

        if abs(angle) <= 45:
            return ["E",1,0]
        elif angle > 45 and angle <= 135:
            return ["S",0,1]
        elif abs(angle)>=135:
            return ["W",-1,0]
        elif angle <= -45 and angle >= -135:
            return ["N",0,-1]  


    def animate(self):
        """
        When delay time has passed, the next
        frame of animation is picked
        """
        # Sets the direction of images and pick the corresponding set of images
        if self.old_rotation != self.rotation:
            self.timer = self.default_timer_value   
            self.animation_index = 0
            self.old_rotation = self.rotation   
            c = self.rect.center
            h = self.image.get_height()
            x = self.rect.x
            y = self.rect.y
            self.image = self.image_set[self.rotation][0]
            self.rect = self.image.get_rect()
            if 1:
                self.rect.x = x; self.rect.y = y
            else:
                self.rect.center = c

        else:
            # If the delay time isn't on its maximum, go on
            if self.timer != self.default_timer_value:
                self.timer += 1
            else:
                # When the delay time is on its maximum, go to next image
                self.timer = 0
                # If there's more images left, continue
                if self.animation_index < len(self.image_set[self.rotation])-1:
                    self.animation_index += 1
                else:
                    self.animation_index = 0 # Reset animation
                c = self.rect.center
                self.image = self.image_set[self.old_rotation][self.animation_index]
                self.rect = self.image.get_rect()
                self.rect.center = c


    def mov(self):
        b = 1
        #if self.point == len(self.waypoints)-1:
            #b = -1

        l = 0
        if self.rotation in ["E", "W"]:
            l = self.offsetnsy
        distance_x = self.waypoints[self.point][0]*32+self.offsetx-self.rect.x
        distance_y = self.waypoints[self.point][1]*32-self.rect.y-(self.offsety*b)+l

        if(abs(distance_y)+abs(distance_x)) <= self.speed:
            self.point += 1
        if self.point > len(self.waypoints)-1:
            self.alive = False
            self.player.passed += 1
            self.kill()

        # Compute the angle between the creep and the waypoint
        angle = math.atan2(distance_y, distance_x)
        rot = self.convert_rotation(angle*(180/math.pi))
            
        if rot[0] in ["E","W"] and self.rotation=="S" and self.offsetnsy!=0:
            self.rect.y += self.offsetnsy

        if not self.rect.y >= 768  and self.move:
            self.rect.x += self.speed*rot[1]
            self.rect.y += self.speed*rot[2]

        if self.old_rotation == None:
            self.old_rotation = rot[0]
            self.rotation = self.old_rotation

        if self.name=="WO":
            if self.speed == 2: self.speed = 1
            else: self.speed = 2

        # Set the rotation and move in the direction of the current waypoint
        self.rotation = rot[0]
        if self.move:
            self.animate()

    def update(self):
        if self.alive:

            if self.rect.y >= 608:
                self.alive = False
                self.player.passed += 1
                self.kill()
                self.cursor.change_hover(self.id,False) 
                self.hfun(1, self.id, [2, self.name, self.health])
                return
            
            # Changes the cursor image
            if self.cursor.rect.colliderect(self.rect) and not self.health<=0:
                self.cursor.change_hover(self.id, True)
                self.hfun(0, self.id, [2, self.name, self.health])
            else:
                self.cursor.change_hover(self.id, False)
                self.hfun(1, self.id, [2, self.name, self.health])

            if self.player.paused<0:
                return

            # When the creep's health is smaller than one, or it has passed the
            # last waypoint, kill it
            if self.health <= 0:
                self.alive = False
                self.player.killed += 1
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
                    self.particle_emitter.add(MCluster(self.rect.center, \
                                      5, self.particle_emitter))
                x = 1
                if self.player["powerup"]=="MIM": x=1.1
                self.player["magicka"] += int(self.banana*x)
                self.kill()
            else:
                # Draw the creep's health bar
                red_bar = pygame.rect.Rect((self.rect.x, self.rect.y-6), \
                                           (self.image.get_width(), 5))
                red_bar.centerx = self.rect.centerx
                unit = (self.image.get_width()*self.health)/self.mh
                green_bar = pygame.rect.Rect((red_bar.x, red_bar.y), \
                                             (unit, 5))
                border = pygame.rect.Rect((self.rect.x-1, self.rect.y-7), \
                                          (self.image.get_width()+1, 6))
                pygame.draw.rect(self.screen, (255, 0, 0), red_bar)
                pygame.draw.rect(self.screen, (0, 255, 0), green_bar)
                pygame.draw.rect(self.screen, (100, 100, 100), border, 1)

            self.mov()
            self.check_cast()

class Boat(pygame.sprite.Sprite):

    def __init__(self, pos, screen, player, particle_emitter, tiles):
        pygame.sprite.Sprite.__init__(self)
        self.asset = Sheet("./data/image/objects/minis.png")
        self.images = [self.asset.get_at((0, 0, 27, 49)), \
                       self.asset.get_at((28, 0, 27, 49)), \
                       self.asset.get_at((58, 0, 47, 43)), \
                       self.asset.get_at((58, 44, 47, 43))]
        self.position = pos
        self.screen = screen
        self.shield = 0
        self.player = player
        self.baned = tiles
        self.alive = True
        self.health = self.mh = 150
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.speed = 2
        self.particle_emitter = particle_emitter
        self.bumped = False
        self.t = "water"
        self.timer = 3
        self.colrect = pygame.Rect(0,0,self.image.get_width()+1,self.image.get_height()+1)
        self.colrect.center = self.rect.center        

    def change(self, n):
        x = self.rect.x
        y = self.rect.y
        self.image = self.images[n]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def wave(self, d):
        x = self.rect.centerx
        y = self.rect.centery
        a = WAVED
        if d>0: a = WAVEU
        if self.timer==0:
            temp = (AnimPart([x,y], \
            [0, 0.1*d], a, 10))
            temp.rect.centerx = x
            temp.rect.centery = y+27*d
            self.particle_emitter.add(temp)
            self.timer = 3
        else:
            self.timer -= 1

    def check(self, d):
        col = pygame.sprite.spritecollide(self, self.baned, False)
        a = True
        if col:
            for i in col:
                if d==0 and i.rect.y>self.rect.y+23:
                    a = False
                elif d==1 and i.rect.y<self.rect.y:
                    a = False
                elif d==2 and i.rect.x>self.rect.x:
                    a = False
                elif d==3 and i.rect.x<self.rect.x:
                    a = False
        if not a and not self.bumped: 
            self.health -= 10
            self.bumped = True
        elif a: self.bumped = False
        return a

    def update(self):
        if self.rect.y >= 768:
            self.player.lpassed = 1
            self.kill()

        if self.player.paused<0:
            return

        self.colrect = pygame.Rect(0,0,self.image.get_width()+1,self.image.get_height()+1)
        self.colrect.center = self.rect.center  

        key = pygame.key.get_pressed()

        if key[pygame.K_DOWN] and self.check(0):
            self.change(0)
            self.rect.y += self.speed
            self.wave(-1)
        elif key[pygame.K_UP] and self.check(1):
            self.change(1)
            self.rect.y -= self.speed
            self.wave(1)
        elif key[pygame.K_RIGHT] and self.check(2):
            self.change(2)
            self.rect.x += self.speed
        elif key[pygame.K_LEFT] and self.check(3):
            self.change(3)
            self.rect.x -= self.speed

        if self.health <= 0:
            self.alive = False
            for i in xrange(15):
                    self.particle_emitter.add(
                ImPart(self.rect.center, [random.uniform(0,1),random.uniform(0,1)],
                       random.choice(GORE1),9), \
                ImPart(self.rect.center, [random.uniform(0,-1),random.uniform(0,1)],
                       random.choice(GORE1),9), \
                ImPart(self.rect.center, [random.uniform(0,-1),random.uniform(0,-1)],
                       random.choice(GORE1),9), \
                ImPart(self.rect.center, [random.uniform(0,1),random.uniform(0,-1)],
                       random.choice(GORE1),9))
            self.kill()
        else:
                red_bar = pygame.rect.Rect((self.rect.x, self.rect.y-6), \
                                           (self.image.get_width(), 5))
                red_bar.centerx = self.rect.centerx
                unit = (self.image.get_width()*self.health)/self.mh
                green_bar = pygame.rect.Rect((red_bar.x, red_bar.y), \
                                             (unit, 5))
                border = pygame.rect.Rect((self.rect.x-1, self.rect.y-7), \
                                          (self.image.get_width()+1, 6))
                pygame.draw.rect(self.screen, (255, 0, 0), red_bar)
                pygame.draw.rect(self.screen, (0, 255, 0), green_bar)
                pygame.draw.rect(self.screen, (100, 100, 100), border, 1)



class Wolf(Creep):

    def __init__(self, position, screen, waypoints, cursor, \
                player, particle_emitter, hfun, p=1):
        Creep.__init__(self, position, screen, waypoints, cursor, \
                       player, particle_emitter, hfun, p=1)
        self.asset = Sheet("./data/image/creeps/wolf.PNG")
        self.image_set["N"] = [self.asset.get_at((149, 0, 17, 40), True), \
                               self.asset.get_at((149, 41, 17, 40), True)]
        self.image_set["W"] = [self.asset.get_at((17, 55, 43, 26), True), \
        self.asset.get_at((61, 55, 43, 26), True), self.asset.get_at((105,\
                                                        55, 43, 26), True)]
        self.image_set["S"] = [self.asset.get_at((0, 0, 17, 40), True), \
                               self.asset.get_at((0, 41, 17, 40), True)]
        self.image_set["E"] = [self.asset.get_at((17, 0, 43, 26), True), \
        self.asset.get_at((61, 0, 43, 26), True), self.asset.get_at((105, \
                                                        0, 43, 26), True)]
        self.image = self.image_set["S"][0]
        self.rect = self.image.get_rect()
        self.offsetx = 7
        self.rect.x = position[0]+self.offsetx
        self.rect.y = position[1]
        self.banana = 10
        self.name = "WO"
        self.speed = 2
        self.health = self.mh = 90


class Goblin(Creep):

    def __init__(self, position, screen, waypoints, cursor, \
                player, particle_emitter, hfun, p=1):
        Creep.__init__(self, position, screen, waypoints, cursor, \
                       player, particle_emitter, hfun, p=1)
        self.asset = Sheet("./data/image/creeps/goblin.png")
        self.image_set["N"] = [self.asset.get_at((0, 49, 22, 48), True), \
                               self.asset.get_at((23, 49, 22, 48), True), \
                               self.asset.get_at((46, 49, 22, 48), True), \
                               self.asset.get_at((69, 49, 22, 48), True)]
        self.image_set["E"] = [self.asset.get_at((0, 98, 18, 48), True), \
                               self.asset.get_at((19, 98, 18, 48), True), \
                               self.asset.get_at((38, 98, 18, 48), True), \
                               self.asset.get_at((57, 98, 18, 48), True)]
        self.image_set["S"] = [self.asset.get_at((0, 0, 22, 48), True), \
                               self.asset.get_at((23, 0, 22, 48), True), \
                               self.asset.get_at((46, 0, 22, 48), True), \
                               self.asset.get_at((69, 0, 22, 48), True)]
        self.image_set["W"] = [self.asset.get_at((0, 147, 19, 48), True), \
                               self.asset.get_at((20, 147, 19, 48), True), \
                               self.asset.get_at((39, 147, 19, 48), True), \
                               self.asset.get_at((58, 147, 19, 48), True)]
        self.image = self.image_set["S"][0]
        self.rect = self.image.get_rect()
        self.offsety = 19
        self.offsetx = 6
        self.rect.x = position[0]+self.offsetx
        self.rect.y = position[1]
        self.banana = 5
        self.speed = 1.0
        self.name = "GB"
        self.health = self.mh = 100


class Troll(Creep):

    def __init__(self, position, screen, waypoints, cursor, \
                player, particle_emitter, hfun, p=1):
        Creep.__init__(self, position, screen, waypoints, cursor, \
                       player, particle_emitter, hfun, p=1)
        self.asset = Sheet("./data/image/creeps/troll.png")
        self.image_set["N"] = [self.asset.get_at((0, 113, 58, 112), True), \
                               self.asset.get_at((59, 113, 58, 112), True), \
                               self.asset.get_at((118, 113, 58, 112), True), \
                               self.asset.get_at((177, 113, 58, 112), True)]
        self.image_set["E"] = [self.asset.get_at((0, 226, 43, 111), True), \
                               self.asset.get_at((44, 226, 43, 111), True), \
                               self.asset.get_at((88, 226, 43, 111), True), \
                               self.asset.get_at((132, 226, 43, 111), True)]
        self.image_set["S"] = [self.asset.get_at((0, 0, 58, 112), True), \
                               self.asset.get_at((59, 0, 58, 112), True), \
                               self.asset.get_at((118, 0, 58, 112), True), \
                               self.asset.get_at((177, 0, 58, 112), True)]
        self.image_set["W"] = [self.asset.get_at((0, 338, 43, 112), True), \
                               self.asset.get_at((44, 338, 43, 111), True), \
                               self.asset.get_at((88, 338, 43, 111), True), \
                               self.asset.get_at((132, 338, 43, 111), True)]
        self.image = self.image_set["S"][0]
        self.rect = self.image.get_rect()
        self.offsety = 90
        self.offsetx = -12
        self.rect.x = position[0]+self.offsetx
        self.rect.y = position[1]
        self.banana = 15
        self.speed = 1
        self.name = "TR"
        self.health = self.mh = 250


class FrostGiant(Creep):

    def __init__(self, position, screen, waypoints, cursor, \
                player, particle_emitter, hfun, p=1):
        Creep.__init__(self, position, screen, waypoints, cursor, \
                       player, particle_emitter, hfun, p=1)
        self.asset = Sheet("./data/image/creeps/giant.png")
        self.image_set["N"] = [self.asset.get_at((0, 130, 58, 128), True), \
                               self.asset.get_at((59, 130, 58, 128), True), \
                               self.asset.get_at((118, 130, 58, 128), True), \
                               self.asset.get_at((177, 130, 58, 128), True)]
        self.image_set["E"] = [self.asset.get_at((0, 258, 35, 129), True), \
                               self.asset.get_at((36, 258, 35, 129), True), \
                               self.asset.get_at((82, 258, 35, 129), True), \
                               self.asset.get_at((118, 258, 35, 129), True)]
        self.image_set["S"] = [self.asset.get_at((0, 0, 58, 128), True), \
                               self.asset.get_at((59, 0, 58, 128), True), \
                               self.asset.get_at((118, 0, 58, 128), True), \
                               self.asset.get_at((177, 0, 58, 128), True)]
        self.image_set["W"] = [self.asset.get_at((0, 390, 35, 129), True), \
                               self.asset.get_at((40, 390, 35, 129), True), \
                               self.asset.get_at((82, 390, 35, 129), True), \
                               self.asset.get_at((122, 390, 35, 129), True)]
        self.image = self.image_set["S"][0]
        self.rect = self.image.get_rect()
        self.offsety = 98
        self.offsetx = -12
        self.rect.x = position[0]+self.offsetx
        self.rect.y = position[1]
        self.banana = 40
        self.speed = 1
        self.name = "FG"
        self.health = self.mh = 500

class Boar(Creep):

    def __init__(self, position, screen, waypoints, cursor, \
                player, particle_emitter, hfun, p=1):
        Creep.__init__(self, position, screen, waypoints, cursor, \
                       player, particle_emitter, hfun, p=1)
        self.asset = Sheet("./data/image/creeps/boar.png")
        self.image_set["N"] = [self.asset.get_at((0, 38, 21, 35), True), \
                               self.asset.get_at((22, 38, 21, 35), True), \
                               self.asset.get_at((44, 38, 21, 35), True), \
                               self.asset.get_at((66, 38, 21, 35), True)]
        self.image_set["E"] = [self.asset.get_at((96, 0, 52, 29), True), \
                               self.asset.get_at((150, 0, 52, 29), True), \
                               self.asset.get_at((204, 0, 52, 29), True), \
                               self.asset.get_at((258, 0, 52, 29), True)]
        self.image_set["S"] = [self.asset.get_at((0, 0, 21, 37), True), \
                               self.asset.get_at((22, 0, 21, 37), True), \
                               self.asset.get_at((44, 0, 21, 37), True), \
                               self.asset.get_at((66, 0, 21, 37), True)]
        self.image_set["W"] = [self.asset.get_at((93, 32, 52, 29), True), \
                               self.asset.get_at((147, 32, 52, 29), True), \
                               self.asset.get_at((201, 32, 52, 29), True), \
                               self.asset.get_at((255, 32, 52, 29), True)]
        self.image = self.image_set["S"][0]
        self.rect = self.image.get_rect()
        self.offsety = 0
        self.offsetx = 7
        self.rect.x = position[0]+self.offsetx
        self.rect.y = position[1]
        self.banana = 5
        self.speed = 1
        self.name = "BO"
        self.health = self.mh = 85


class Skeleton(Creep):

    def __init__(self, position, screen, waypoints, cursor, \
                player, particle_emitter, hfun, p=1):
        Creep.__init__(self, position, screen, waypoints, cursor, \
                       player, particle_emitter, hfun, p=1)
        self.asset = Sheet("./data/image/creeps/skeleton.png")
        self.image_set["E"] = [self.asset.get_at((0, 93, 26, 91), True), \
                               self.asset.get_at((27, 93, 26, 91), True), \
                               self.asset.get_at((54, 93, 26, 91), True), \
                               self.asset.get_at((81, 93, 26, 91), True)]
        self.image_set["S"] = [self.asset.get_at((0, 0, 39, 92), True), \
                               self.asset.get_at((40, 0, 39, 92), True), \
                               self.asset.get_at((80, 0, 39, 92), True), \
                               self.asset.get_at((120, 0, 39, 92), True)]
        self.image_set["N"] = [self.asset.get_at((160, 0, 39, 92), True), \
                               self.asset.get_at((200, 0, 39, 92), True), \
                               self.asset.get_at((240, 0, 39, 92), True), \
                               self.asset.get_at((280, 0, 39, 92), True)]
        self.image_set["W"] = [self.asset.get_at((106, 93, 26, 91), True), \
                               self.asset.get_at((135, 93, 26, 91), True), \
                               self.asset.get_at((162, 93, 26, 91), True), \
                               self.asset.get_at((190, 93, 26, 91), True)]
        self.image = self.image_set["S"][0]
        self.rect = self.image.get_rect()
        self.offsety = 62
        self.offsetx = -1
        self.rect.x = position[0]+self.offsetx
        self.rect.y = position[1]
        self.banana = 7
        self.speed = 1
        self.name = "SK"
        self.default_timer_value = 4
        self.health = self.mh = 150


class SeaSerpent(Creep):

    def __init__(self, position, screen, waypoints, cursor, \
                player, particle_emitter, hfun, p=1):
        Creep.__init__(self, position, screen, waypoints, cursor, \
                       player, particle_emitter, hfun, p=1)
        self.asset = Sheet("./data/image/creeps/seaserpent.png")
        self.image_set["N"] = [self.asset.get_at((0, 104, 36, 97), True), \
                               self.asset.get_at((37, 104, 36, 97), True), \
                               self.asset.get_at((74, 104, 36, 97), True), \
                               self.asset.get_at((111, 104, 36, 97), True)]
        self.image_set["E"] = [self.asset.get_at((0, 208, 100, 36), True), \
                               self.asset.get_at((0, 245, 100, 36), True), \
                               self.asset.get_at((0, 282, 100, 36), True), \
                               self.asset.get_at((0, 319, 100, 36), True)]
        self.image_set["S"] = [self.asset.get_at((0, 0, 36, 97), True), \
                               self.asset.get_at((37, 0, 36, 97), True), \
                               self.asset.get_at((74, 0, 36, 97), True), \
                               self.asset.get_at((111, 0, 36, 97), True)]
        self.image_set["W"] = [self.asset.get_at((0, 356, 100, 36), True), \
                               self.asset.get_at((0, 393, 100, 36), True), \
                               self.asset.get_at((0, 430, 100, 36), True), \
                               self.asset.get_at((0, 467, 100, 36), True)]
        self.image = self.image_set["S"][0]
        self.rect = self.image.get_rect()
        self.offsetnsy = 60
        self.offsetx = 5
        self.offsety = 30
        self.rect.x = position[0]+self.offsetx
        self.rect.y = position[1]
        self.banana = 17
        self.speed = 1
        self.name = "SRP"
        self.health = self.mh = 375
        self.t = "water"

class LilKraken(Creep):

    def __init__(self, position, screen, waypoints, cursor, \
                player, particle_emitter, hfun, p=1):
        Creep.__init__(self, position, screen, waypoints, cursor, \
                       player, particle_emitter, hfun, p=1)
        self.asset = Sheet("./data/image/creeps/lilkraken.png")
        self.image_set["N"] = [self.asset.get_at((0, 58, 42, 57), True), \
                               self.asset.get_at((43, 58, 42, 57), True), \
                               self.asset.get_at((86, 58, 42, 57), True), \
                               self.asset.get_at((129, 58, 42, 57), True)]
        self.image_set["E"] = [self.asset.get_at((0, 116, 19, 57), True), \
                               self.asset.get_at((20, 116, 19, 57), True), \
                               self.asset.get_at((40, 116, 19, 57), True), \
                               self.asset.get_at((60, 116, 19, 57), True)]
        self.image_set["S"] = [self.asset.get_at((0, 0, 42, 57), True), \
                               self.asset.get_at((43, 0, 42, 57), True), \
                               self.asset.get_at((86, 0, 42, 57), True), \
                               self.asset.get_at((129, 0, 42, 57), True)]
        self.image_set["W"] = [self.asset.get_at((80, 116, 19, 57), True), \
                               self.asset.get_at((100, 116, 19, 57), True), \
                               self.asset.get_at((120, 116, 19, 57), True), \
                               self.asset.get_at((140, 116, 19, 57), True)]
        self.image = self.image_set["S"][0]
        self.rect = self.image.get_rect()
        self.offsety = 15
        self.offsetx = -5
        self.rect.x = position[0]+self.offsetx
        self.rect.y = position[1]
        self.banana = 7
        self.speed = 1
        self.name = "LK"
        self.health = self.mh = 175
        self.t = "water"

class Warrior(Creep):

    def __init__(self, position, screen, waypoints, cursor, \
                player, particle_emitter, hfun, p=1):
        Creep.__init__(self, position, screen, waypoints, cursor, \
                       player, particle_emitter, hfun, p=1)
        self.asset = Sheet("./data/image/creeps/warrior_soul.png")
        self.image_set["N"] = [self.asset.get_at((122, 0, 60, 81), True), \
                               self.asset.get_at((183, 0, 60, 81), True)]
        self.image_set["E"] = [self.asset.get_at((0, 82, 29, 80), True), \
                               self.asset.get_at((30, 82, 29, 80), True)]
        self.image_set["S"] = [self.asset.get_at((0, 0, 60, 81), True), \
                               self.asset.get_at((61, 0, 60, 81), True)]
        self.image_set["W"] = [self.asset.get_at((60, 82, 29, 80), True), \
                               self.asset.get_at((90, 82, 29, 80), True)]
        self.image = self.image_set["S"][0]
        self.rect = self.image.get_rect()
        self.offsety = 32
        self.offsetx = -5
        self.rect.x = position[0]+self.offsetx
        self.rect.y = position[1]
        self.banana = 30
        self.speed = 1
        self.name = "WA"
        self.health = self.mh = 300
        self.t = "magic"

class Wyvern(Creep):

    def __init__(self, position, screen, waypoints, cursor, \
                player, particle_emitter, hfun, p=1):
        Creep.__init__(self, position, screen, waypoints, cursor, \
                       player, particle_emitter, hfun, p=1)
        self.asset = Sheet("./data/image/creeps/wyvern.png")
        self.image_set["N"] = [self.asset.get_at((0, 154, 102, 140), True), \
                               self.asset.get_at((103, 154, 102, 140), True)]
        self.image_set["E"] = [self.asset.get_at((0, 296, 124, 50), True), \
                               self.asset.get_at((0, 346, 124, 50), True)]
        self.image_set["S"] = [self.asset.get_at((0, 0, 102, 146), True), \
                               self.asset.get_at((103, 0, 102, 146), True)]
        self.image_set["W"] = [self.asset.get_at((0, 398, 124, 50), True), \
                               self.asset.get_at((0, 448, 124, 50), True)]
        self.image = self.image_set["S"][0]
        self.rect = self.image.get_rect()
        self.offsety = 64
        self.offsetx = -32
        self.rect.x = position[0]+self.offsetx
        self.rect.y = position[1]
        self.banana = 1000
        self.speed = 1
        self.name = "WYV"
        self.health = self.mh = 2000
        self.t = "air"

class BonusWarrior(Warrior):

    def __init__(self, position, screen, waypoints, cursor, \
                player, particle_emitter, hfun, towers, p=1):
        Warrior.__init__(self, position, screen, waypoints, cursor, \
                       player, particle_emitter, hfun, p=1)
        self.asset = Sheet("./data/image/creeps/warrior_soul.png")
        self.image_set["N"] = [self.asset.get_at((122, 0, 60, 81), True), \
                               self.asset.get_at((183, 0, 60, 81), True)]
        self.image_set["E"] = [self.asset.get_at((0, 82, 29, 80), True), \
                               self.asset.get_at((30, 82, 29, 80), True)]
        self.image_set["S"] = [self.asset.get_at((0, 0, 60, 81), True), \
                               self.asset.get_at((61, 0, 60, 81), True)]
        self.image_set["W"] = [self.asset.get_at((60, 82, 29, 80), True), \
                               self.asset.get_at((90, 82, 29, 80), True)]
        self.shimage = self.asset.get_at((121,83,69,85),True)
        self.srect = pygame.rect.Rect((0,0,69,85))
        self.image = self.image_set["S"][0]
        self.rect = self.image.get_rect()
        self.offsety = 32
        self.offsetx = -5
        self.rect.x = position[0]+self.offsetx
        self.rect.y = position[1]
        self.speed = 1
        self.health = self.mh = 1000
        self.tw = None
        self.shield = 300
        self.t = "ground"
        self.towers = towers
        self.countdowns = [[0,60],[0,160],[0,220],[0,400]]

    def check_towers(self):
        a = 1000
        tw = None
        for t in self.towers:
           d_x = abs(self.rect.centerx-t.rect.centerx)
           d_y = abs(self.rect.centery-t.rect.centery)
           d = math.sqrt(d_x**2+d_y**2)
           if d<=a:
               a = d
               tw = t
        self.tw = tw
        self.smoke = Smoke(self.particle_emitter, [0, 0], 60)
        self.smoke.rect.center = tw.rect.center
        self.particle_emitter.add(self.smoke)
        self.tw.see = False

    def do_mist(self, n):
        for t in self.towers:
            t.see = n
            if n==False and not "awesome" in t.t:
                x, y = t.rect.center
                self.particle_emitter.add(Mist([x, y], 100))
                self.particle_emitter.add(Mist([x-10, y+5], 100))

    def give_cool(self):
        l = []
        for c in self.countdowns:
            if c[0]==0:
                l.append(0)
            else:
                x = (c[0]*1.0/c[1]*1.0)
                l.append(int(x*80)+50)
        return l

    def update(self):
        if self.alive:
            if self.player.paused<0:
                return

            key = pygame.key.get_pressed()

            for i in range(len(self.countdowns)):
                a = self.countdowns[i][0]
                if a>0:
                    a -=1
                    self.countdowns[i][0] = a
                    if a==50 and i==1:
                        self.speed = 1 
                    elif a==183 and i==2:
                        self.tw.see = True
                    elif a==300 and i==3:
                        self.do_mist(True)

            if key[pygame.K_SPACE]:
                self.move = False
                if self.shield>=1: self.shield -= 3
            else:
                if self.shield<300: self.shield += 1
                if not self.clist["ft"]: self.move = True

            if self.player["magicka"]>=50:
                if key[pygame.K_x] and self.countdowns[0][0]==0 and self.shield<300:
                    self.shield = 300
                    self.countdowns[0][0] = self.countdowns[0][1]
                    self.player["magicka"] -= 50
                elif key[pygame.K_c] and self.countdowns[1][0]==0:
                    self.speed = 2
                    self.countdowns[1][0] = self.countdowns[1][1]
                    self.player["magicka"] -= 50
                elif key[pygame.K_v] and self.countdowns[2][0]==0:
                    self.check_towers()
                    self.countdowns[2][0] = self.countdowns[2][1]
                    self.player["magicka"] -= 50
                elif key[pygame.K_b] and self.countdowns[3][0]==0:
                    self.do_mist(False)
                    self.countdowns[3][0] = self.countdowns[3][1]
                    self.player["magicka"] -= 50

            if self.rect.y >= 768:
                self.alive = False
                self.player.lpassed = 1
                self.kill()
                return

            if self.health <= 0:
                self.alive = False
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
                self.kill()
            else:
                bar1 = pygame.rect.Rect((self.rect.x, self.rect.y-6), \
                                           (self.image.get_width(), 5))
                bar1.centerx = self.rect.centerx
                unit = (self.image.get_width()*self.shield)/300
                bar2 = pygame.rect.Rect((bar1.x, bar1.y), \
                                             (unit, 5))
                border = pygame.rect.Rect((self.rect.x-1, self.rect.y-7), \
                                          (self.image.get_width()+1, 6))
                pygame.draw.rect(self.screen, (100, 155, 100), bar1)
                if self.shield>=1:
                    pygame.draw.rect(self.screen, (100, 255, 100), bar2)
                pygame.draw.rect(self.screen, (100, 100, 100), border, 1)

            if self.point > len(self.waypoints)-1:
                self.alive = False
                self.player.lpassed = 1
                self.kill()
            if not self.move and self.shield>=1:
                self.srect.center = self.rect.center
                self.screen.blit(self.shimage, self.srect)
            self.mov()
            self.check_cast()

