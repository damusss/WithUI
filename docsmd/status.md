[<- back to docs](docs.md)

# Element Status

Each element object has an unique status object and attribute, of the `Status` class.

This object is responsible of figuring out when the element is hovered, clicked, selected or released. It's also responsible for calling event callbacks.

The behaviour of this object depends on the settings of the element it's attached to.

# Attributes

## hovering: bool

Whether the element is being hovered

## clicking: bool

Whether the element is being held

## selected: bool

If the element is selectable, whether the element is currently selected

# Methods

## check_click() -> bool

If you don't want to use the callbacks, return True the frame the element is clicked

## check_release() -> bool

If you don't want to use the callbacks, return True the frame the element is released

## select()

Same as `element.status.selected = True`

## deselect()

Same as `element.status.selected = False`

## toggle_selection()

Flip the selected attribute, same as `element.status.selected = not element.status.selected`

## [-> next (element list)](elements.md)
