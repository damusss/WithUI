import pygame
import sys

import withui as wui

W, H = 1120, 240
pygame.init()
screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()
pygame.display.set_caption("Themes Demo")

x = 20
for i,theme in enumerate(["Dark","Blue","Green","Purple","Red"]):
    wui.Themes.set_default(theme)
    with wui.Window(size=(200,200), **wui.NORESIZE, title=f"{theme} Theme", topleft=(x,20)):
        with wui.HCont(**wui.INVISIBLE):
            wui.Label(text="Inner Color", font_size=18)
            wui.Checkbox(size=(30,30)).status.select()
        wui.Button(text="Hovering", background_color=wui.DefaultSettings.hover_color)
        wui.Button(text="Selected", can_select=True).status.select()
    x += 220

while True:
    for event in pygame.event.get():
        wui.register_event(event)
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                pygame.image.save(screen, "demos/screenshot.png")

    screen.fill("black")

    wui.update_ui()

    wui.draw_ui(screen)

    clock.tick(60)
    pygame.display.update()
