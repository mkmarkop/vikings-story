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

import pygame.mixer

pygame.mixer.init()


class SoundManager:

    def __init__(self):
        """
        Class for managing sound effects and 
        background music
        """
        self.bg_volume = 1
        self.se_volume = 1
        self.music_lib = {"menu":"./data/music/CAP-Woods_of_Eremae.mp3", \
                          "game":"./data/music/CAP-Virtue_lost.mp3", \
                          "intro":"./data/music/CAP-The_saga_begins.mp3", \
                          "shop":"./data/music/CAP-Alchemist.mp3"}
        self.sound_lib = {"arrow":pygame.mixer.Sound("./data/sounds/braqoon_arrow-damage.wav"), \
                          "build":pygame.mixer.Sound("./data/sounds/cinevid_fallingdown.wav"), \
                          "lightning":pygame.mixer.Sound("./data/sounds/parnellij_lightning-strike.wav"), \
                          "hammer":pygame.mixer.Sound("./data/sounds/ingudios_shock.wav"), \
                          "swords":pygame.mixer.Sound("./data/sounds/black-snow_sword-slice-23.wav"), \
                          "shockwave":pygame.mixer.Sound("./data/sounds/sarge4267_explosion4.wav"), \
                          "spell":pygame.mixer.Sound("./data/sounds/northern-monkey_buffer-spell.wav")}
        self.current = None
        self.paused = False

    def change_volume(self, sound_type, volume):
        """
        Changes the volume of sound effects
        or background music
        """
        if sound_type == "background":
            self.bg_volume = volume
            pygame.mixer.music.set_volume(self.bg_volume)
        elif sound_type == "sound":
            self.se_volume = volume
            for sound in self.sound_lib:
                self.sound_lib[sound].set_volume(volume)

    def change_music(self, track):
        """
        Tries to change the track to the
        given one, if volume isn't 0
        """
        try:
            if self.bg_volume != 0:
                self.current = self.music_lib[track]
                pygame.mixer.music.load(self.current)
                pygame.mixer.music.play(-1)
                self.current = track
            else:
                pygame.mixer.music.stop()
        except:
            print "Couldn't load track '", track + "'!"     

    def pause(self):
        """
        (Un)pauses all music
        """
        if self.paused:
            pygame.mixer.unpause()
            self.paused = False
        else:
            pygame.mixer.pause()
            self.paused = True

    def play_sound(self, sound):
        """
        Tries to play the given sound
        from the library
        """
        try:
            if self.se_volume != 0:
                self.sound_lib[sound].play()
        except:
            print "Couldn't play the sound '", sound, "'!"
            
    def stop(self, time=100):
        """
        Fades out all music and stops it
        """
        pygame.mixer.fadeout(time)
