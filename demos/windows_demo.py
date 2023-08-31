import pygame
import sys
import random

import withui as wui

W, H = 1000, 700
pygame.init()
screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()
pygame.display.set_caption("Windows Demo")

pygame_logo = pygame.transform.scale_by(
    pygame.image.load("demos/pygame.png").convert_alpha(), 0.5)

with wui.Window(size=(W//2, H//2), **wui.NORESIZE, title="Bars Demo") as window:
    # another demo inside
    window.inner_container.set(center_elements=True)
    with wui.HCont(width_percent=101, height_percent=102, **wui.NORESIZE, center_elements=True):
        with wui.VCont(**wui.NORESIZE, width_percent=50, height_percent=100, margin=0, **wui.INVISIBLE, center_elements=True):
            wui.Slider(slider_size=200)
            wui.Slider(direction="vertical", slider_size=200)
        with wui.VCont(**wui.NORESIZE, height_percent=100, width_percent=50, margin=0, **wui.INVISIBLE, center_elements=True) as cont:
            with wui.VCont(**wui.NORESIZE, height_percent=30, width_percent=100, margin=0, center_elements=True, **wui.INVISIBLE):
                wui.ProgressBar(value_percent=30, size=(100, 30))
                wui.ProgressBar(direction="right-left",
                                value_percent=40, size=(100, 30), inner_color="green")
            with wui.HCont(**wui.NORESIZE, height_percent=70, width_percent=100, margin=0, center_elements=True, **wui.INVISIBLE):
                wui.ProgressBar(direction="top-bottom",
                                value_percent=80, size=(30, 100), inner_color="red")
                wui.ProgressBar(direction="bottom-top",
                                value_percent=60, size=(30, 100), inner_color="purple")
with wui.Window(size=(W//2, H//2), **wui.NORESIZE, title="Containers Demo", topleft=(W//2, H//2)):
    # another demo inside
    with wui.HCont(width_percent=101, height_percent=102, **wui.NORESIZE, center_elements=True):
        with wui.HCont(**wui.NORESIZE, width_percent=60, height_percent=100, margin=0, center_elements=True, **wui.INVISIBLE):
            with wui.HCont(width_percent=90, height_percent=50, **wui.NORESIZE, **wui.SCROLLABLE):
                for i in range(7):
                    wui.Button(text=f"Button {i}", parent_anchor=random.choice(
                        ["center", "top", "bottom"]))
        with wui.VCont(**wui.NORESIZE, height_percent=100, width_percent=40, margin=0, center_elements=True, **wui.INVISIBLE):
            with wui.VCont(width_percent=90, height_percent=90, **wui.NORESIZE, **wui.SCROLLABLE):
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
