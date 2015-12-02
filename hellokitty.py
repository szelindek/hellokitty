#!/usr/bin/python3
r"""
EASY WAY TO PRINT TEXT:
    # label = MenuItem("The cake is a lie!", default_font, 72, color_lib["white"])
    # posx = get_center(screen.get_width(), label.width)
    # posy = get_center(screen.get_height(), label.height)
    # label.SetPos(posx, posy)
    # screen.blit(label.text, (label.posx, label.posy))

write C extensions:
    collision detection
    other heavy calculation

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

util_chimpy:
    derive from Sprite class
    create RenderPlain==Group class -> sprite handling easier
    Can use „allsprites” or similar, to call the update() func of all sprites at once, and draw them at once

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
    key combo fix -> left HOLD, right HOLD, left RELEASE -> won't move right
    Fix windowed menu position (for quitscene)
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
_active_res = 0
_fullscreen = 0

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

    def Update(self, screen):
        pass

    def Render(self, screen):
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

    def Update(self, screen):
        pass

    def Render(self, screen):
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

    def Update(self, screen):
        pass

    def Render(self, screen):
        self.BlitMenu(screen, color_lib["forest"])

class Bunny:
    def __init__(self, posx, posy, screen):
        # Move 1/200 of the screen in each frame
        self.move_step = screen.get_width() // 200

        # Load bunny, it should be facing right by default
        self.look = load_image(os.path.join(image_dir,"bunny_look.png"))
        self.facing_right = True

        # Scale the look of the bunny depending on the display resolution
        self.rect = pygame.Rect(posx, posy, self.look.get_width(), self.look.get_height())
        ratio = self.rect.h / self.rect.w
        scaled_width = screen.get_width() // 16
        self.look = pygame.transform.smoothscale(self.look, (scaled_width,int(ratio*scaled_width)))

        # Update rect, which is changed due to scaling.
        # The real posy of the bunny is derived from the posy of the ground (input)
        self.rect = pygame.Rect(posx, posy-self.look.get_height(), self.look.get_width(), self.look.get_height())

        # Has one of the defined values in "mov_lib"
        self.moving_dir = 0

    def SetMovingDirection(self, direction, start_movement):
        """Map pressed keys to a bitfield, to determine movement direction"""
        if start_movement:
            if (self.moving_dir | direction) in mov_lib_r:
                self.moving_dir |= direction
        else:
            if (self.moving_dir & ~direction) in mov_lib_r:
                self.moving_dir &= ~direction

    def UpdateCoordinates(self, posx_delta, posy_delta):
        """Change coordinates of the bunny, update the direction it's facing"""
        self.rect.x += posx_delta
        self.rect.y += posy_delta

        # If moving left but facing right, or moving right but facing left,
        # then flip the bunny look, to face in the direction of the movement
        if (posx_delta < 0 and self.facing_right == True) or \
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

class GameScene(SceneBase):
    def __init__(self, screen, active_scene=None):
        SceneBase.__init__(self, screen,
            pygame.Rect(0, 0, screen.get_width(), screen.get_height()))

        pygame.mouse.set_visible(False)

        # Define background settings
        self.ground = pygame.Rect(0, screen.get_height() * 5 // 6, screen.get_width(), screen.get_height() // 6)

        # Create a bunny
        self.bunny = Bunny(screen.get_width() // 20,
                           self.ground.y,
                           screen)

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
                if "left" == mov_lib_r[direction]:
                    self.bunny.UpdateCoordinates(-self.bunny.move_step,0)
                elif "right" == mov_lib_r[direction]:
                    self.bunny.UpdateCoordinates(self.bunny.move_step,0)
                elif "up" == mov_lib_r[direction]:
                    self.bunny.UpdateCoordinates(0,-self.bunny.move_step)
                elif "down" == mov_lib_r[direction]:
                    self.bunny.UpdateCoordinates(0,self.bunny.move_step)
            pow_2 += 1
            tmp = tmp // 2
        # Check the position on both axles
        self.bunny.ForceBoundaries(screen)

    def Render(self, screen):
        screen.fill(color_lib["royalblue"], self.window)

        screen.fill(color_lib["spring"], self.ground)

        #pygame.draw.rect(screen, color_lib["neon"],pygame.Rect(self.bunny.rect.x, self.bunny.rect.y, self.bunny.rect.w, self.bunny.rect.h),1)
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
        active_scene.Update(screen)
        active_scene.Render(screen)

        # Show newly rendered stuff to user and keep fps
        pygame.display.flip()
        clock.tick(fps)

# Execute main function only after the whole script was parsed
if __name__ == "__main__":
    main(60)
