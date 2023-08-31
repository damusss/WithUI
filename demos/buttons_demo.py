import pygame
import sys

import withui as wui

W, H = 500, 300
pygame.init()
screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()
pygame.display.set_caption("Buttons Demo")

with wui.VCont(size=(W, H), **wui.NORESIZE, center_elements=True):
    wui.Button(text="Button")
    wui.Button(text="Button Wrapped", width=100, auto_resize_h=False)
    wui.Checkbox(size=(30, 30))
    wui.Checkbox(size=(30, 30)).status.select()

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
