[<- back to elements](../elements.md)

# Drop Menu

## inherit HCont

A wrapper of different elements in order to create either a dropdown or a dropup, depending on the direction

You can use the following settings:
- selected_option
- options
- direction - up/down
- menu_open
- down_arrow
- up_arrow

menu_open and selected_option can also be obtained/changed with the `menu_open` and `selected` properties

When the user select a new option, the `on_select` callback is called.

## open_menu(), close_menu(), toggle_menu()

This methods change the visibility of the options menu.

## apply_settings_to_options(**kwargs)

This method will pass the kwargs settings to each option button, this way you can customize them easly.