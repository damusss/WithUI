import pygame
import typing
import json
pygame.init()

_ColorValue = pygame.Color | str | tuple[int, int,
                                         int] | tuple[int, int, int, int] | list[int]
_Number = int | float
_Coordinate = pygame.Vector2 | tuple[_Number,
                                     _Number] | list[_Number] | typing.Iterable[_Number]


class _WithUIException(Exception):
    ...


class _UIManager:
    last_element: "_Element" = None
    tree_elements: list["_Element"] = []
    top_elements: list["_Element"] = []
    mouse_buttons = None
    mouse_pos = None
    mouse_rel = None
    keys = None
    was_clicking = False
    frame_events: list[pygame.event.Event] = []
    frame_ended = False
    ticks = 0

    @classmethod
    def update(cls):
        if cls.mouse_buttons:
            cls.was_clicking = cls.mouse_buttons[0]
        cls.mouse_buttons = pygame.mouse.get_pressed()
        cls.mouse_pos = pygame.mouse.get_pos()
        cls.mouse_rel = pygame.mouse.get_rel()
        cls.keys = pygame.key.get_pressed()
        cls.ticks = pygame.time.get_ticks()


class _Settings:
    # positioning
    offset: pygame.Vector2 = None
    margin: _Number = 5
    center_elements: bool = False
    free_position: pygame.Vector2 = None
    draw_top: bool = False
    ignore_scroll: bool = False
    parent_anchor: str = None
    # style
    border_radius: _Number = 4
    outline_width: _Number = 1
    padding: _Number = 3
    # style color
    background_color: _ColorValue = (30, 30, 30)
    dark_bg_color: _ColorValue = (15, 15, 15)
    hover_color: _ColorValue = (40, 40, 40)
    click_color: _ColorValue = (22, 22, 22)
    outline_color: _ColorValue = (50, 50, 50)
    text_color: _ColorValue = (255, 255, 255)
    inner_color: _ColorValue = (0, 100, 200)
    # style flags
    has_background: bool = True
    has_outline: bool = True
    has_dark_bg: bool = False
    # text
    font_size: int = 20
    font_name: str = None
    sysfont_name: str = "NotoSans"
    font_antialas: bool = True
    font: pygame.font.Font = pygame.font.SysFont(sysfont_name, font_size)
    # size
    width: _Number = 0
    height: _Number = 0
    min_width: _Number = 0
    min_height: _Number = 0
    max_width: _Number = 0
    max_height: _Number = 0
    width_percent: _Number = None
    height_percent: _Number = None
    # flags
    visible: bool = True
    active: bool = True
    # events
    on_hover: typing.Callable[[typing.Any], None] = None
    on_click: typing.Callable[[typing.Any], None] = None
    on_release: typing.Callable[[typing.Any], None] = None
    on_pressed: typing.Callable[[typing.Any], None] = None
    on_select: typing.Callable[[typing.Any], None] = None
    on_deselect: typing.Callable[[typing.Any], None] = None
    # event flags
    can_hover: bool = True
    can_press: bool = True
    can_select: bool = False
    show_press: bool = True
    show_hover: bool = True
    # scrolling
    can_scroll_h: bool = False
    can_scroll_v: bool = False
    scroll_offset: pygame.Vector2 = None


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
        "font_size": "The size of the font for the text",
        "font_name": "The file name or the font. None is allowed",
        "sysfont_name": "If it's not None, it overrides font_name and calls pygame.font.SysFont instead",
        "font_antialas": "Antialas flag for text rendering",
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
    }
}


class _Status:
    hovering: bool = False
    pressing: bool = False
    selected: bool = False
    _clicked = False
    _released = False
    _started_pressing = False

    def check_click(self) -> bool:
        return self._clicked

    def check_release(self) -> bool:
        return self._released

    def select(self):
        self.selected = True

    def deselect(self):
        self.selected = False

    def toggle_selection(self):
        self.selected = not self.selected

    def _update(self, element: "_Element"):
        self._clicked = False
        self._released = False
        any_other = False
        for el in _UIManager.top_elements:
            if not el is element and not el is element._parent and el.settings.visible and \
                el.settings.active and el._rect.collidepoint(_UIManager.mouse_pos)and el._tree_element._tree_index == element._tree_element._tree_index:
                any_other = True
        for el in _UIManager.tree_elements:
            if el._tree_index > element._tree_element._tree_index:
                if el.settings.active and el.settings.visible and el._rect.collidepoint(_UIManager.mouse_pos):
                    any_other = True
        was_hovering = self.hovering
        self.hovering = element._rect.collidepoint(
            _UIManager.mouse_pos) and element.settings.can_hover and \
            not any_other and (
                not element.parent or element.parent._rect.collidepoint(_UIManager.mouse_pos)) \
            and (not element.parent or (element.parent.settings.active and element.parent.settings.visible))
        if self.hovering and element.settings.on_hover:
            element.settings.on_hover(element)

        was_pressing = self.pressing
        self.pressing = (
            self.hovering or self._started_pressing) and _UIManager.mouse_buttons[0] and element.settings.can_press
        if not was_hovering and _UIManager.was_clicking and not self._started_pressing:
            self.pressing = False
            self.hovering = False
        if self.pressing and element.settings.on_pressed:
            element.settings.on_pressed(element)

        if was_pressing and not self.pressing:
            self._started_pressing = False
            self._released = True
            if element.settings.on_release:
                element.settings.on_release(element)

        if not was_pressing and self.pressing:
            self._started_pressing = True
            self._clicked = True
            if element.settings.on_click:
                element.settings.on_click(element)
            if element.settings.can_select and not self.selected:
                self.selected = True
                if element.settings.on_select:
                    element.settings.on_select(element)
            elif element.settings.can_select and self.selected:
                self.selected = False
                if element.settings.on_deselect:
                    element.settings.on_deselect(element)


class _Element:
    def __init__(self, **kwargs):
        self._children: list["_Element"] = []
        self._parent: "_Element" = None
        self.settings: _Settings = _Settings()
        self.settings.offset, self.settings.scroll_offset = pygame.Vector2(), pygame.Vector2()
        self.status: _Status = _Status()
        self._topleft = pygame.Vector2()
        self._rect = pygame.Rect(
            self._topleft, (self.settings.width, self.settings.height))
        self._surface = pygame.Surface((1, 1), pygame.SRCALPHA)
        self._tree_index = -1
        if _UIManager.last_element:
            _UIManager.last_element._add_to_queue(self)
            self._parent = _UIManager.last_element
            self._tree_element = self._parent._get_tree()
        else:
            _UIManager.last_element = self
            self._tree_index = len(_UIManager.tree_elements)
            _UIManager.tree_elements.append(self)
            self._tree_element = self

        self._on_init()
        self.set(**kwargs)

    def _get_tree(self):
        if self in _UIManager.tree_elements:
            return self
        elif self.parent:
            return self.parent._get_tree()

    def _on_init(self): ...
    def _on_set(self, **kwargs): ...
    def _on_enter(self): ...
    def _on_exit(self): ...
    def _on_draw(self): ...

    def _update(self):
        self._pre_update()
        self._post_update()

    def _set_w(self, w):
        if self.settings.width == w:
            return
        self.settings.width = pygame.math.clamp(
            w, self.settings.min_width, self.settings.max_width if self.settings.max_width != 0 else float("inf"))

    def _set_h(self, h):
        if self.settings.height == h:
            return
        self.settings.height = pygame.math.clamp(
            h, self.settings.min_height, self.settings.max_height if self.settings.max_height != 0 else float("inf"))

    def set(self, **kwargs: dict[str, typing.Any]) -> typing.Self:
        for name, val in kwargs.items():
            if hasattr(self.settings, name):
                setattr(self.settings, name, val)

        if "min_max_size" in kwargs:
            self.settings.width = self.settings.min_width = self.settings.max_width = kwargs[
                "min_max_size"][0]
            self.settings.height = self.settings.min_height = self.settings.max_height = kwargs[
                "min_max_size"][1]
        if "min_size" in kwargs:
            self.settings.min_width = kwargs["min_size"][0]
            self.settings.min_height = kwargs["min_size"][1]
        if "max_size" in kwargs:
            self.settings.max_width = kwargs["max_size"][0]
            self.settings.max_height = kwargs["max_size"][1]
        if "size" in kwargs:
            print(kwargs["size"])
            self.settings.width = kwargs["size"][0]
            self.settings.height = kwargs["size"][1]
        if "min_max_width" in kwargs:
            self.settings.width = self.settings.max_width = self.settings.min_width = kwargs[
                "min_max_width"]
        if "min_max_height" in kwargs:
            self.settings.height = self.settings.max_height = self.settings.min_height = kwargs[
                "min_max_height"]
        if "font_size" in kwargs or "font_name" in kwargs:
            func = pygame.font.SysFont if self.settings.sysfont_name else pygame.font.Font
            font_name = self.settings.sysfont_name if self.settings.sysfont_name else self.settings.font_name
            self.settings.font = func(font_name, self.settings.font_size)
        if "draw_top" in kwargs:
            if self.settings.draw_top:
                if self not in _UIManager.top_elements:
                    _UIManager.top_elements.append(self)
            if not self.settings.draw_top:
                if self in _UIManager.top_elements:
                    _UIManager.top_elements.remove(self)

        self._on_set(**kwargs)
        return self

    def _add_child(self, child):
        self._children.append(child)

    def _add_to_queue(self, child):
        self._children_queue.append(child)

    def __enter__(self):
        self._children_queue: list["_Element"] = []
        _UIManager.last_element = self
        self._on_enter()
        return self

    def __exit__(self, exc_type=None, exc_val=None, exc_tb=None):
        _UIManager.last_element = self._parent
        for child in self._children_queue:
            self._add_child(child)
        self._on_exit()
        del self._children_queue

    def _pre_update(self):
        if self.settings.free_position:
            self._topleft = self.settings.free_position
        if self.settings.ignore_scroll:
            self.settings.offset = -self._parent.settings.scroll_offset
        self._rect.topleft = self._real_topleft
        if self.settings.width_percent and self.parent:
            self.settings.width = (
                (self.parent.settings.width-self.settings.margin*2-self.parent._scroll_margin_h)*self.settings.width_percent)/100
        if self.settings.height_percent and self.parent:
            self.settings.height = (
                (self.parent.settings.height-self.settings.margin*2-self.parent._scroll_margin_v)*self.settings.height_percent)/100
        self._rect.w = self.settings.width
        self._rect.h = self.settings.height
        if self.settings.active:
            self.status._update(self)
        if self._surface.get_width() != int(self.settings.width) or self._surface.get_height() != int(self.settings.height):
            self._surface = pygame.Surface(
                (int(self.settings.width), int(self.settings.height)), pygame.SRCALPHA)

    def _post_update(self):
        if not self.settings.active:
            return
        for child in self._children:
            child._update()

    def _draw(self, surface: pygame.Surface):
        if not self.settings.visible:
            return
        self._surface.fill(0)
        if self.settings.has_background:
            bg_col = self.settings.click_color if (self.status.pressing or self.status.selected) and self.settings.show_press else \
                self.settings.hover_color if self.status.hovering and self.settings.show_hover else \
                self.settings.dark_bg_color if self.settings.has_dark_bg else \
                self.settings.background_color
            pygame.draw.rect(self._surface, bg_col, ((
                0, 0), self._rect.size), border_radius=self.settings.border_radius)
        self._on_draw()
        for child in self._children:
            if not child.settings.draw_top:
                child._draw(self._surface)
        if self.settings.has_outline:
            pygame.draw.rect(self._surface, self.settings.outline_color,
                             ((0, 0), self._rect.size),
                             self.settings.outline_width,
                             self.settings.border_radius)
        surface.blit(self._surface, (self._topleft +
                                     self.settings.offset -
                                     ((self._parent.settings.scroll_offset if not self.settings.ignore_scroll else -self._parent.settings.scroll_offset)
                                      if self._parent else pygame.Vector2()))
                     if not self.settings.draw_top else self._real_topleft)

    def _kill(self):
        if self._parent:
            self._parent._remove_child(self)
        if self in _UIManager.top_elements:
            _UIManager.top_elements.remove(self)
        if self in _UIManager.tree_elements:
            _UIManager.tree_elements.remove(self)
        for child in self.children:
            child._kill()
        del self

    def _remove_child(self, child):
        if child in self._children:
            self._children.remove(child)

    @property
    def _real_topleft(self):
        return (self._topleft +
                self.settings.offset +
                (self._parent._real_topleft if self._parent else pygame.Vector2()) -
                ((self._parent.settings.scroll_offset if not self.settings.ignore_scroll else -self._parent.settings.scroll_offset)
                    if self._parent else pygame.Vector2()))

    def show(self):
        self.settings.visible = True

    def hide(self):
        self.settings.visible = False

    def activate(self):
        self.settings.active = True

    def deactivate(self):
        self.settings.active = False

    def point_hovering(self, point: _Coordinate) -> bool:
        return self._rect.collidepoint(point)

    @property
    def parent(self) -> "_Element":
        return self._parent

    @property
    def children(self) -> list["_Element"]:
        return self._children


_SCROLLBAR_SIZE = 15
_SLIDER_SIZE = 15
_HANDLE_SIZE = 25


class _VScrollbar(_Element):
    def _on_init(self):
        self.set(can_press=False, can_hover=False, has_dark_bg=True, width=_SCROLLBAR_SIZE,
                 min_width=_SCROLLBAR_SIZE, max_width=_SCROLLBAR_SIZE, ignore_scroll=True, draw_top=True)
        _UIManager.last_element = self
        self._children_queue = []
        self.handle: _Element = _Element()
        self._children.append(self.handle)
        self.handle.set(width=_SCROLLBAR_SIZE, min_width=_SCROLLBAR_SIZE,
                        max_width=_SCROLLBAR_SIZE, ignore_scroll=True)
        self.handle_pos = 0
        _UIManager.last_element = self._parent
        del self._children_queue

    def _update(self):
        if not self._parent.settings.can_scroll_v or self._parent.settings.height >= self._parent._tot_h:
            self.settings.active = False
            self.settings.visible = False
            return
        self.settings.height = self.settings.max_height = self.settings.min_height = self._parent.settings.height
        self.settings.free_position = pygame.Vector2(
            self._parent.settings.width-self.settings.width, 0)

        self._pre_update()

        self.handle_size = (self.settings.height *
                            self._parent.settings.height)/self._parent._tot_h
        scroll_v = (self.handle_pos*self._parent._tot_h)/self.settings.height
        self.handle.settings.free_position = pygame.Vector2(0, self.handle_pos)
        self.handle.settings.height = self.handle.settings.min_height = self.handle.settings.max_height = self.handle_size
        self._parent.settings.scroll_offset.y = scroll_v

        self._post_update()

        # print(self.parent.__class__.__name__)

        if self.handle.status.pressing:
            self.handle_pos += _UIManager.mouse_rel[1]
            if self.handle_pos < 0:
                self.handle_pos = 0
            if self.handle_pos > self.settings.height-self.handle_size:
                self.handle_pos = self.settings.height-self.handle_size
            self.handle.settings.free_position = pygame.Vector2(
                0, self.handle_pos)


class _HScrollbar(_Element):
    def _on_init(self):
        self.set(can_press=False, can_hover=False, has_dark_bg=True, height=_SCROLLBAR_SIZE,
                 min_height=_SCROLLBAR_SIZE, max_height=_SCROLLBAR_SIZE, ignore_scroll=True, draw_top=True)
        _UIManager.last_element = self
        self._children_queue = []
        self.handle = _Element()
        self._children.append(self.handle)
        self.handle.set(height=_SCROLLBAR_SIZE, min_height=_SCROLLBAR_SIZE,
                        max_height=_SCROLLBAR_SIZE, ignore_scroll=True)
        self.handle_pos = 0
        _UIManager.last_element = self._parent
        del self._children_queue

    def _update(self):
        if not self._parent.settings.can_scroll_h or self._parent.settings.width >= self._parent._tot_w:
            self.settings.active = False
            self.settings.visible = False
        self.settings.width = self.settings.max_width = self.settings.min_width = self._parent.settings.width
        self.settings.free_position = pygame.Vector2(
            0, self._parent.settings.height-self.settings.height)

        self._pre_update()

        self.handle_size = (self.settings.width *
                            self._parent.settings.width)/self._parent._tot_w
        scroll_v = (self.handle_pos*self._parent._tot_w)/self.settings.width
        self.handle.settings.free_position = pygame.Vector2(self.handle_pos, 0)
        self.handle.settings.width = self.handle.settings.min_width = self.handle.settings.max_width = self.handle_size
        self._parent.settings.scroll_offset.x = scroll_v

        self._post_update()

        if self.handle.status.pressing:
            self.handle_pos += _UIManager.mouse_rel[0]
            if self.handle_pos < 0:
                self.handle_pos = 0
            if self.handle_pos > self.settings.width-self.handle_size:
                self.handle_pos = self.settings.width-self.handle_size
            self.handle.settings.free_position = pygame.Vector2(
                self.handle_pos, 0)


def _anchor_inner(anchor, parent, inner, padding):
    if anchor in ["left", "right", "top", "bottom"]:
        raise _WithUIException(
            f"Invalid anchor '{anchor}'. Only corners and mid-edges are supported.")
    ppos = getattr(parent, anchor)
    setattr(inner, anchor, (
        ppos[0]+padding if "left" in anchor else ppos[0] -
            padding if "right" in anchor else ppos[0],
            ppos[1]+padding if "top" in anchor else ppos[1] -
            padding if "bottom" in anchor else ppos[1]
            ))
