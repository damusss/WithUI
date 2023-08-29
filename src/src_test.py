# this is literally an ugly test i just need everything to work lmao

import pygame, sys
from withui import withui as wui
pygame.init()
screen = pygame.display.set_mode((1000,700))
clock = pygame.time.Clock()
pygame.display.set_caption("WithUI Testing/Showcase")

colors = ["green", "red", "blue", "yellow", "orange", "pink", "purple"]
surfaces = [pygame.Surface((100,100)) for col in colors]
[surface.fill(colors[i]) for i, surface in enumerate(surfaces)]

wui.UserSettings.add("vcont", 
                     center_elements=True, 
                     **wui.min_max_width(1000), 
                     **wui.min_max_height(700), 
                     **wui.SCROLLABLE)

value = 0
vspeed = 0.2
vdir = 1

def on_move(slider, rel):
    print(slider.value, rel)

with wui.VCont(**wui.UserSettings.get("vcont")) as cont:
    label = wui.Label(text="FPS", anchor = "center", min_width=100, min_height=50)
    wui.Line(height = 3, width_percent=100)
    checkbox = wui.Checkbox(**wui.min_max_square(30))
    button = wui.Button(text="RANDOM BUTTON")
    wui.Slideshow(surfaces=surfaces)
    pb = wui.ProgressBar(width_percent=50, height=40, padding=4, value = 0)
    sl = wui.SelectionList(options=["ciao","come","stai", "io", "bene"], max_height = 100, min_width=200)
    s=wui.Slider(direction="horizontal",value_percent=30, size=300, on_move=on_move)
    wui.Separator(**wui.min_max_square(800))
    
while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
    screen.fill("black")
    
    label.set(text=f"FPS {clock.get_fps():.0f}")
    
    value += vspeed*vdir
    if value > pb.max_value or value < pb.min_value:
        vdir*=-1
        if pb.direction == "left-right": pb.set(direction="right-left")
        else: pb.set(direction="left-right")
    pb.set(value=value)
    
    wui.update_ui()
    wui.draw_ui(screen)
    
    clock.tick(0)
    pygame.display.update()
