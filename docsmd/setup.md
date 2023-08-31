[<- back to docs](docs.md)

# Setup

## Importing
Import WithUI just like you would import anything else
```py
import withui
```
This will give you access to all public classes, constants and functions as defined in `__init__.py` <br>
I suggest renaming the module for quicker typing
```py
import withui as wui
```
# Element tree structure

Your tree structure should begin after pygame initialization and before the main loop.<br>

To indicate that you want elements to be children of another element, use the `with` statement in python. this will also grant parentship indentation.<br>

## Example
```py
import withui as wui
#...
with wui.Window(title="Example window", size=(500,400)) as window:
    wui.Button(text="I am inside the window container")
    with wui.HCont(**wui.INVISIBLE):
        wui.Button(text="Side by side 1")
        wui.Button(text="Side by side 2")
# main loop
```

Using the statement such as `with <WithUI Element>() as element` you can save your parent element in a variable. <br>
Check the rest of the documentation for more about elements.

# Updating the UI

3 methods are needed to correctly update the UI<br>

`withui.register_event(event:pygame.event.Event)`<br>
Call this function for every event in your game loop <br>

`withui.update_ui()`<br>
Call this in your main loop always before drawing the ui<br>

`withui.draw_ui()`<br>
Call this in your main loop always after updating, after filling the screen and before updating the pygame display

## Example
```py
# code before main loop
while True:
    # ...
    for event in pygame.event.get():
        withui.register_event(event)
        # other events such as pygame.QUIT
    # ...
    screen.fill("black")
    # ...
    withui.update_ui()
    # ...
    withui.draw_ui()
    # ...
    clock.tick(60)
    pygame.display.update()
```

## [-> next (base element)](element.md)