import pygame
import sys
import random

import withui as wui

W, H = 1000, 700
pygame.init()
screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()
pygame.display.set_caption("Containers Demo")

with wui.HCont(size=(W, H), **wui.NORESIZE, center_elements=True):
    with wui.HCont(**wui.NORESIZE, width_percent=60, height_percent=100, margin=0, center_elements=True, **wui.INVISIBLE):
        with wui.HCont(width_percent=80, height_percent=20, **wui.NORESIZE, **wui.SCROLLABLE):
            for i in range(7):
                wui.Button(text=f"Button {i}", parent_anchor=random.choice(
                    ["center", "top", "bottom"]))
    with wui.VCont(**wui.NORESIZE, height_percent=100, width_percent=40, margin=0, center_elements=True, **wui.INVISIBLE):
        with wui.VCont(width_percent=80, height_percent=80, **wui.NORESIZE, **wui.SCROLLABLE):
            for i in range(20):
                wui.Button(text=f"Button {i}", parent_anchor=random.choice(
                    ["left", "right", "center"]))

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
