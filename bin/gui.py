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

from helpers       import Sheet, load_image

STATUS_ICONS = Sheet("./data/image/menu/status_icons.png")
BOX = Sheet("./data/image/menu/message.png")

class Cursor:

    def __init__(self, images, screen):
        """
        Class for custom cursor image.
        Can change its image.
        """
        self.images = images
        self.scr = screen
        self.image = self.images[0]
        self.pos = pygame.mouse.get_pos()
        self.rect = self.image.get_rect()
        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1]
        self.hover = False
        self.caller_id = None
        self.sp = False
        self.visible = True

    def spell(self):
        if not self.sp:
            self.sp = True
        else:
            self.sp = False

    def return_data(self):
        return self.data

    def reset(self):
        self.hover = False
        self.caller_id = None
        self.image = self.images[0]

    def change_hover(self, object_id, hovering):
        """
        Judging by the object's ID, changes current
        image to other one. ID is needed, so other
        objects don't kill one's request
        """
        if object_id == self.caller_id and not hovering:
            self.hover = hovering

        elif self.caller_id == None and hovering:
            self.hover = hovering
            self.caller_id = object_id

        elif hovering:
            self.hover = hovering
            self.caller_id = object_id

    def update(self):
        if not self.visible: return
        self.rect.x, self.rect.y = pygame.mouse.get_pos()

        if not self.sp:
            if self.hover == True:
                self.image = self.images[1]
            else:
                self.image = self.images[0]
            self.scr.blit(self.image, self.rect)
        else:
            self.image = self.images[2]
            self.scr.blit(self.image, self.rect)

class Master:

    def __init__(self, pos, width, height, screen, cursor, font, player=None):
        """
        Controlls and updates widgets
        """
        self.widgets = []
        self.key = None
        self.alive = 1
        self.surface = screen
        self.cursor = cursor
        self.rect = pygame.rect.Rect(0, 0, width, height)
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.scr = screen
        self.font = font
        self.state = "default"
        self.pl = player
        self.frozen = False

    def die(self):
        """
        Kills object
        """
        self.alive = False

    def switch(self, new_state):
        """
        Switches the state of master
        """
        self.state = new_state
        self.cursor.reset()

        if "box" in new_state:
            self.freeze()

    def update(self):
        """
        Updates widgets if they're updateable
        in current state
        """
        if self.alive:
            for widget in self.widgets:
                if self.state in widget.states:
                    widget.update()

    def freeze(self):
        """
        (Un)Freezes all buttons from checking for click;
        Used by message boxes
        """
        if not self.frozen:
            self.frozen = True
        else:
            self.frozen = False

    def add_widget(self, widget):
        """
        Adds widgets.
        """
        self.widgets.append(widget)

    def reset_widgets(self):
        """
        Deletes all widgets
        """
        del self.widgets[:]

class Widget:

    def __init__(self, master, pos, txt_col, bg_col, txt_size, \
                 states=["default"]):
        """
        Base class for other widgets.
        """
        self.master = master
        self.master.add_widget(self)
        self.id = id(self)
        self.cursor = self.master.cursor
        self.pos = [pos[0]+self.master.rect.x, pos[1]+self.master.rect.y]
        self.txt_col = txt_col
        self.txt_size = txt_size
        self.bg_col = bg_col
        self.surf = self.master.surface
        self.font = pygame.font.Font(self.master.font, self.txt_size)
        self.states = states

    def update(self):
        pass


class Label(Widget):

    def __init__(self, master, pos, txt_col, bg_col, txt_size, text, \
                 states=["default"]):
        """
        Blits only one line of text.
        """
        Widget.__init__(self, master, pos, txt_col, bg_col, txt_size, states) 
        self.text = text

        if self.bg_col:
            self.surf = self.font.render(self.text, True, self.txt_col, \
                                         self.bg_col)
        else:
            self.surf = self.font.render(self.text, True, self.txt_col)

        self.rect = self.surf.get_rect()
        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1]

    def change(self, text):
        """
        Changes data of the label.
        """
        self.text = text

        if self.bg_col:
            self.surf = self.font.render(self.text, True, self.txt_col, \
                                         self.bg_col)
        else:
            self.surf = self.font.render(self.text, True, self.txt_col)
        x = self.rect.x
        y = self.rect.y
        self.rect = self.surf.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        self.master.scr.blit(self.surf, self.rect)    


class Textbox(Label):

    def __init__(self, master, pos, txt_col, bg_col, txt_size, text, indent, \
                 states=["default"]):
        """
        Blits multiple lines of text,
        separated by newline.
        """
        Label.__init__(self, master, pos, txt_col, bg_col, txt_size, text, \
                       states)
        self.lines = self.text.split("\n")
        self.surfaces = []
        self.ii = indent # Space between lines

        # Makes new surface for each line
        for i in self.lines:
            tmp = self.font.render(i, True, self.txt_col)
            self.surfaces.append(tmp)

    def update(self):
        for i in range(0, len(self.lines)): 
            self.master.scr.blit(self.surfaces[i], (self.pos[0], \
                                (self.pos[1]+self.txt_size*i+i*self.ii)))

    def get_size(self):
        width = 0
        height = 0
        
        for i in range(0, len(self.lines)):
            surf = self.surfaces[i]
            w = surf.get_width()
            if w > width:
                 width = w
            height += self.txt_size+i*self.ii

        return (width, height)

    def change(self, text):
        """
        Changes text of the textbox.
        """
        self.lines = text.split("\n")
        self.surfaces = []
        for i in self.lines:
            tmp = self.font.render(i, True, self.txt_col)
            self.surfaces.append(tmp)


class Button(Label):

    def __init__(self, master, pos, txt_col, bg_col, txt_size, text, command, \
                 arguments, states=["default"], holdable=False, box=False, \
                 hovfun=None,hovarg=None):
        """
        Button widget - when clicked,
        it will execute the given command.
        """
        Label.__init__(self, master, pos, txt_col, bg_col, txt_size, text, \
                       states)
        self.command = command
        self.args = arguments
        self.holdable = holdable # If true, command will execute when holding 
                                 # button
        self.holding = 0
        self.alpha = 0
        self.line = pygame.surface.Surface((self.surf.get_width(), 1))
        self.line.fill(txt_col)
        self.line.set_alpha(self.alpha)
        self.line_rect = self.line.get_rect()
        self.line_rect.center = self.rect.center
        self.line_rect.centery += (self.surf.get_height()/4+1)
        self.box = box
        self.hovfun = hovfun
        self.hovarg = hovarg
        self.line.set_alpha(0)

    def change_line(self):
        self.line_rect = self.line.get_rect()
        self.line_rect.center = self.rect.center
        self.line_rect.centery += (self.surf.get_height()/4)+1

    def update(self):
        click = pygame.mouse.get_pressed()
        pos = pygame.mouse.get_pos()

        # If mouse is colliding with the button, and our master is on top,
        # change cursor image and increase alpha, if not, decrease it.
        if self.rect.collidepoint(pos):

            if not self.master.frozen or self.box:
                self.cursor.change_hover(self.id, True)

                if not self.alpha >= 255:
                    self.alpha += 15

                elif self.alpha > 255:
                    self.alpha = 255

                if self.hovfun != None:
                    self.hovfun(0, self.id, self.hovarg)
            
                # If LMB is clicked and button's holdable or the user's not
                # holding the button, execute the command (with or without 
                # arguments, it depends on given values)
                if click[0] == 1:
                    if self.holdable or not self.holding>0:
                        if self.args!=None:
                            self.command(self.args)

                        else:
                            self.command()

                        self.holding += 1

                else:
                    self.holding = 0

        else:
            self.cursor.change_hover(self.id, False)
            if self.hovfun != None:
                 self.hovfun(1, self.id, self.hovarg)

            if not self.alpha <= 0:
                self.alpha -= 30

            elif self.alpha < 0:
                self.alpha = 0    

        self.line.set_alpha(self.alpha)
        self.master.scr.blit(self.surf, self.rect)
        self.master.scr.blit(self.line, self.line_rect)

class Image:

    def __init__(self, master, pos, img, states=["default"]):
        """
        Blits an image.
        """
        self.master = master
        self.master.add_widget(self)
        self.cursor = self.master.cursor
        self.id = id(self)
        self.pos = [pos[0]+self.master.rect.x, pos[1]+self.master.rect.y]
        self.img = img
        self.dimg = img
        self.rect = self.img.get_rect()
        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1]
        self.states = states
        self.flashing = False
        if self.img.get_width()<=29:
            self.flashy = load_image("./data/image/menu/flashing_button1.png", \
            True).convert()
        else:
            self.flashy = load_image("./data/image/menu/flashing_button.png", \
            True).convert()
        self.alpha = 0
        self.flashy.set_alpha(0)
        self.frec = self.flashy.get_rect(center=self.rect.center)
        self.o = 1

    def flash(self):
        if not self.flashing:
            self.flashing = True
        else:
            self.flashing = False

    def change(self, image):
        x = self.rect.x
        y = self.rect.y
        self.img = self.dimg = image
        self.rect = self.img.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        self.master.scr.blit(self.img, self.rect)


class ImageButton(Image):

    def __init__(self, master, pos, img, command, arguments=None, \
                 states=["default"], holdable=False, hovimg=None, \
                 hovfun=None,hovarg=None,box=False,key=None):
        """
        Image, which when is clicked, will
        execute a command. For more info see Button
        class
        """
        Image.__init__(self, master, pos, img, states)
        self.command = command
        self.args = arguments
        self.holding = 0
        self.t = 0
        self.box = box
        self.holdable = holdable
        self.hovimg = hovimg
        self.hovfun = hovfun
        self.hovarg = hovarg
        self.done = False
        self.key = key

    def update(self):
        self.master.scr.blit(self.img, self.rect)
        if self.key!=None:
			shorty = pygame.key.get_pressed()
			if shorty[self.key]:
				if self.args!=None:
					self.command(self.args)
				else:
					self.command()
				return
                
        click = pygame.mouse.get_pressed()
        pos = pygame.mouse.get_pos()
        hoover = False

        if self.rect.collidepoint(pos) and (not self.master.frozen or self.box):
            hoover = True
            
        if hoover:
            self.cursor.change_hover(self.id, True)
            
            if self.hovfun != None:
                self.hovfun(0, self.id, self.hovarg)
            
            if self.hovimg != None:
                self.img = self.hovimg 
            
            if click[0] == 1:
                if self.holdable or not self.done:
                    if self.args!=None:
                         self.command(self.args)
                    else:
                         self.command()
                    #self.holding+=1
                    self.done = True
                    self.t = 2 

            elif not click[0] == 1:
                self.holding = 0
                if self.done: self.done = False
                
        elif not hoover:
            if self.hovimg != None:
                 self.img = self.dimg      
            self.cursor.change_hover(self.id,  False)
            if self.hovfun != None:
                 self.hovfun(1, self.id, self.hovarg)
            if self.flashing:
                if self.alpha < 120 and self.o: 
                    self.alpha += 10
                elif self.alpha >=120 and self.o:
                    self.o = 0
                if not self.o and self.alpha >0: 
                    self.alpha -= 10
                elif not self.o and self.alpha <=0:
                    self.o = 1

                self.flashy.set_alpha(self.alpha)
                self.master.scr.blit(self.flashy, self.frec)


class Checkbox(Widget):

    def __init__(self, master, pos, txt_col, bg_col, txt_size, text, values, \
                 states=["default"], def_value=None):
        """
        Widget for visually showing Boolean
        value. If box is clicked, and value is true,
        change it to false and vice-versa.
        """
        Widget.__init__(self, master, pos, txt_col, bg_col, txt_size, states)
        self.text = text
        self.current = self.not_checked = values[0] # Sets value to default one
        self.checked = values[1]
        self.images = [STATUS_ICONS.get_at((57, 0, 19, 19), False), \
                       STATUS_ICONS.get_at((0, 0, 19, 19), False)]
        self.button = ImageButton(master, [pos[0], pos[1]+7], self.images[0], \
                                  self.switch, None, states)

        if self.bg_col:
            self.surf = self.font.render(self.text, True, self.txt_col, \
                                         self.bg_col)
        else:
            self.surf = self.font.render(self.text, True, self.txt_col)

        self.rect = self.surf.get_rect()
        self.rect.x = self.pos[0]+21 
        self.rect.y = self.pos[1]
        if def_value:
            self.current = def_value
        self.button.img = self.images[def_value]

    def get_value(self):
        """
        Returns current value.
        """
        return self.current

    def switch(self):
        """
        Switches the current value.
        """
        if not self.current == self.checked:
            self.current = self.checked
            self.button.img = self.images[1]

        else:
            self.current = self.not_checked
            self.button.img = self.images[0]

    def update(self):
        self.master.scr.blit(self.surf, self.rect)
        self.button.update()   


class Scroll(Label):

    def __init__(self, master, pos, txt_col, bg_col, txt_size, \
                 states=["default"], def_val = 100.0, minv=0.0, maxv=100.0, \
                 step=1.0):
        """
        Widget for changeable values.
        """
        Label.__init__(self, master, pos, txt_col, bg_col, txt_size, \
                       str(maxv), states)
        self.text = str(maxv)
        self.minv = minv
        self.maxv = maxv
        self.step = step
        self.value = def_val
        pos1 = [pos[0], pos[1]+7]
        self.lower  = ImageButton(master, pos1, STATUS_ICONS.get_at(( \
                                  76, 0, 19, 19), False), self.add, (-1.0), \
                                  states, True)
        self.higher = ImageButton(master, [pos1[0]+80, pos1[1]], \
                                  STATUS_ICONS.get_at((95, 0, 19, 19), False), \
                                  self.add, (1.0), states, True)
        self.rect.x += 26

    def add(self, value=1):
        """
        Adds value to current one.
        """
        if not self.value < self.minv and not self.value > self.maxv:
            self.value += self.step*value

            if self.value > self.maxv:
                self.value = self.maxv

            elif self.value < self.minv:
                self.value = self.minv

            self.text = str(self.value)

    def get_value(self):
        return self.value

    def update(self):
        self.change(str(int(self.value)))
        self.master.scr.blit(self.surf, self.rect)
        self.lower.update()
        self.higher.update()

class OKBox:

    def __init__(self, master, txt_col, bg_col, txt_size, text, indent, \
                 okfun, okargs=None, states=["okbox"]):
        """
        Blits an image.
        """
        self.master = master
        self.master.add_widget(self)
        self.cursor = self.master.cursor
        self.states = states
        self.okfun = okfun
        self.okargs = okargs
        self.tbox = Textbox(self.master,[400,400],txt_col,bg_col,txt_size,text,3,states)
        size = self.tbox.get_size()
        w = size[0]+20
        h = size[1]+20+txt_size+24
        self.image = BOX.get_at((0,0,330,334),True)
        self.rect = self.image.get_rect()
        self.rect.center = (512, 384)
        x, y = self.rect.x, self.rect.y
        self.tbox.pos[0] = 28+x
        self.tbox.pos[1] = 28+y
        self.okb = ImageButton(self.master,[0,0],BOX.get_at((50,483,47,22),True),self.kill, \
                          None, states, False, BOX.get_at((50,506,47,22),True), box=True)
        self.okb.rect.y = 273+y
        self.okb.rect.x = 138+x
        self.stat = False
        self.st = BOX.get_at((21,336,282,146),False)
        self.sr = self.st.get_rect()
        self.sr.x = 24+self.rect.x
        self.sr.y = 63+self.rect.y

    def kill(self):
        if self.okargs:
            self.okfun(self.okargs)
        else:
            self.okfun()

        self.master.freeze()

    def stats(self, g=0, r=0, bp=0, tw=0, sp=0, un='-'):
        self.tbox.change('')
        x, y = self.rect.x, self.rect.y
        p = Image(self.master, [0,0], BOX.get_at((194,508,143,25),True), self.states)
        p.rect.x, p.rect.y = 101+x, 28+y
        lbs = [Label(self.master,[0,0],(0,0,0),None,18,'',self.states), \
                    Label(self.master,[0,0],(0,0,0),None,18,'',self.states), \
                    Label(self.master,[0,0],(0,0,0),None,18,'',self.states), \
                    Label(self.master,[0,0],(0,0,0),None,18,'',self.states), \
                    Label(self.master,[0,0],(0,0,0),None,18,'',self.states), \
                    Label(self.master,[0,0],(0,0,0),None,18,'',self.states)]
        for i in range(6):
            if i==1 or i==2:
               lbs[i].rect.x = 222+x
            elif i==5:
               lbs[i].rect.x = 196+x
            else:
               lbs[i].rect.x = 227+x
            lbs[i].rect.y = 64+y+24*i
        lbs[0].change(str(g))
        lbs[1].change('+'+str(r))
        lbs[2].change('+'+str(bp))
        lbs[3].change(str(tw))
        lbs[4].change(str(sp))
        lbs[5].change(un)
        self.stat = True

    def change(self, txt):
        self.tbox.change(txt)

    def update(self):
        self.master.scr.blit(self.image, self.rect)
        if self.stat:
            self.master.scr.blit(self.st, self.sr)


class YesNoBox:

    def __init__(self, master, txt_col, bg_col, txt_size, text, indent, \
                 yesfun, nofun, yesargs=None, noargs=None, states=["yesnobox"]):
        """
        Blits an image.
        """
        self.master = master
        self.master.add_widget(self)
        self.cursor = self.master.cursor
        self.states = states
        self.yesfun = yesfun
        self.yesargs = yesargs
        self.nofun = nofun
        self.noargs = noargs
        self.tbox = Textbox(self.master,[400,400],txt_col,bg_col,txt_size,text,3,states)
        self.image = BOX.get_at((0,0,330,334),True)
        self.rect = self.image.get_rect()
        self.rect.center = (512, 384)
        x, y = self.rect.x, self.rect.y
        self.tbox.pos[0] = 28+x
        self.tbox.pos[1] = 28+y
        #self.okb = ImageButton(self.master,[0,0],BOX.get_at((50,483,47,22),True),self.kill, \
        #                  None, states, False, BOX.get_at((50,506,47,22),True), box=True)
        #self.okb.rect.y = 273+y
        #self.okb.rect.x = 138+x
        self.stat = False
        self.st = BOX.get_at((21,336,282,146),False)
        self.sr = self.st.get_rect()
        self.sr.x = 24+self.rect.x
        self.sr.y = 63+self.rect.y
        self.yesb = ImageButton(self.master,[0,0],BOX.get_at((98,483,47,22),True),self.kill, \
                          0, states, False, BOX.get_at((98,506,47,22),True), box=True)
        self.yesb.rect.y = 273+y
        self.yesb.rect.x = 50+x
        self.nob = ImageButton(self.master, [0,0],BOX.get_at((146,483,47,22),True),self.kill, \
                          1, states, False, BOX.get_at((146,506,47,22),True), box=True)
        self.nob.rect.y = 273+y
        self.nob.rect.x = 232+x

    def change(self, txt):
        self.tbox.change(txt)

    def kill(self, n):
        if n==0:
            if self.yesargs!=None:
                self.yesfun(self.yesargs)
            else:
                self.yesfun()
        else:
            if self.noargs!=None:
                self.nofun(self.noargs)
            else:
                self.nofun()

        self.master.freeze()

    def stats(self, g=0, r=0, bp=0, tw=0, sp=0, un='-'):
        self.tbox.change('')
        x, y = self.rect.x, self.rect.y
        p = Image(self.master, [0,0], BOX.get_at((194,483,143,23),True), self.states)
        p.rect.x, p.rect.y = 101+x, 28+y
        z = Label(self.master,[0,0],(0,0,0),None,22,'Do you want to retry?',self.states)
        z.rect.x = 66 + x
        z.rect.y = 229 + y
        lbs = [Label(self.master,[0,0],(0,0,0),None,18,'',self.states), \
                    Label(self.master,[0,0],(0,0,0),None,18,'',self.states), \
                    Label(self.master,[0,0],(0,0,0),None,18,'',self.states), \
                    Label(self.master,[0,0],(0,0,0),None,18,'',self.states), \
                    Label(self.master,[0,0],(0,0,0),None,18,'',self.states), \
                    Label(self.master,[0,0],(0,0,0),None,18,'',self.states)]
        for i in range(6):
            if i==1 or i==2:
               lbs[i].rect.x = 222+x
            elif i==5:
               lbs[i].rect.x = 196+x
            else:
               lbs[i].rect.x = 227+x
            lbs[i].rect.y = 64+y+24*i
        lbs[0].change(str(g))
        lbs[1].change('+'+str(r))
        lbs[2].change('+'+str(bp))
        lbs[3].change(str(tw))
        lbs[4].change(str(sp))
        lbs[5].change(un)
        self.stat = True

    def update(self):
        self.master.scr.blit(self.image, self.rect)
        if self.stat:
            self.master.scr.blit(self.st, self.sr)
