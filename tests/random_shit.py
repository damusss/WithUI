# this is literally an ugly test i just need everything to work lmao

import pygame, sys
import withui as wui

pygame.init()
screen = pygame.display.set_mode((1000,700))
clock = pygame.time.Clock()

def on_click(btn:wui.Button):
    btn.set(text=btn.text+"1")

surf = pygame.Surface((200,50))
surf.fill("red")

wui.UserSettings.add("vcont", center_elements=True, min_width=1000, max_width=1000, max_height=700, min_height=500, **wui.SCROLLABLE)

with wui.VCont(**wui.UserSettings.get("vcont")) as cont:
    wui.Button(surface=surf, anchor = "center", min_width=100, min_height=50, can_select=False, on_click=on_click, padding=20)
    wui.Button(text="Test", anchor = "center", min_width=100, min_height=50, can_select=False, on_click=on_click, free_position=(100,100), draw_top=True)
    label = wui.Label(text="Test", anchor = "center", min_width=100, min_height=50, can_select=False, on_click=on_click)
    for i in range(15):
        wui.Button(text="Test"*10, anchor = "center", min_width=100, min_height=50, can_select=False, on_click=on_click)

while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
    screen.fill("black")
    
    label.set(text=f"FPS {clock.get_fps():.0f}")
    wui.update_ui()
    wui.draw_ui(screen)
    
    clock.tick(0)
    pygame.display.update()
