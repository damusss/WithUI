import pygame
import sys

import withui as wui

W, H = 500, 300
pygame.init()
screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()
pygame.display.set_caption("Images Demo")

pygame_logo = pygame.transform.scale_by(
    pygame.image.load("demos/pygame.png").convert_alpha(), 0.5)

with wui.VCont(size=(W, H), **wui.NORESIZE, center_elements=True):
    wui.Image(surface=pygame_logo)
    wui.Slideshow(surfaces=[pygame_logo])

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
