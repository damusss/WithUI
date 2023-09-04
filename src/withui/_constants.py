import pygame
import typing

_ColorValue = pygame.Color | str | tuple[int, int,
                                         int] | tuple[int, int, int, int] | list[int]
_Coordinate = pygame.Vector2 | tuple[float,
                                     float] | list[float] | typing.Iterable[float]

_ZERO_VEC = pygame.Vector2()
_SCROLLBAR_SIZE = 15
_SLIDER_SIZE = 15
_HANDLE_SIZE = 25

_FONT_ALIGN_LOOKUP = {
    "center": pygame.FONT_CENTER,
    "left": pygame.FONT_LEFT,
    "right": pygame.FONT_RIGHT
}

_SETTINGS_HELP = {
    "Element": {
        "offset": "Vector that will offset the element relative to it's normal position",
        "margin": "How much the element is separated from nearby elements. Same for all directions",
        "center_elements": "If enabled, containers will center elements in their axis and in the opposite axis unless the element has a different anchor",
        "free_position": "The element will not be forced in a grid by the container. This position is relative to the parent",
        "draw_top": "If enabled, the element will be drawn after anything else has been drawn",
        "ignore_scroll": "If enabled, the element won't move when the container scrolls",
        "parent_anchor": "The element will stay attached to one side/center of the parent container. Some anchors are only allowed in some containers",
        "border_radius": "How much the corners of shapes will be rounded",
        "outline_width": "How thick the outline of the element is",
        "padding": "How much the inner surface of the element, if any, is separated from the borders",
        "background_color": "Color to fill the background when the element is not pressed or hovered if has_background flag is enabled",
        "dark_bg_color": "Color used overriding background_color if has_dark_bg flag is enabled",
        "hover_color": "Color to fill the background when the element is hovered if can_hover and show_hover flags are enabled",
        "click_color": "Color to fill the background when the element is being held, if can_press and show_press flags are enabled",
        "outline_color": "Color of the outline if has_outline flag is true",
        "text_color": "Color of the text, if any",
        "inner_color": "Color for shapes inside the element, if any",
        "background_image": "If not None, it's the surface drawn after filling the background and before drawing the outline",
        "background_anchor": "The anchor of the background image relative to the element",
        "background_padding": "The margin between the borders and the background image",
        "resize_background": "Whether the background image should be resized when the element size changes",
        "adapt_to_bg": "Whether the element size should be the same as the background image (+ padding). Does not interfer with the auto resize settings",
        "bg_effect_alpha": "The alpha used when filling the image with the interaction color (hover / press)",
        "bg_hover_flag": "The pygame blend flag constant passed as a special flag when filling the image with the hover color",
        "bg_press_flag": "The pygame blend flag constant passed as a special flag when filling the image with the click color",
        "font_size": "The size of the font for the text",
        "font_name": "The file name or the font. None is allowed",
        "sysfont_name": "If it's not None, it overrides font_name and calls pygame.font.SysFont instead",
        "font_antialas": "Antialas flag for text rendering",
        "text_align": "If text wrapping is enabled (check auto_resize_h), Text that falls into a new line will be aligned depending on the value. Available are left, right center or pygame constants (FONT_CENTER, FONT_LEFT, FONT_RIGHT)",
        "auto_resize_h": "If enabled, elements will be able to resize automatically horizontally, if needed. If disabled, it will enable text wrapping for labels and buttons",
        "auto_resize_v": "If enabled, elements will be able to resize automatically vertically, if needed. This flag doesn't affect text wrapping and should be kept enabled for labels and buttons",
        "width": "Current width of the element. Might be changed by the element during runtime",
        "height": "Current height of the element. Might be changed by the element during runtime",
        "min_width": "The width of the element will never be smaller than this value",
        "min_height": "The height of the element will never be smaller than this value",
        "max_width": "The width of the element will never be grater than this value",
        "max_height": "The height of the element will never be grater than this value",
        "width_percent": "If not None, overrides the width using it as a percentage relative to the parent width",
        "height_percent": "If not None, overrides the height using it as a percentage relative to the parent height",
        "size": "Both width and height are updated with the iterable",
        "min_size": "Both min_width and min_height are updated with the iterable",
        "max_size": "Both max_width and max_height are updated with the iterable",
        "min_max_width": "Width, min_width and max_width are set to the same value",
        "min_max_height": "Height, min_height and max_height are set to the same value",
        "min_max_size": "Width, min_width, max_width, height, min_height, max_height are set to the same values from the iterator",
        "visible": "If enabled, the element and its children will be drawn",
        "active": "If enabled, the element and its children will be updated",
        "on_hover": "Called every frame the element is hovered if can_hover flag is enabled",
        "on_press": "Called every frame the element is hovered if can_press flag is enabled",
        "on_click": "Called the frame the element is clicked if can_press flag is enabled",
        "on_release": "Called the frame the element is not clicked anymore if can_press flag is enabled",
        "on_select": "Called when the element is selected if can_select flag is enabled",
        "on_deselect": "Called when the element is deselected if can_select flag is enabled",
        "on_toggle": "Set both on_select and on_deselect with the same callback",
        "can_hover": "If enabled, the element will fire hover events",
        "can_press": "If enabled, the element will fire press, click and release events",
        "can_select": "If enabled, the element will fire select and deselect events",
        "show_hover": "If enabled, when the element is hovered the background will change color if can_hover and has_background flags are enabled",
        "show_press": "If enabled, when the element is held the background will change color if can_press and has_background flags are enabled",
        "can_scroll_v": "If enabled, allows containers to scroll vertically",
        "can_scroll_h": "If enabled, allows containers to scroll horizontally",
        "scroll_offset": "The scrolling offset of a container. Should not be changed manually",
    },
    "Button": {
        "text": "The text shown in the button",
        "surface": "The surface shown in the button",
        "inner_anchor": "Where the surface/text is positioned relative to the element"
    },
    "Label": {
        "text": "The text shown in the label",
        "inner_anchor": "Where the text is positioned relative to the element"
    },
    "Image": {
        "surface": "The surface shown in the image",
        "inner_anchor": "Where the surface is positioned relative to the element"
    },
    "Checkbox": {

    },
    "Separator": {

    },
    "Line": {

    },
    "ProgressBar": {
        "min_value": "The minimum value used for calculations",
        "max_value": "The maximum value used for calculations",
        "value": "The current value clamped between min and max",
        "value_percent": "If not None, overrides the value using the percentage between min and max",
        "direction": "The direction the bar fills in. Available: left-right, right-left, top-bottom, bottom-top",
    },
    "VCont": {

    },
    "HCont": {

    },
    "Slideshow": {
        "surfaces": "The surfaces that will be displayed in the slideshow. An empty will result in weird behaviour",
        "surface_index": "Manually change the current surface"
    },
    "SelectionList": {
        "options": "Set the selection list options",
        "multi_select": "Whether the user can select one or more options",
        "selected_option": "Manually set the selected option. Only if multi_select is disabled",
        "selected_options": "Manually set the selected options. Only if multi_select is enabled"
    },
    "Slider": {
        "slider_size": "Set either the width or the height depending on the direction",
        "direction": "The slider direction. Available are horizontal and vertical",
        "value": "Manually set the value, which goes from 0 to 1",
        "value_percent": "Manually set the value using percentage (0-100)",
        "handle_size": "The size of the slider handle",
        "on_move": "Called whenever the handle position changes. Pass as parameters the slider itself and the movement delta"
    },
    "DropMenu": {
        "selected_option": "Manually set the currently selected option",
        "options": "Change the options shown in the menu",
        "menu_optn": "Manually set the options menu visibility",
        "direction": "Whether the options menu should appear below or above the arrow. Available are up and down",
        "down_arrow": "If you don't like the default down arrow or your font doesn't have it you can try with another character",
        "up_arrow": "If you don't like the default up arrow or your font doesn't have it you can try with another character",
    },
    "Window": {
        "title": "The title button text. To change more settings, use the title_button property",
        "on_close": "Called when the close button is clicked. Before the callback is called the window is hidden",
        "topleft": "Modify the topleft position of the window manually",
        "can_drag": "Whether holding the title button will make the window move or not"
    },
    "Entryline": {
        "text": "Manually set the text in the entryline",
        "cursor_width": "How wide is the cursor",
        "blink_time": "How frequently the cursor blinks",
        "enable_empty": "Whether the placeholder will be inserted or not",
        "placeholder": "The text inserted when the entryline is empty and out of focus, if enable_empty is false",
        "focused": "Manually focus or unfocus the entryline",
        "on_focus": "Called when the entryline is focused or unfocused",
        "on_change": "Called when the entryline text is changed",
        "on_copy": "Called when the selection of the entryline is copied",
        "on_paste": "Called when a paste operation occurs"
    },
    "GIF": {
        "inner_anchor": "Where the images are anchored",
        "frames": "The gif frames",
        "frame_cooldown": "How much time between every frame in milliseconds"
    }
}
