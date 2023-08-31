import pygame
import sys

import withui as wui

W, H = 800, 500
pygame.init()
screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()
pygame.display.set_caption("Bars Demo")

with wui.HCont(size=(W, H), **wui.NORESIZE, center_elements=True):
    with wui.VCont(**wui.NORESIZE, width_percent=50, height_percent=100, margin=0, **wui.INVISIBLE, center_elements=True):
        wui.Slider(slider_size=300)
        wui.Slider(direction="vertical", slider_size=300)
    with wui.VCont(**wui.NORESIZE, height_percent=100, width_percent=50, margin=0, **wui.INVISIBLE, center_elements=True):
        with wui.VCont(**wui.NORESIZE, height_percent=30, width_percent=100, margin=0, center_elements=True, **wui.INVISIBLE):
            wui.ProgressBar(value_percent=30, size=(300, 30))
            wui.ProgressBar(direction="right-left",
                            value_percent=40, size=(300, 30), inner_color="green")
        with wui.HCont(**wui.NORESIZE, height_percent=70, width_percent=100, margin=0, center_elements=True, **wui.INVISIBLE):
            wui.ProgressBar(direction="top-bottom",
                            value_percent=80, size=(30, 300), inner_color="red")
            wui.ProgressBar(direction="bottom-top",
                            value_percent=60, size=(30, 300), inner_color="purple")

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
