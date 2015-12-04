#!/usr/bin/python3
r"""
EASY WAY TO PRINT TEXT:
    # label = MenuItem("The cake is a lie!", default_font, 72, color_lib["white"])
    # posx = get_center(screen.get_width(), label.width)
    # posy = get_center(screen.get_height(), label.height)
    # label.SetPos(posx, posy)
    # screen.blit(label.text, (label.posx, label.posy))

C extensions?

Animation:
    store image of the background
    replace all to-be-moved objects on screen with background (blitting)
    calculate object movement
    blit all moving objects at their new position
    use display.update(rect_list_to_update) to refresh only changed parts of the screen

Physics:
    RK4 integrator
    fixed time-step
    inputs apply forces
    no inertia?

Options menu:
    Actual value change should be done only when exiting (destroying?) Optionsscene
    Display currently selected resolution and a tick mark for fullscreen
    Add a tip text which explains that changes are automatically saved
    Add background music + mute option (play or stop music) -> global var: _isplaying

# A and B are derived from Rect class
if A.x < B.x + B.w and A.x + A.w > B.x and A.y < B.y + B.h and A.y + A.h > B.y:
    # Collision!

#Circle class: r, x, y -> for radius, center-x, center-y
# A and B are derived from Circle class
if (A.x - B.x)*(A.x - B.x) + (A.y - B.y)*(A.y - B.y) < (A.r + B.r)*(A.r + B.r):
    # Collision!

TEST:
    left HOLD, right HOLD, left RELEASE -> won't move right -> generate multiple keydown events when pressed?
    Fix windowed menu position (for quitscene)
    adjust bunny rect to be pixel-precise
    check block rect and the gap between bunny and block
    include todo.txt here
"""

import os
import sys
import pygame
from libfalcon import *

# Each menu consists of one or more headers for the given scene and one or more
# items which are the possible "buttons" to select. Each item has a second
# parameter which is the name of the function to be called when the given item
# is selected. Empty second parameter means to exit the whole program.
_title_headers  = ("Bunny hop",)
_title_items    = (("Start game", "GameScene"), ("Options", "OptionsScene"),
                   ("Quit", "QuitScene"))
_option_headers = ("Options",)
_option_items   = (("Resolution", "ChangeResolution"), ("Fullscreen", "ToggleFullscreen"),
                   ("Keys", "ChangeKeys"), ("Mute sounds", "ToggleSound"))
_quit_headers   = ("Do you really want to", "leave the bunny alone?")
_quit_items     = (("Yes! I am a bad person...", ""), ("No, of course not!", "TitleScene"))

_resolutions = ((640,360),(960,540))
# Index of the active res from _resolutions
_active_res = 0
# Constant value to set fullscreen mode via display.set_mode
_fullscreen = 0
#
_isplayingsound = False

class TitleScene(SceneBase, MenuBase):
    def __init__(self, screen, active_scene=None):
        SceneBase.__init__(self, screen,
            pygame.Rect(0, 0, screen.get_width(), screen.get_height()))
        MenuBase.__init__(self, screen, _title_headers, _title_items)

    def ProcessInput(self, screen, events, pressed_keys):
        for event in events:
            if event.type == pygame.KEYDOWN:
                return self.HandleKeyboard(screen, event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                return self.HandleMouse(event.button)
        return self.__class__.__name__

    def GenerateOutput(self, screen):
        self.BlitMenu(screen, color_lib["orange"])

class QuitScene(SceneBase, MenuBase):
    def __init__(self, screen, active_scene=None):
        SceneBase.__init__(self, screen,
            pygame.Rect(0, 0, screen.get_width(), screen.get_height()))
        MenuBase.__init__(self, screen, _quit_headers, _quit_items,
            font_size=35, header_font_size=50, spacing_ratio=25)

    def ProcessInput(self, screen, events, pressed_keys):
        for event in events:
            if event.type == pygame.KEYDOWN:
                return self.HandleKeyboard(screen, event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                return self.HandleMouse(event.button)
        return self.__class__.__name__

    def GenerateOutput(self, screen):
        self.BlitMenu(screen, color_lib["dark_orange"])

def ChangeResolution(screen, active_scene):
    global _active_res

    if _active_res == len(_resolutions) - 1:
        _active_res = 0
    else:
        _active_res += 1

    pygame.display.set_mode(_resolutions[_active_res],_fullscreen)

    return OptionsScene(screen)

def ToggleFullscreen(screen, active_scene):
    global _fullscreen

    if _fullscreen == 0:
        _fullscreen = pygame.FULLSCREEN
    else:
        _fullscreen = 0

    pygame.display.set_mode(_resolutions[_active_res],_fullscreen)

    return OptionsScene(screen)

def ToggleSound(screen, active_scene):
    global _isplayingsound

    if _isplayingsound == False:
        _isplayingsound = True
    else:
        _isplayingsound = False

    return OptionsScene(screen)

def ChangeKeys(screen, active_scene):
    return OptionsScene(screen)

class OptionsScene(SceneBase, MenuBase):
    def __init__(self, screen, active_scene=None):
        SceneBase.__init__(self, screen,
            pygame.Rect(0, 0, screen.get_width(), screen.get_height()))
        MenuBase.__init__(self, screen, _option_headers, _option_items,
            font_size=40)

    def ProcessInput(self, screen, events, pressed_keys):
        for event in events:
            if event.type == pygame.KEYDOWN:
                return self.HandleKeyboard(screen, event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                return self.HandleMouse(event.button)
        return self.__class__.__name__

    def GenerateOutput(self, screen):
        self.BlitMenu(screen, color_lib["forest"])

class Bunny(SpriteBase):
    def __init__(self, look_image, scaling, posx, posy, screen):
        SpriteBase.__init__(self, look_image, scaling, posx, posy, screen)

        # Move 1/200 of the screen in each frame -> this is speed (pixel/frame)
        self.move_step = screen.get_width() // 200

        # Bunny should be facing right by default
        self.facing_right = True

        # This will have only one of the values defined in "mov_lib"
        self.moving_dir = 0

    def SetMovingDirection(self, direction, start_movement):
        """Map pressed keys to a bitfield, to determine movement direction"""
        if start_movement:
            if (self.moving_dir | direction) in mov_lib_r:
                self.moving_dir |= direction
        else:
            if (self.moving_dir & ~direction) in mov_lib_r:
                self.moving_dir &= ~direction

    def UpdateCoordinates(self, posx_delta, posy_delta, update_facing_dir=False):
        """Change coordinates of the bunny, update the direction it's facing"""
        self.rect.x += posx_delta
        self.rect.y += posy_delta

        # If moving left but facing right, or moving right but facing left,
        # then flip the bunny look, to face in the direction of the movement
        if update_facing_dir and \
           (posx_delta < 0 and self.facing_right == True) or \
           (posx_delta > 0 and self.facing_right == False):
            self.look = pygame.transform.flip(self.look, True, False)
            self.facing_right = not self.facing_right

    def ForceBoundaries(self, screen):
        """Keep the bunny on-screen, modify coordinates in case it would move outside"""
        if self.rect.x < 0:
            self.rect.x = 0
        elif self.rect.x > screen.get_width() - self.rect.w:
            self.rect.x = screen.get_width() - self.rect.w
        if self.rect.y < 0:
            self.rect.y = 0
        elif self.rect.y > screen.get_height() - self.rect.h:
            self.rect.y = screen.get_height() - self.rect.h

class Ground(SpriteBase):
    def __init__(self, look_image, scaling, posx, posy, screen):
        SpriteBase.__init__(self, look_image, scaling, posx, posy, screen)

class Block(SpriteBase):
    def __init__(self, look_image, scaling, posx, posy, screen):
        SpriteBase.__init__(self, look_image, scaling, posx, posy, screen)

class GameScene(SceneBase):
    def __init__(self, screen, active_scene=None):
        SceneBase.__init__(self, screen,
            pygame.Rect(0, 0, screen.get_width(), screen.get_height()))

        pygame.mouse.set_visible(False)

        # Delay for sending the second KEYDOWN event when helding keys down, and the
        # interval for sending all others. Both in msec
        # pygame.key.set_repeat(100,100)

        # Create ground from small ground elements, which fill up the width of
        # the whole screen
        self.ground_list = []
        self.ground_cnt = 10
        # The x coordinate is increased after creating each ground element, so
        # they will be next to each other
        ground_x = 0
        for i in range(self.ground_cnt):
            self.ground_list.append(Ground("ground.png", self.ground_cnt,
                                    ground_x, screen.get_height(), screen))
            ground_x += self.ground_list[-1].rect.w

        # Create a block
        self.block = Block("block.png", 10, screen.get_width() // 2,
                           self.ground_list[0].rect.y,
                           screen)

        # Create a bunny
        self.bunny = Bunny("bunny_look.png", 16, screen.get_width() // 20,
                           self.ground_list[0].rect.y,
                           screen)

        self.all_blocking = pygame.sprite.Group(self.ground_list, self.block)

    def CheckCollision(self, A):
        for cur_sprite in self.all_blocking:
            B = cur_sprite.rect
            if (A.x < B.x + B.w) and (A.x + A.w > B.x) and \
               (A.y < B.y + B.h) and (A.y + A.h > B.y):
                return True
        return False

    def ProcessInput(self, screen, events, pressed_keys):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # Move back to title scene when escape is pressed
                return "TitleScene"
            elif event.type == pygame.KEYDOWN and event.key in key_lib_r:
                self.bunny.SetMovingDirection(mov_lib[key_lib_r[event.key]],True)
            elif event.type == pygame.KEYUP and event.key in key_lib_r:
                self.bunny.SetMovingDirection(mov_lib[key_lib_r[event.key]],False)

        return self.__class__.__name__

    def Update(self, screen):
        # Update the position of the bunny based on the pressed keys
        tmp = self.bunny.moving_dir
        pow_2 = 0
        while tmp:
            if tmp % 2:
                direction = 2 ** pow_2

                # Short alias to rectangle of the bunny
                A = self.bunny.rect
                # Move the bunny in the desired direction only if there's no collision
                if "left" == mov_lib_r[direction] and \
                   not self.CheckCollision(pygame.Rect(A.x-self.bunny.move_step,A.y,A.w,A.h)):
                    self.bunny.UpdateCoordinates(-self.bunny.move_step,0,True)
                elif "right" == mov_lib_r[direction] and \
                   not self.CheckCollision(pygame.Rect(A.x+self.bunny.move_step,A.y,A.w,A.h)):
                    self.bunny.UpdateCoordinates(self.bunny.move_step,0,True)
                elif "up" == mov_lib_r[direction] and \
                   not self.CheckCollision(pygame.Rect(A.x,A.y-self.bunny.move_step,A.w,A.h)):
                    self.bunny.UpdateCoordinates(0,-self.bunny.move_step,True)
                elif "down" == mov_lib_r[direction] and \
                   not self.CheckCollision(pygame.Rect(A.x,A.y+self.bunny.move_step,A.w,A.h)):
                    self.bunny.UpdateCoordinates(0,self.bunny.move_step,True)
            pow_2 += 1
            tmp = tmp // 2
        # Check the position on both axles
        self.bunny.ForceBoundaries(screen)

    def GenerateOutput(self, screen):
        self.Update(screen)

        screen.fill(color_lib["royalblue"], self.window)

        for ground in self.ground_list:
            screen.blit(ground.look, (ground.rect.x, ground.rect.y))
            pygame.draw.rect(screen, color_lib["purple"], ground.rect, 1)

        screen.blit(self.block.look, (self.block.rect.x, self.block.rect.y))
        pygame.draw.rect(screen, color_lib["cyan"], self.block.rect, 1)

        pygame.draw.rect(screen, color_lib["neon"], self.bunny.rect, 1)
        screen.blit(self.bunny.look, (self.bunny.rect.x, self.bunny.rect.y))

def main(fps):
    pygame.init()

    # Create new cursor from 'cursor_string', where the hotspot is (23,0)
    cursor_string = (
        "            XXXX   XXXX ",
        "           XX..XX XX..XX",
        "           XX...XXX...XX",
        "           XX....XX...XX",
        "            XX...XX..XX ",
        "              XX.XXXXX  ",
        "          XXXXXXXX..XXX ",
        "         XX.XXXXXX....XX",
        "        XXX...XXXXX...XX",
        "       XXX.....XX XX..XX",
        "       XX.......XX  XXX ",
        "      XX........XX      ",
        "     XX.........XX      ",
        "     XX........XXX      ",
        "    XX........XXX       ",
        "   XX........XXX        ",
        "   XX.......XXX         ",
        "  XX......XXX           ",
        " XX......XXX            ",
        " XX....XXX              ",
        "XX....XXX               ",
        "XX..XXX                 ",
        "XXXXXX                  ",
        "XXXX                    "
    )
    cursor, mask = pygame.cursors.compile(cursor_string, 'X', '.', 'O')
    cursor_size = len(cursor_string[0]), len(cursor_string)
    pygame.mouse.set_cursor(cursor_size, (0,23), cursor, mask)

    # Create graphical window
    pygame.display.set_caption("Bunny hop")
    pygame.display.set_icon(load_image(os.path.join(image_dir,"bunny_256.png")))
    screen = pygame.display.set_mode((_resolutions[_active_res][0],
        _resolutions[_active_res][1]))

    clock = pygame.time.Clock()
    next_scene = TitleScene(screen)

    while True:
        active_scene = next_scene
        filtered_events = []
        pressed_keys = pygame.key.get_pressed()

        # Process quit requests, collect all other requests
        for event in pygame.event.get():
            if (event.type == pygame.QUIT) or \
               (event.type == pygame.KEYDOWN and event.key == pygame.K_F4 and \
                (pressed_keys[pygame.K_LALT] or pressed_keys[pygame.K_RALT])):
                return
            else:
                filtered_events.append(event)

        # Work on those inputs
        action = active_scene.ProcessInput(screen, filtered_events, pressed_keys)

        # If the next scene name is empty string, then quit
        if action == "":
            return

        # Execute action, update next_scene and screen
        if action != active_scene.__class__.__name__:
            next_scene = globals()[action](screen, active_scene)
            screen = pygame.display.get_surface()

        # Update active_scene for next iteration of the loop
        active_scene = next_scene

        # Update the logic and render new screen
        active_scene.GenerateOutput(screen)

        # Show newly rendered stuff to user and keep fps
        pygame.display.flip()
        clock.tick(fps)

# Execute main function only after the whole script was parsed
if __name__ == "__main__":
    main(60)
