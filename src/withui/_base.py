import pygame
import typing

from ._constants import _ColorValue, _Coordinate, _Number, _FONT_ALIGN_LOOKUP

pygame.init()


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
    text_align: str = "center"
    # size
    auto_resize_h: bool = True
    auto_resize_v: bool = True
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

    def __init__(self):
        for attr, value in vars(_Settings).items():
            if attr.startswith("__") and attr.endswith("__"):
                continue
            if not hasattr(self, attr):
                continue
            setattr(self, attr, value)
            self.font.align = pygame.FONT_CENTER


_Settings.font.align = pygame.FONT_CENTER


class _Status:
    def __init__(self):
        self.hovering: bool = False
        self.pressing: bool = False
        self.selected: bool = False
        self._hovering = False
        self._clicked = False
        self._released = False
        self._started_pressing = False

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
                    el.settings.active and el._rect.collidepoint(_UIManager.mouse_pos) and el._tree_element._tree_index == element._tree_element._tree_index:
                any_other = True
        for el in _UIManager.tree_elements:
            if el._tree_index > element._tree_element._tree_index:
                if el.settings.active and el.settings.visible and el._rect.collidepoint(_UIManager.mouse_pos):
                    any_other = True
        if element._is_cont:
            for child in element._children:
                if child._is_cont and child.status._hovering:
                    any_other = True
        was_hovering = self.hovering
        self._hovering = element._rect.collidepoint(
            _UIManager.mouse_pos) and \
            not any_other and (
                not element.parent or element.parent._rect.collidepoint(_UIManager.mouse_pos)) \
            and (not element.parent or (element.parent.settings.active and element.parent.settings.visible))
        self.hovering = self._hovering and element.settings.can_hover
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
        self._is_cont = False
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
    def _on_font_change(self): ...

    def _update(self):
        self._pre_update()
        self._post_update()

    def _set_w(self, w):
        if self.settings.width == w or not self.settings.auto_resize_h:
            return
        self.settings.width = pygame.math.clamp(
            w, self.settings.min_width, self.settings.max_width if self.settings.max_width != 0 else float("inf"))

    def _set_h(self, h):
        if self.settings.height == h or not self.settings.auto_resize_v:
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
            self._on_font_change()
        if "text_align" in kwargs:
            if isinstance(kwargs["text_align"], int):
                self.settings.font.align = kwargs["text_align"]
            else:
                if kwargs["text_align"] in ["center", "left", "right"]:
                    self.settings.font.align = _FONT_ALIGN_LOOKUP[kwargs["text_align"]]
                else:
                    raise _WithUIException(
                        f"Text alignment can only be left, right or center, not '{kwargs['text_align']}'")
            self._on_font_change()
        if "text_color" in kwargs:
            self._on_font_change()
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
                (self.parent.settings.width-(self.settings.margin*2+(self.settings.margin*(len(self._parent._children)-2) if
                                                                     self._parent._h_cont else 0))-self.parent._scroll_margin_h) *
                self.settings.width_percent)/100
        if self.settings.height_percent and self.parent:
            self.settings.height = (
                (self.parent.settings.height-(self.settings.margin*2+(self.settings.margin*(len(self._parent._children)-2) if
                                                                      self._parent._v_cont else 0))-self.parent._scroll_margin_v) *
                self.settings.height_percent)/100
        self._rect.w = self.settings.width
        self._rect.h = self.settings.height
        if self.settings.active:
            self.status._update(self)
        if self._surface.get_width() != int(self.settings.width) or self._surface.get_height() != int(self.settings.height):
            self._surface = pygame.Surface(
                (max(int(self.settings.width), 1), max(int(self.settings.height), 1)), pygame.SRCALPHA)
            self._on_font_change()

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

    def is_tree(self) -> bool:
        return self in _UIManager.tree_elements

    @property
    def parent(self) -> "_Element":
        return self._parent

    @property
    def children(self) -> list["_Element"]:
        return self._children


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
