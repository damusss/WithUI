[<- back to docs](docs.md)

# Base Element

All elements in WithUI inherit from the `Element` class. It's suggested not to create empty elements, but it's important to know about it as all elements also inherit everything from it.

# Main components

### Status

Accessible from the `status` attribute, of type `Status` <br>
[Status in detail](status.md)

### Settings

Accessible from the `settings` attribute, of type `Settings` <br>
[Settings in detail](status.md)

Most of the attributes and method are prefixed with an underscore: they are used internally and interacting with them will result in undefined behaviour and possibly exceptions

# Methods

## set(\*\*kwargs)

This is the most important method. It's used to update the settings object.
<br>Why use this and not use the settings attribute?

- Other elements might have settings that aren not available in the settings object
- Some settings need the refresh of the element or of other settings (for example, when you change font size the font is re-created)

How to give arguments to it?<br>
This methods take only keyword arguments, but they are not listed. To know about all the possible settings, use `withui.settings_help(element)`

#### Example

```py
withui.Button(width=100, text="Button text")
```

## show()

Same as `set(visible=True)`

## hide()

Same as `set(visible=False)`

## activate()

Same as `set(active=True)`

## deactivate()

Same as `set(active=False)`

## point_hovering(point: Coordinate) -> bool

Return whether a point is inside the element's rect using the absolute position

## is_root() -> bool

Return whether the element is a tree element

## kill()

Deletes the element from every place its referenced

## move_in_parent(places: int = 1) -> bool

Move the element a specified amount of places through the parent's children if any. Return whether the element position changed

# Properties

## parent: Element | None

The element this element is children of

## children: list[Element]

A copy of the list containing the element's children

## root: Element

The root element this element is under of. If the element is root, the propery returns the element

## absolute_rect: pygame.Rect

A copy of the rect relative to the window position used for interaction calculations

## relative_rect: pygame.Rect

A copy of the rect which topleft is relative to its parent

## [-> next (element settings)](settings.md)
