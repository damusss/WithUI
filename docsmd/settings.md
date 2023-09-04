[<- back to docs](docs.md)

# Element Settings

The settings for each element are stored in an object that is unique for every element.

Every element that is not a base element has often some custom settings. Always use the `set()` method.
You can also pass settings to the constructor of the element and you'll have the same result.

To know about each setting use the following method:

```py
withui.pretty_print(withui.settings_help(element))
# or
print(withui.settings_help(element, "setting_name"))
```

Additional constants that you can find in the end of the documentation will help with quick settings

## How to change the default settings?

The `Settings` class is privated in the base module, but it's still accessible renamed to `DefaultSettings`

WARNING: If you want to change font settings, refresh the font object!

### Example

```py
withui.DefaultSettings.margin = 10
# all elements by default have this margin
withui.DefaultSettings.font_size = 30
# don't forget this!
withui.refresh_default_font()
```

## Can i cache my own settings to use multiple times?

Yes you can, you only need to use the `UserSettings` static class.

It holds your custom settings in a dictionary and you can retrieve them. They are saved in dictionaries, so when you call the `get()` method don't forget to unpack it (unpack operator: `**`)

### Example

```py
withui.UserSettings.add(
    "custom_button",
    width=200,
    has_outline=False,
    padding=15,
)

# don't forget the unpack operator!
withui.Button(**withui.UserSettings.get("custom_button"), text="Button 1")
withui.Button(**withui.UserSettings.get("custom_button"), text="Button 2")
withui.Button(**withui.UserSettings.get("custom_button"), text="Button 3")
```

## [-> next (element status)](status.md)
