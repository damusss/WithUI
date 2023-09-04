[<- back to docs](docs.md)

# Other

In addition to the rest, there are still a few things left!

# Clipboard

Very small class, it's a wrapper for the scrap module.

Only have a `put(text:str)` method to update the clipboard and `get()` to retrieve data from it

# Constants

## INVISIBLE

It's a shortcut for the following settings

- has_background = False
- has_outline = False

Shortcut to remove the background and outline

```py
# don't forget the unpack operator!
withui.Button(text="Invis Bg", **withui.INVISIBLE)
```

## SCROLLABLE

It's a shortcut for the following settings

- can_scroll_h = True
- can_scroll_v = True

Shortcut to allow containers to scroll

```py
# don't forget the unpack operator!
with withui.VCont(**withui.SCROLLABLE, min_max_height=500) as cont:
    # a lot of elements that overflow the height!
```

## STATIC

It's a shortcut for the following settings

- can_hover = False
- can_press = False

Shortcut to remove interactiveness from an element

```py
# don't forget the unpack operator!
withui.Button(text="I cannot be interacted in any way!", **withui.STATIC)
```

## NORESIZE

It's a shortcut for the following settings

- auto_resize_h = False
- auto_resize_v = False

Shortcut to remove auto resizing on all axis

```py
# don't forget the unpack operator!
withui.VCont(size=(500,500), **withui.NORESIZE)
```

## MODERN_ARROW_DOWN / MODERN_ARROW_UP

This constants hold strings for pretty arrows to use in drop menus. The problem is most fonts don't support them, therefore the default strings are `v` and `^`.

If your font support this arrows, put them using the drop menu `down_arrow` and `up_arrow` settings.

# Functions

## set_hover_sound(sound: pygame.mixer.Sound)

Set the sound that will play when hovering an element

## set_click_sound(sound: pygame.mixer.Sound)

Set the sound that will play when clicking an element

## get_all_elements() -> list[Element]

Return a copy of the list containing all elements existing. Useful to apply settings like a theme during runtime

## apply_settings_to_all_elements(\*\*kwargs)

Apply the given settings as keyword arguments to all elements existing. Useful to apply settings like a theme during runtime

## settings_help(element: str | Element | type[Element], setting: str | None) -> dict | str

As said in [Element Settings](settings.md), use this function to know about the settings available for every element

## enable_keyboard_navigation() / disable_keyboard_navigation()

Toggle whether ui elements can be navigated using the keyboard

## pretty_format(json_like_object) -> str

Formats a json like object with pretty indentation. If you put a string by mistake nothing bad will happen!

## pretty_print(json_like_object) -> str

Formats a json like object with pretty indentation and print it immediately. If you put a string by mistake nothing bad will happen!

It's suggested to be used while printing settings from `settings_help()`

## refresh_default_font()

If you change font settings in `DefaultSettings`, don't forget to call this function!

## [-> next (extension module)](ext.md)