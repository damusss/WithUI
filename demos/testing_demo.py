# showcase-like test

import pygame
import sys
import withui as wui

pygame.init()

screen = pygame.display.set_mode((1000, 700))
clock = pygame.time.Clock()
pygame.display.set_caption("WithUI Testing/Showcase")

colors = ["green", "red", "blue", "yellow", "orange", "pink", "purple"]
surfaces = [pygame.Surface((100, 100)) for col in colors]
[surface.fill(colors[i]) for i, surface in enumerate(surfaces)]

pygame_logo = pygame.transform.scale_by(
    pygame.image.load("demos/pygame.png").convert_alpha(), 0.5)

wui.UserSettings.add("vcont",
                     center_elements=True,
                     min_max_size=(1000, 700),
                     **wui.SCROLLABLE)

value = 0
vspeed = 0.2
vdir = 1

wui.Themes.set_default("dark")

tt_manager = wui.ext.TooltipManager()

with wui.VCont(**wui.UserSettings.get("vcont")) as cont:
    label = wui.Label(text="Label", anchor="center",
                      min_width=100, min_height=50)
    tt_manager.register_tooltip(
        label, "FPS Label", "display fps to check the performance of the UI")
    animated_label = wui.Label()
    wui.ext.TypingAnimation(
        animated_label, "This thing, will appear. animated \nyes").start()

    wui.Line(height=3, width_percent=100)
    checkbox = wui.Checkbox(min_max_size=(30, 30))
    button = wui.Button(text="RANDOM\n BUTTON", width=100, height=100, auto_resize_h=True, auto_resize_v=True,
                        background_image=pygame_logo, has_background=False, text_color="black", background_padding=5, adapt_to_bg=True)
    wui.ext.HoverGrowAnimation(button, pygame_logo)
    wui.Slideshow(surfaces=surfaces)
    wui.GIF(frames=surfaces, frame_cooldown=500)
    pb = wui.ProgressBar(width_percent=50, height=40, padding=4, value=0)
    wui.SelectionList(
        options=["ciao", "come", "stai", "io", "bene"], max_height=100, min_width=200)
    wui.Slider(direction="horizontal", value_percent=30, slider_size=300)
    e = wui.Entryline(width=400)
    tt_manager.register_tooltip(
        e, "Entryline", "another tooltip example wow incredible i know")
    wui.DropMenu(options=["io", "sono", "tua", "madre",
                 "in", "realta"], min_max_width=200)
    wui.Separator(min_max_size=(800, 800))

with wui.Window(min_max_size=(300, 300)):
    for i in range(20):
        wui.Button(text="win button")

dialog = wui.ext.FileDialog((200, 200), 400, 300, filter_extensions=["txt"])

while True:
    for e in pygame.event.get():
        wui.register_event(e)
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    dt = clock.tick(0)*0.001
    screen.fill("black")

    label.set(text=f"FPS {clock.get_fps():.0f}")

    value += vspeed*vdir
    if value > pb.max_value or value < pb.min_value:
        vdir *= -1
        if pb.direction == "left-right":
            pb.set(direction="right-left")
        else:
            pb.set(direction="left-right")
    pb.set(value=value)

    tt_manager.update()
    wui.ext.AnimationsManager.update(dt)
    wui.update_ui()
    result = wui.raycast(pygame.mouse.get_pos())
    wui.draw_ui(screen)

    pygame.display.update()
