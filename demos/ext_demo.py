import pygame
import sys

import withui as wui

W, H = 800, 500
pygame.init()
screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()
pygame.display.set_caption("Demo Layout")

tt_manager = wui.ext.TooltipManager()

pygame_logo = pygame.transform.scale_by(
    pygame.image.load("demos/pygame.png").convert_alpha(), 0.5)

with wui.VCont(size=(W, H), **wui.NORESIZE, center_elements=True):
    tt_manager.register_tooltip(wui.Label(text="Hover to show tooltip"), "Example Tooltip",
                                "This is how the description will appear. You can customize everything")
    wui.ext.TypingAnimation(wui.Label(
    ), "This very, very cool label will appear slowly.\n And speed changes when there are punctuation marks!")
    btn = wui.Button(width=100, height=100, background_image=pygame_logo,
                     has_background=False, has_outline=False, text_color="black", background_padding=5)
    wui.ext.HoverGrowAnimation(btn, pygame_logo)

wui.ext.FileDialog((200, 100), 400, 300)

dt = 1
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

    tt_manager.update()
    wui.ext.AnimationsManager.update(dt)

    wui.draw_ui(screen)

    dt = clock.tick(60)*0.001
    pygame.display.update()
