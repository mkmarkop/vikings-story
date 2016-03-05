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

from helpers import Sheet

blic = Sheet("./data/image/menu/info_icons.png")
CLUSTER = {"m": blic.get_at((59,5,11,17), True),
           "g": blic.get_at((144,3,15,15), True)}

PARTPIC = Sheet("./data/image/environment/particles.png")
SMOKE = [PARTPIC.get_at((0,22,5,5),True), PARTPIC.get_at((6,22,7,6),True), \
         PARTPIC.get_at((14,22,11,9),True)]
FROZEN = Sheet("./data/image/environment/frozen.png")
GORE = [PARTPIC.get_at((7,0,5,5),True), PARTPIC.get_at((13,0,6,5),True), \
        PARTPIC.get_at((20,0,5,5),True)]
DRP = [PARTPIC.get_at((71,8,3,4),True), PARTPIC.get_at((14,73,6,3),True), \
       PARTPIC.get_at((21,72,10,5),True), PARTPIC.get_at((32,72,10,5),True)]
WAVED = [PARTPIC.get_at((4,32,7,3),True), PARTPIC.get_at((16,32,11,4),True), \
         PARTPIC.get_at((30,32,15,5),True)]
WAVEU = [PARTPIC.get_at((4,38,7,3),True), PARTPIC.get_at((16,38,11,4),True), \
         PARTPIC.get_at((30,38,15,5),True)]

class ABoat(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.asset = Sheet("./data/image/objects/minis.png")
        self.images = [self.asset.get_at((0, 0, 27, 49)), \
                       self.asset.get_at((28, 0, 27, 49)), \
                       self.asset.get_at((58, 0, 47, 43)), \
                       self.asset.get_at((58, 44, 47, 43))]
        self.wp = [[928, 320], [672, 320], [672, 384], [672, 448], \
                   [928, 448], [928, 768]]
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.x = 928
        self.rect.y = 0
        self.speed = 1
        self.timer = 6       
        self.rotation = None
        self.point = 0
        self.paused = 60

    def convert_rotation(self, angle):
        if abs(angle) <= 45:
            return [2,1,0]
        elif angle > 45 and angle <= 135:
            return [0,0,1]
        elif abs(angle)>=135:
            return [3,-1,0]
        elif angle <= -45 and angle >= -135:
            return [1,0,-1]  

    def mov(self):
        distance_x = self.wp[self.point][0]-self.rect.x
        distance_y = self.wp[self.point][1]-self.rect.y

        if(abs(distance_y)+abs(distance_x)) <= self.speed:
            self.point += 1
        if self.point > len(self.wp)-1:
            self.reset()

        angle = math.atan2(distance_y, distance_x)
        rot = self.convert_rotation(angle*(180/math.pi))
        self.rect.x += self.speed*rot[1]
        self.rect.y += self.speed*rot[2]

        self.rotation = rot[0]
        self.change(self.rotation)
        d = 0
        if self.rotation == 1:
            d = 1
        elif self.rotation == 0:
            d = -1 
        self.wave(d)

    def change(self, n):
        x = self.rect.x
        y = self.rect.y
        self.image = self.images[n]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def wave(self, d):
        if d==0: return
        x = self.rect.centerx
        y = self.rect.centery
        a = WAVED
        if d>0: a = WAVEU
        if self.timer==0:
            g = self.groups()[0]
            temp = (AnimPart([x,y], \
            [0, 0.1*d], a, 10))
            temp.rect.centerx = x
            temp.rect.centery = y+27*d
            g.add(temp)
            self.timer = 6
        else:
            self.timer -= 1

    def reset(self):
        self.rect.y = 0
        self.point = 0
        self.paused = 60

    def update(self):
        if self.rect.y >= 768:
            self.reset()

        if self.point == 3:
            if self.paused > 0:
                self.paused -= 1
                return

        self.mov()


class Particle(pygame.sprite.Sprite):

    def __init__(self, pos, speed, size=None, color=None, duration=None, \
                 gravity=0):
        pygame.sprite.Sprite.__init__(self)
        self.acclrtn_x = speed[0]
        self.acclrtn_y = speed[1]
        self.velocity_x = 0
        self.velocity_y = 0
        self.gravity = gravity
        self.dur = duration
        self.image = pygame.surface.Surface((size, size)).convert()
        self.image.fill(color)
        self.rect = self.image.get_rect(center=pos)

    def update(self):
        self.rect.move_ip(self.velocity_x, self.velocity_y)
        self.velocity_x += self.acclrtn_x
        self.velocity_y += self.acclrtn_y
        self.acclrtn_y += self.gravity
        if self.dur<=0:
            self.kill()
        else:
            self.dur -= 1


class Butterfly(pygame.sprite.Sprite):

    def __init__(self, pat):
        pygame.sprite.Sprite.__init__(self)
        self.images = [PARTPIC.get_at((39,46,12,9),True), \
                       PARTPIC.get_at((39,57,12,11),True), \
                       PARTPIC.get_at((52,46,12,9),True), \
                       PARTPIC.get_at((52,57,12,11),True)]
        self.image = self.images[0]
        self.timer = 0
        self.stop = False
        self.potato = 0
        p = random.choice(pat)
        self.pat = pat
        self.pi = 0
        self.rect = self.image.get_rect()
        self.p = [random.randint(0, 12), random.randint(0, 12)]
        self.rect.x = p[0]+self.p[0]
        self.rect.y = p[1]+self.p[1]
        self.b = 1
        self.moving = False
        self.turned = 0

    def move(self):
        p = [self.goal[0]+self.p[0], self.goal[1]+self.p[1]]
        if self.rect.x == p[0] and self.rect.y == p[1]:
            self.moving = False
            return
        else:
            distance_x = p[0]-self.rect.x
            distance_y = p[1]-self.rect.y
            if distance_x != 0:
                if distance_x<0: self.turned = 2
                else: self.turned = 0
                self.rect.x += distance_x/abs(distance_x)
            if distance_y != 0:
                self.rect.y += distance_y/abs(distance_y)

    def update(self):
        if self.moving:
           self.move()
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos) and not self.moving:
            self.moving = True
            self.goal = random.choice(self.pat)
        if self.stop:
            if self.potato != 7: 
                self.potato += 1
            else:
                self.potato = 0
                self.stop = False
                self.pi = 0
            return
        if self.timer == 0:
            oc = self.rect.center
            self.image = self.images[self.b+self.turned]
            self.rect = self.image.get_rect()
            self.rect.center = oc
            self.timer = 3
            if self.b == 1: self.b = 0
            else: self.b = 1
            self.pi += 1
        elif self.timer !=0:
            self.timer -= 1
        if self.pi >= 10 and not self.moving: self.stop = True


class Fish(pygame.sprite.Sprite):

    def __init__(self, p):
        pygame.sprite.Sprite.__init__(self)
        x = pygame.surface.Surface((32,32))
        x.fill((0,0,0))
        x.set_colorkey((0,0,0))
        self.images = [PARTPIC.get_at((65,0,32,32),True), \
                       PARTPIC.get_at((65,32,32,32),True), \
                       PARTPIC.get_at((65,64,32,32),True), x]
        self.image = self.images[0]
        self.timer = 0
        self.stop = True
        self.potato = random.randint(18, 30)
        self.pi = 0
        self.rect = self.image.get_rect()
        a = random.choice(p.sprites())
        self.rect.x = a.rect.x
        self.rect.y = a.rect.y
        self.b = 0

    def update(self):
        if self.stop:
            if self.potato != 30: 
                self.potato += 1
            else:
                self.potato = 0
                self.stop = False
                self.pi = 0
            return
        if self.timer == 0:
            oc = self.rect.center
            self.image = self.images[self.b]
            self.rect = self.image.get_rect()
            self.rect.center = oc
            self.timer = 3
            if self.b >= 3:
                self.b = 0
            else:
                self.b += 1
            self.pi += 1
        elif self.timer !=0:
            self.timer -= 1
        if self.pi >= 4: self.stop = True

class ImPart(Particle):
    def __init__(self, pos, speed, image, duration=None, \
                 gravity=0, onFall=False):
        Particle.__init__(self, pos, speed, 1, (0,0,0), duration, gravity)
        self.acclrtn_x = speed[0]
        self.acclrtn_y = speed[1]
        self.velocity_x = 0
        self.velocity_y = 0
        self.gravity = gravity
        self.image = image
        self.rect = self.image.get_rect(center=pos)
        self.onFall = onFall

    def update(self):
        self.rect.move_ip(self.velocity_x, self.velocity_y)
        self.velocity_x += self.acclrtn_x
        self.velocity_y += self.acclrtn_y
        self.acclrtn_y += self.gravity
        if self.dur<=0:
            if self.onFall:
                c = self.image.get_at((0,0))
                gs = self.groups(); g = gs[0];
                for i in range(30):
                    g.add(Particle(self.rect.center, [random.randint(-2,2),random.randint(-2,2)], random.randint(2,4), c, 7))
            self.kill()
        else:
            self.dur -= 1

class AnimPart(pygame.sprite.Sprite):

    def __init__(self, pos, speed, anim, duration=None, \
                 acc=True, gravity=0 ,timer=4):
        pygame.sprite.Sprite.__init__(self)
        self.acclrtn_x = speed[0]
        self.acclrtn_y = speed[1]
        self.velocity_x = self.acclrtn_x 
        self.velocity_y = self.acclrtn_y
        self.dur = duration
        self.gravity = gravity
        self.anim = anim
        self.image = anim[0]
        self.rect = self.image.get_rect(center=pos)
        self.timer = self.deft = timer
        self.aindex = 0
        self.acc = acc

    def update(self):
        self.rect.move_ip(self.velocity_x, self.velocity_y)
        if self.acc:
            self.velocity_x += self.acclrtn_x
            self.velocity_y += self.acclrtn_y
        self.acclrtn_y += self.gravity
        if self.dur<=0:
            self.kill()
        else:
            self.dur -= 1
            if self.timer!=0:
                self.timer -= 1
            else:
                if not self.aindex>=len(self.anim)-1:
                    self.aindex += 1
                    old = self.rect.center
                    self.image = self.anim[self.aindex]
                    self.rect = self.image.get_rect(center=old)
                self.timer = self.deft


class Smoke(pygame.sprite.Sprite):

    def __init__(self, g, pos, time):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.surface.Surface((1, 1))
        self.image.set_alpha(0)
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.t = 4
        self.time = time
        self.p_em = g

    def update(self):
        if self.time != 0:
            if self.t==0:
                self.p_em.add(AnimPart(self.rect.center, [random.randint(-1,1), -1],
                              SMOKE, 25, acc=False))
                self.t = 4
            else:
                self.t-= 1
            self.time -=1
        else:
            self.kill()


class Mist(pygame.sprite.Sprite):

    def __init__(self, pos, time):
        pygame.sprite.Sprite.__init__(self)
        self.image = PARTPIC.get_at((2,49,35,19),True).convert()
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.a = 30
        self.b = 1
        self.mt = time
        self.time = time

    def update(self):
        if self.time!=0:
            self.time -= 1
            if self.a >= 30+self.mt/2:
                self.b = -1
            elif self.a <= 29:
                self.b = 1
            self.a += self.b
            self.image.set_alpha(self.a)
        else:
            self.kill()

        
class Weather(pygame.sprite.Sprite):

    def __init__(self, pos, height, drop, sea=None, creeps=None, towers=None):
        pygame.sprite.Sprite.__init__(self)
        self.gravity = 0.1
        self.height = height
        self.velocity_y = 10
        self.d = drop
        if drop == "rain":
            self.image = PARTPIC.get_at((0,0,1,4),True)
        elif drop == "snow":
            self.image = PARTPIC.get_at((1,0,4,4),True)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.sea = sea
        self.creeps = creeps
        self.towers = towers
        
    def update(self):
        if not self.rect.y>=self.height:
            self.rect.y += self.velocity_y
            self.velocity_y += self.gravity
        else:
            if self.d=="rain":
                x = pygame.sprite.spritecollide(self, self.creeps, False)
                y = pygame.sprite.spritecollide(self, self.towers, False)
                if pygame.sprite.spritecollide(self, self.sea,False) \
                   and not x and not y:
                    g = self.groups()[0]
                    g.add(AnimPart(self.rect.center, [0,0], DRP, 25))
            self.height = random.randint(10, 608)
            self.rect.y = 0
            self.velocity_y = 10


class MReward(pygame.sprite.Sprite):

    def __init__(self, pos, speed, dur, image):
        pygame.sprite.Sprite.__init__(self)
        self.acclrtn_x = speed[0]
        self.acclrtn_y = speed[1]
        self.velocity_x = 0
        self.velocity_y = 0
        self.image = image
        self.pops = []
        self.alpha = 255
        for i in xrange(dur):
            self.alpha -= 5
            image = self.image.copy()
            image.set_alpha(self.alpha)
            self.pops.append(image)
        self.rect = self.image.get_rect(center=pos)
        self.rect.x = pos[0]
        self.rect.y = pos[1]

    def update(self):
        self.rect.move_ip(self.velocity_x, self.velocity_y)
        self.velocity_x += self.acclrtn_x
        self.velocity_y += self.acclrtn_y
        self.acclrtn_y += 0.07
        if not self.pops:
            self.kill()
        else:
            self.image = self.pops.pop(0)


class MCluster(pygame.sprite.Sprite):

    def __init__(self, pos, n, p_em, image="m"):
        pygame.sprite.Sprite.__init__(self)
        self.pos = pos
        self.image = pygame.surface.Surface((1, 1))
        self.image.set_alpha(0)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.n = n
        self.t = 3
        self.p_em = p_em
        self.imag = CLUSTER[image]

    def update(self):
        if self.n==0:
            self.kill()
        if self.t!=0 and self.n!=0:
            self.t -= 1
        elif self.t==0 and self.n!=0:
            self.t = 3
            self.p_em.add(MReward(self.pos, [0, 1], 7, self.imag))
            self.n-=1

class Error(Particle):

    def __init__(self, pos, size, color, message):
        Particle.__init__(self, pos, [0, 0], size, color, 25)
        self.font = pygame.font.Font("./data/font/times.ttf", size)
        self.image = self.font.render(message, True, color)
        self.pops = []
        self.alpha = 255
        for i in xrange(25):
            self.alpha -= 50
            image = self.image.copy()
            image.set_alpha(self.alpha)
            self.pops.append(image)
        self.rect.x = pos[0]
        self.rect.y = pos[1]


class Bullet(pygame.sprite.Sprite):

    def __init__(self, pos, speed, goal, bastards, image, damage, passon=None, \
                 passedon=[],effect=None,trail=False):
        pygame.sprite.Sprite.__init__(self)
        self.pos = pos
        self.speed = speed
        self.goal = goal
        self.dir = math.atan2(self.goal[1]-pos[1], self.goal[0]-pos[0])
        self.image = pygame.transform.rotate(image, int(self.dir*(-180/math.pi)))
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.damage = damage
        self.bastards = bastards
        self.alive = True
        self.passon = passon
        self.passedon = passedon
        self.vx = 0
        self.vy = 0
        self.effect = effect
        self.trail = trail

    def update(self):
        if self.alive:
            gs = self.groups()
            g = gs[0]
            vx = 0
            vy = 0
            if self.vx!=0:
                vx = abs(self.vx)/self.vx
            if self.vy!=0:
                vy = abs(self.vy)/self.vy
            if self.trail:
                 g.add(Particle([speed_x, self.rect.y+height], [vy,vx], \
                            random.randrange(1, 3), self.c[0], 6, 0.7), 
                       Particle([speed_x+4, self.rect.y+height], [vy,vx], \
                            random.randrange(1, 3), self.c[1], 6, 0.7))
            col = pygame.sprite.spritecollide(self, self.bastards, False)
            # If the bullet is off the boundaries, kill him, if he's colliding
            # with the target, remove HP from target and than kill him
            if self.rect.x > 1024 or self.rect.x < 0 or self.rect.y < 0 or \
               self.rect.y > 768 or col:
                if col:
                    for i in col:
                        if i.shield>=1 and not i.move:
                            continue
                        g.add(ImPart(i.rect.center, [vy,vx], random.choice(GORE), 5))
                        if self.passon:
                            p = self.passon
                            if i.clist[p]!=True:
                                i.clist[p]=True
                                self.passedon.append(i)
                        i.health -= self.damage
                        if self.effect=="icy":
                            w, h = i.image.get_size()
                            r = pygame.Rect(0, 0, w, h)
                            g.add(ImPart(i.rect.center, [0,0], FROZEN.get_at(r,True), 30, onFall=True))
                self.alive = False
                self.kill()
            else:
                self.vx = self.speed*math.cos(self.dir)
                self.vy = self.speed*math.sin(self.dir)
                self.rect.x += self.speed*math.cos(self.dir)
                self.rect.y += self.speed*math.sin(self.dir)
            self.speed += 0.1


class Bullet2(Bullet):

    def __init__(self, pos, speed, goal, bastards, image, damage, id, \
                 deg=0, pause=True):
        pygame.sprite.Sprite.__init__(self)
        self.pos = pos
        self.speed = speed
        self.goal = goal
        if deg!=0:
            rad = deg*math.pi/180
            velx = math.sin(rad)*100
            vely = math.cos(rad)*100
            pos[0] += velx
            pos[1] -= vely
        self.dir = math.atan2(self.goal[1]-pos[1], self.goal[0]-pos[0])
        self.image = pygame.transform.rotate(image, int(self.dir*(-180/math.pi)))
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.damage = damage
        self.bastards = bastards
        self.alive = True
        self.id = id
        self.pause = pause

    def bye(self):
        self.alive = False
        self.kill()

    def update(self):
        if self.alive:
            col = pygame.sprite.spritecollide(self, self.bastards, False)
            if col:
                for i in col:
                    if i.id==self.id:
                        i.health -= self.damage
                        if self.pause:
                            i.clist["ft"] = True
                        self.bye()
            if self.rect.center==self.goal or self.rect.y>=700 or self.rect.y<=0 or self.rect.x<=0 or self.rect.y>=1024: 
                self.bye()
            else:
                self.rect.centerx += self.speed*math.cos(self.dir)
                self.rect.centery += self.speed*math.sin(self.dir)
