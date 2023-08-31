import pygame
import sys

import withui as wui

W, H = 600, 400
pygame.init()
screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()
pygame.display.set_caption("Menus Demo")

with wui.HCont(size=(W, H), **wui.NORESIZE, center_elements=True):
    with wui.VCont(**wui.NORESIZE, width_percent=40, height_percent=100, margin=0, **wui.INVISIBLE, center_elements=True):
        wui.SelectionList(options=["Different", "Options", "In", "The", "Selection",
                          "List", "As", "You", "Can", "See"], width_percent=60, height_percent=60, **wui.NORESIZE, multi_select=True)
    with wui.HCont(**wui.NORESIZE, height_percent=100, width_percent=60, margin=0, **wui.INVISIBLE, center_elements=True):
        wui.DropMenu(options=["Dropdown", "With", "Some", "Options"],
                     selected_option="Choose", min_max_width=150).menu_open = True
        wui.DropMenu(options=["Dropup", "With", "Some", "Options"],
                     selected_option="Choose", direction="up", min_max_width=150).menu_open = True

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
