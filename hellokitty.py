#!/usr/bin/python3
r"""

util_chimpy:
    derive from Sprite class
    create RenderPlain==Group class -> sprite handling easier
    use Rect class for (posx, posy, width, height)
util_functions:
    keyboard control for menu

write C extensions

store image of the background
movement:
    replace all to-be-moved objects on screen with background (blitting)
    calculate object movement
    blit all moving objects at their new position
    use display.update(rect_list_to_update) to refresh only changed parts of the screen

Physics:
    RK4 integrator
    fixed time-step
    inputs apply forces
    no inertia?

detect display resolution and collect possible resolutions:
    pygame.display.list_modes() -> all possible resolutions
    pygame.display.Info() -> display info object
        wm: if false, then only fullscreen is allowed (no windowed mode)
        current_w, current_h: current resolution
    pygame.display.get_wm_info() -> windowed mode info list

defaults for SceneBase.init() -> self.window, font, size, color, ...
"items" list creation to SceneBase init, use self.window as offsetting
init quitscene before main loop and keep in memory
    when titlescene wants to execute quitscene constructor return the existing object


TEST:
    mirror bunny_look.png and spare "transform.flip" from Bunny.init()
    moves continuously when single key hold down
    print(bunny.moving_dir) values while pressing key combos
    can move diagonally
    cannot move left and right same time
    force_boundaries works even in corners
    bunny image ratio is okay on multiple resolutions
    bunny movement speed (bunny.move-step) is scaled to the resolution
    mouse enabled by SceneBase init
    quitscene rendered correctly
    quitscene is functional -> ESCAPE, YES, NO works
    quitscene hides titlescene (titlescene buttons not functional)

"""

import os
import sys
import pygame
from libfalcon import *

# Items of the main menu: tuples of label of the menu item and the scene
# connected to it
_title_items  = (("Bunny hop", "TitleScene"), ("Start game", "GameScene"),
                 ("Options", "OptionsScene"), ("Quit", "QuitScene"))
_option_items = ("Options", "Resolution", "Fullscreen", "Keys", "Mute sounds")
_quit_items   = (("Do you really want to let the bunny down?", "QuitScene"),
                 ("Yes, I am a bad person...", ""),
                 ("No, of course not!", "TitleScene"))

class MenuItem:
    def __init__(self, name, font=default_font, font_size=default_font_size,
                 font_color=default_font_color, scene=""):
        self.name = name
        self.font = font
        self.font_size = font_size
        self.font_color = font_color
        self.scene = scene

        self.text = load_text(name, self.font, self.font_size, self.font_color)

        self.width = self.text.get_width()
        self.height = self.text.get_height()
        self.posx = 0
        self.posy = 0

    def SetPos(self, posx, posy):
        self.posx = posx
        self.posy = posy

    def IsMouseHovered(self, mouse_pos):
        mouse_posx, mouse_posy = mouse_pos
        if self.posx <= mouse_posx and self.posx + self.width > mouse_posx and \
           self.posy <= mouse_posy and self.posy + self.height > mouse_posy:
            return True
        return False

class TitleScene(SceneBase):
    def __init__(self, screen):
        global _title_items

        SceneBase.__init__(self, screen)

        self.font = default_font
        self.header_font_size = default_header_font_size
        self.item_font_size = default_font_size
        self.font_color = default_font_color
        self.items = []

        # For the aesthetical layout, we add a spacing before the title
        # and between the menu options
        spacing = screen.get_height() // 50
        # For the title, the offset is the spacing above it, but for
        # the other menu items, it will be increased with the height
        # of the title and with future spacings which will be put
        # between the menu items
        offset = spacing
        # Exclude the title from the count of menu items
        item_cnt = len(_title_items)-1

        # Create and store menu items
        for index, element in enumerate(_title_items):
            name = element[0]
            scene = element[1]

            # Render the text for current item
            font_size = self.item_font_size
            if index == 0:
                font_size = self.header_font_size
            label = MenuItem(name, self.font, font_size, self.font_color, scene)

            # Center horizontally on the screen, and init vertical position
            # with the current offset
            posx = get_center(screen.get_width(), label.width)
            posy = offset

            if index == 0:
                # Increase offset for "not title" menu items
                offset += label.height + spacing * (item_cnt-1)
            else :
                # The screen height virtually decreased with the offset,
                # the height of each menu item virtually increased with the spacing,
                # and index is decremented, because the title is excluded from indexing
                posy += get_center((screen.get_height() - offset),
                                   (item_cnt * (label.height + spacing))) + \
                        ((index-1) * (label.height + spacing))

            # Update label position and store label
            label.SetPos(posx, posy)
            self.items.append(label)

    def ProcessInput(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                for label in self.items:
                    if label.IsMouseHovered(mouse_pos):
                        return label.scene
        return self.__class__.__name__

    def Update(self, screen):
        pass

    def Render(self, screen):
        screen.fill(color_lib["orange"])

        for label in self.items:
            screen.blit(label.text, (label.posx, label.posy))

class QuitScene(SceneBase):
    def __init__(self, screen):
        global _quit_items

        SceneBase.__init__(self, screen)

        self.window = pygame.Rect(
                       get_center(screen.get_width(), screen.get_width()//2),
                       get_center(screen.get_height(), screen.get_height()//2),
                       screen.get_width()//2,
                       screen.get_height()//2)

        self.font = default_font
        self.header_font_size = default_header_font_size
        self.item_font_size = default_font_size
        self.font_color = default_font_color
        self.items = []

        # For the aesthetical layout, we add a spacing before the title
        # and between the menu options
        spacing = self.window.h // 50
        # For the title, the offset is the spacing above it, but for
        # the other menu items, it will be increased with the height
        # of the title and with future spacings which will be put
        # between the menu items
        offset = spacing
        # Exclude the title from the count of menu items
        item_cnt = len(_quit_items)-1

        # Create and store menu items
        for index, element in enumerate(_quit_items):
            name = element[0]
            scene = element[1]

            # Render the text for current item
            font_size = self.item_font_size
            if index == 0:
                font_size = self.header_font_size
            label = MenuItem(name, self.font, font_size, self.font_color, scene)

            # Center horizontally on the screen, and init vertical position
            # with the current offset
            posx = get_center(self.window.w, label.width) + self.window.x
            posy = offset

            if index == 0:
                # Increase offset for "not title" menu items
                offset += label.height + spacing * (item_cnt-1)
            else :
                # The screen height virtually decreased with the offset,
                # the height of each menu item virtually increased with the spacing,
                # and index is decremented, because the title is excluded from indexing
                posy += get_center((self.window.h - offset),
                                   (item_cnt * (label.height + spacing))) + \
                        ((index-1) * (label.height + spacing)) + self.window.y

            # Update label position and store label
            label.SetPos(posx, posy)
            self.items.append(label)

    def ProcessInput(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # Move back to title scene when escape is pressed
                return "TitleScene"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                for label in self.items:
                    if label.IsMouseHovered(mouse_pos):
                        return label.scene
        return self.__class__.__name__

    def Update(self, screen):
        pass

    def Render(self, screen):
        screen.fill(color_lib["purple"], self.window)

        for label in self.items:
            screen.blit(label.text, (label.posx, label.posy))

class OptionsScene(SceneBase):
    def __init__(self, screen):
        SceneBase.__init__(self, screen)

    def ProcessInput(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # Move back to title scene when escape is pressed
                return "TitleScene"
        return self.__class__.__name__

    def Update(self, screen):
        pass

    def Render(self, screen):
        screen.fill(color_lib["forest"])

        label = MenuItem("The cake is a lie!", default_font, 72, color_lib["white"])
        posx = get_center(screen.get_width(), label.width)
        posy = get_center(screen.get_height(), label.height)
        label.SetPos(posx, posy)
        screen.blit(label.text, (label.posx, label.posy))

class Bunny:
    def __init__(self, posx, posy, screen):
        global image_dir

        # Move 1/50 of the screen in each frame
        self.move_step = screen.get_width() // 50

        # Load bunny, it should be facing right by default
        self.look = load_image(os.path.join(image_dir,"bunny_look.png"))
        self.look = pygame.transform.flip(self.look, True, False)
        self.facing_right = True

        # Scale the look of the bunny depending on the display resolution
        self.width = self.look.get_width()
        self.height = self.look.get_height()
        ratio = self.height / self.width
        scaled_width = screen.get_width() // 16
        self.look = pygame.transform.smoothscale(self.look, (scaled_width,int(ratio*scaled_width)))

        # Store all info for Rect
        self.posx = posx
        self.posy = posy
        self.width = self.look.get_width()
        self.height = self.look.get_height()

        # Has one of the defined values in "mov_lib"
        self.moving_dir = 0

    def moving(self, direction, start_movement):
        global mov_lib_r

        if start_movement:
            if ((self.moving_dir + direction) in mov_lib_r) :
                self.moving_dir += direction
        else:
            if ((self.moving_dir - direction) in mov_lib_r) :
                self.moving_dir -= direction

    def move(self, posx_delta, posy_delta):
        self.posx += posx_delta
        self.posy += posy_delta

        # If moving left but facing right, or moving right but facing left,
        # then flip the bunny look, to face in the direction of the movement
        if (posx_delta < 0 and self.facing_right == True) or \
           (posx_delta > 0 and self.facing_right == False):
            self.look = pygame.transform.flip(self.look, True, False)
            self.facing_right = not self.facing_right

    def force_boundaries(self, screen):
        if self.posx < 0:
            self.posx = 0
        elif self.posx > screen.get_width() - self.width:
            self.posx = screen.get_width() - self.width
        if self.posy < 0:
            self.posy = 0
        elif self.posy > screen.get_height() - self.height:
            self.posy = screen.get_height() - self.height

class GameScene(SceneBase):
    def __init__(self, screen):
        SceneBase.__init__(self, screen)
        pygame.mouse.set_visible(False)

        self.bunny = Bunny(screen.get_width() // 20,
                           screen.get_height() - (screen.get_height() // 3),
                           screen)

    def ProcessInput(self, events, pressed_keys):
        global key_lib_r

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # Move back to title scene when escape is pressed
                return "TitleScene"
            elif event.type == pygame.KEYDOWN and event.key in key_lib_r:
                self.bunny.moving(mov_lib[key_lib_r[event.key]],True)
            elif event.type == pygame.KEYUP and event.key in key_lib_r:
                self.bunny.moving(mov_lib[key_lib_r[event.key]],False)

        return self.__class__.__name__

    def Update(self, screen):
        tmp = self.bunny.moving_dir
        pow_2 = 0
        while tmp:
            if tmp % 2:
                direction = 2 ** pow_2
                if "left" == mov_lib_r[direction]:
                    self.bunny.move(-self.bunny.move_step,0)
                elif "right" == mov_lib_r[direction]:
                    self.bunny.move(self.bunny.move_step,0)
                elif "up" == mov_lib_r[direction]:
                    self.bunny.move(0,-self.bunny.move_step)
                elif "down" == mov_lib_r[direction]:
                    self.bunny.move(0,self.bunny.move_step)
            pow_2 += 1
            tmp = tmp // 2

        self.bunny.force_boundaries(screen)

    def Render(self, screen):
        screen.fill(color_lib["royalblue"])
        pygame.draw.rect(screen, color_lib["neon"], pygame.Rect(self.bunny.posx, self.bunny.posy, self.bunny.width, self.bunny.height),1)
        screen.blit(self.bunny.look, (self.bunny.posx, self.bunny.posy))

def main(width, height, fps):
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
    screen = pygame.display.set_mode((width, height))

    clock = pygame.time.Clock()
    active_scene = TitleScene(screen)

    while True:
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

        next_scene = active_scene.ProcessInput(filtered_events, pressed_keys)
        if next_scene == "":
            # If the next scene name is empty string, then quit
            break
        elif next_scene == active_scene.__class__.__name__ :
            # Don't need to change the scene, we can continue normally
            active_scene.Update(screen)
            active_scene.Render(screen)
        else:
            # Initialize new scene, call the right init function
            active_scene = globals()[next_scene](screen)

        pygame.display.flip()
        clock.tick(fps)

# Execute main function only after the whole script was parsed
if __name__ == "__main__":
    main(640, 360, 60)
