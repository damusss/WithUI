import pygame
import typing

from ._constants import _ColorValue, _Coordinate, _FONT_ALIGN_LOOKUP, _ZERO_VEC

pygame.init()


class _WithUIException(Exception):
    ...


class _UIManager:
    last_element: "_Element" = None
    root_elements: list["_Element"] = []
    top_elements: list["_Element"] = []
    mouse_buttons = None
    mouse_pos = (0, 0)
    mouse_rel = (0, 0)
    keys = None
    was_clicking = False
    was_right = False
    frame_events: list[pygame.event.Event] = []
    frame_ended = False
    ticks = 0
    all_elements: list["_Element"] = []
    navigating: bool = False
    tabbed_element: "_Element" = None
    navigation_enabled: bool = True
    space_pressed: bool = False
    hover_sound: pygame.mixer.Sound | None = None
    click_sound: pygame.mixer.Sound | None = None

    @classmethod
    def update(cls):
        cls.space_pressed = False
        if cls.mouse_buttons:
            cls.was_clicking = cls.mouse_buttons[0]
            cls.was_right = cls.mouse_buttons[2]
        cls.mouse_buttons = pygame.mouse.get_pressed()
        cls.mouse_pos = pygame.mouse.get_pos()
        cls.mouse_rel = pygame.mouse.get_rel()
        cls.keys = pygame.key.get_pressed()
        cls.ticks = pygame.time.get_ticks()

        for event in cls.frame_events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    cls.navigating = False
                    if cls.tabbed_element:
                        cls.tabbed_element._set_dirty()
                    cls.tabbed_element = None
                elif event.key == pygame.K_UP:
                    if cls.navigating and cls.tabbed_element is not None and cls.tabbed_element.parent is not None:
                        if cls.tabbed_element:
                            cls.tabbed_element._set_dirty()
                        cls.tabbed_element = cls.tabbed_element.parent
                        if cls.tabbed_element:
                            cls.tabbed_element._set_dirty()
                elif event.key == pygame.K_RETURN:
                    if cls.navigating and cls.tabbed_element is not None and len(cls.tabbed_element._children) > 0:
                        if cls.tabbed_element:
                            cls.tabbed_element._set_dirty()
                        cls.tabbed_element = cls.tabbed_element._children[0]
                        if cls.tabbed_element:
                            cls.tabbed_element._set_dirty()
                        if not cls.tabbed_element.settings.active or not cls.tabbed_element.settings.visible or not cls.tabbed_element.settings.can_navigate:
                            cls.tab(1)
                elif event.key == pygame.K_TAB:
                    if cls.keys[pygame.K_LSHIFT]:
                        if cls.navigating and cls.tabbed_element is not None:
                            cls.tab(-1)
                    else:
                        if not cls.navigating and len(cls.root_elements) > 0 and cls.navigation_enabled:
                            cls.navigating = True
                            if cls.tabbed_element:
                                cls.tabbed_element._set_dirty()
                            cls.tabbed_element = cls.root_elements[0]
                            if cls.tabbed_element:
                                cls.tabbed_element._set_dirty()
                            if not cls.tabbed_element.settings.active or not cls.tabbed_element.settings.visible or not cls.tabbed_element.settings.can_navigate:
                                cls.tab(1)
                        else:
                            if cls.navigating and cls.tabbed_element is not None:
                                cls.tab(1)

        if cls.keys[pygame.K_SPACE]:
            if cls.navigating and cls.tabbed_element is not None:
                cls.space_pressed = True

    @classmethod
    def tab(cls, increment):
        if cls.tabbed_element._parent is not None:
            try:
                cur_index = cls.tabbed_element._parent._children.index(
                    cls.tabbed_element)
            except ValueError:
                cls.navigating = False
                if cls.tabbed_element:
                    cls.tabbed_element._set_dirty()
                cls.tabbed_element = None
            else:
                cur_index += increment
                if (cur_index < len(cls.tabbed_element._parent._children) and increment > 0) or (cur_index >= 0 and increment < 0):
                    if cls.tabbed_element:
                        cls.tabbed_element._set_dirty()
                    cls.tabbed_element = cls.tabbed_element._parent._children[cur_index]
                    if cls.tabbed_element:
                        cls.tabbed_element._set_dirty()
                    if not cls.tabbed_element.settings.active or not cls.tabbed_element.settings.visible or not cls.tabbed_element.settings.can_navigate:
                        cls.tab(increment)
                else:
                    if len(cls.tabbed_element._parent._children) > 0:
                        if increment > 0:
                            if cls.tabbed_element:
                                cls.tabbed_element._set_dirty()
                            cls.tabbed_element = cls.tabbed_element._parent._children[0]
                            if cls.tabbed_element:
                                cls.tabbed_element._set_dirty()
                            if not cls.tabbed_element.settings.active or not cls.tabbed_element.settings.visible or not cls.tabbed_element.settings.can_navigate:
                                cls.tab(increment)
                        else:
                            if cls.tabbed_element:
                                cls.tabbed_element._set_dirty()
                            cls.tabbed_element = cls.tabbed_element._parent._children[-1]
                            if cls.tabbed_element:
                                cls.tabbed_element._set_dirty()
                            if not cls.tabbed_element.settings.active or not cls.tabbed_element.settings.visible or not cls.tabbed_element.settings.can_navigate:
                                cls.tab(increment)
        else:
            try:
                cur_index = cls.root_elements.index(cls.tabbed_element)
            except ValueError:
                cls.navigating = False
                if cls.tabbed_element:
                    cls.tabbed_element._set_dirty()
                cls.tabbed_element = None
            else:
                cur_index += increment
                if (cur_index < len(cls.root_elements) and increment > 0) or (cur_index >= 0 and increment < 0):
                    if cls.tabbed_element:
                        cls.tabbed_element._set_dirty()
                    cls.tabbed_element = cls.root_elements[cur_index]
                    if cls.tabbed_element:
                        cls.tabbed_element._set_dirty()
                    if not cls.tabbed_element.settings.active or not cls.tabbed_element.settings.visible or not cls.tabbed_element.settings.can_navigate:
                        cls.tab(increment)
                else:
                    if len(cls.root_elements) > 0:
                        if increment > 0:
                            if cls.tabbed_element:
                                cls.tabbed_element._set_dirty()
                            cls.tabbed_element = cls.root_elements[0]
                            if cls.tabbed_element:
                                cls.tabbed_element._set_dirty()
                            if not cls.tabbed_element.settings.active or not cls.tabbed_element.settings.visible or not cls.tabbed_element.settings.can_navigate:
                                cls.tab(increment)
                        else:
                            if cls.tabbed_element:
                                cls.tabbed_element._set_dirty()
                            cls.tabbed_element = cls.root_elements[-1]
                            if cls.tabbed_element:
                                cls.tabbed_element._set_dirty()
                            if not cls.tabbed_element.settings.active or not cls.tabbed_element.settings.visible or not cls.tabbed_element.settings.can_navigate:
                                cls.tab(increment)


class _Settings:
    # positioning
    offset: pygame.Vector2 = None
    margin: float = 5
    center_elements: bool = False
    free_position: pygame.Vector2 | None = None
    draw_top: bool = False
    ignore_scroll: bool = False
    parent_anchor: str | None = None
    # style
    border_radius: float = 4
    outline_width: float = 1
    padding: float = 3
    # style color
    background_color: _ColorValue = (30, 30, 30)
    dark_bg_color: _ColorValue = (15, 15, 15)
    hover_color: _ColorValue = (40, 40, 40)
    click_color: _ColorValue = (22, 22, 22)
    outline_color: _ColorValue = (50, 50, 50)
    text_color: _ColorValue = (255, 255, 255)
    inner_color: _ColorValue = (0, 100, 200)
    # style image
    background_image: pygame.Surface | None = None
    background_anchor: str = "center"
    background_padding: float = 0
    resize_background: bool = False
    adapt_to_bg: bool = False
    bg_effect_alpha: int = 255
    bg_hover_flag: int = pygame.BLEND_RGB_ADD
    bg_press_flag: int = pygame.BLEND_RGB_SUB
    # style flags
    has_background: bool = True
    has_outline: bool = True
    has_dark_bg: bool = False
    # text
    font_size: int = 20
    font_name: str | None = None
    sysfont_name: str | None = "NotoSans"
    font_antialas: bool = True
    font: pygame.font.Font = pygame.font.SysFont(sysfont_name, font_size)
    text_align: str | int = pygame.FONT_CENTER
    # size
    auto_resize_h: bool = True
    auto_resize_v: bool = True
    width: float = 0
    height: float = 0
    min_width: float = 0
    min_height: float = 0
    max_width: float = 0
    max_height: float = 0
    width_percent: float | None = None
    height_percent: float | None = None
    # flags
    visible: bool = True
    active: bool = True
    # events
    on_hover: typing.Callable[[typing.Any], None] | None = None
    on_click: typing.Callable[[typing.Any], None] | None = None
    on_release: typing.Callable[[typing.Any], None] | None = None
    on_pressed: typing.Callable[[typing.Any], None] | None = None
    on_select: typing.Callable[[typing.Any], None] | None = None
    on_deselect: typing.Callable[[typing.Any], None] | None = None
    on_mouse_enter: typing.Callable[[typing.Any], None] | None = None
    on_mouse_exit: typing.Callable[[typing.Any], None] | None = None
    on_right_click: typing.Callable[[typing.Any], None] | None = None
    on_right_release: typing.Callable[[typing.Any], None] | None = None
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
    # navigation
    navigation_color: _ColorValue = "red"
    navigation_size: float = 2
    can_navigate: bool = True

    def __init__(self):
        for attr, value in vars(_Settings).items():
            if attr.startswith("__") and attr.endswith("__"):
                continue
            if not hasattr(self, attr):
                continue
            setattr(self, attr, value)
        self.font = pygame.font.Font = pygame.font.SysFont(
            self.sysfont_name, self.font_size)
        self.font.align = pygame.FONT_CENTER


_Settings.font.align = pygame.FONT_CENTER


class _Status:
    def __init__(self, element):
        self.hovering: bool = False
        self.pressing: bool = False
        self.selected: bool = False
        self.right_pressing: bool = False
        self._hovering = False
        self._clicked = False
        self._right_clicked = False
        self._right_released = False
        self._released = False
        self._started_pressing = False
        self._started_right = False
        self._absolute_hover = False
        self._element = element

    def check_click(self) -> bool:
        return self._clicked

    def check_right_click(self) -> bool:
        return self._right_clicked

    def check_release(self) -> bool:
        return self._released

    def check_right_release(self) -> bool:
        return self._right_released

    def select(self):
        self._element._set_dirty()
        self.selected = True

    def deselect(self):
        self._element._set_dirty()
        self.selected = False

    def toggle_selection(self):
        self._element._set_dirty()
        self.selected = not self.selected

    def _any_child_hover(self, any_other_child, element: "_Element"):
        if element._is_cont:
            for child in element._children:
                if child._is_cont and child.status._hovering and (child._v_scrollbar.settings.visible or child._h_scrollbar.settings.visible):
                    return True
                elif child._is_cont:
                    any_other_child = self._any_child_hover(
                        any_other_child, child)
        return any_other_child

    def _update(self, element: "_Element"):
        self._clicked = self._released = self._right_clicked = self._right_released = False
        any_other = False
        for el in _UIManager.top_elements:
            if not el is element and not el is element._parent and el.settings.visible and \
                    el.settings.active and el._rect.collidepoint(_UIManager.mouse_pos) and el._root_element._root_index == element._root_element._root_index:
                any_other = True
        for el in _UIManager.root_elements:
            if el._root_index > element._root_element._root_index:
                if el.settings.active and el.settings.visible and el._rect.collidepoint(_UIManager.mouse_pos):
                    any_other = True
        any_other_child = self._any_child_hover(False, element)
        was_hovering = self.hovering
        self._absolute_hover = element._rect.collidepoint(
            _UIManager.mouse_pos) and \
            not any_other and (
                not element.parent or element.parent._rect.collidepoint(_UIManager.mouse_pos)) \
            and (not element.parent or (element.parent.settings.active and element.parent.settings.visible))
        self._hovering = self._absolute_hover and not any_other_child
        self.hovering = self._hovering and element.settings.can_hover
        if self.hovering and element.settings.on_hover:
            element.settings.on_hover(element)

        was_pressing = self.pressing
        self.pressing = (((
            self.hovering or self._started_pressing) and _UIManager.mouse_buttons[0]) or
            element is _UIManager.tabbed_element and _UIManager.space_pressed) and element.settings.can_press

        was_right = self.right_pressing
        self.right_pressing = (self.hovering or self._started_right) and _UIManager.mouse_buttons[
            2] and element.settings.can_press

        if not was_hovering and _UIManager.was_right and not self._started_right:
            self.right_pressing = False
            self.hovering = False
            self._hovering = False

        if not was_right and self.right_pressing:
            self._right_clicked = True
            self._started_right = True
            if element.settings.on_right_click:
                element.settings.on_right_click(element)

        if was_right and not self.right_pressing:
            self._right_released = True
            self._started_right = False
            if element.settings.on_right_release:
                element.settings.on_right_release(element)

        if not was_hovering and _UIManager.was_clicking and not self._started_pressing:
            self.pressing = False
            self.hovering = False
            self._hovering = False

        if self.hovering and not was_hovering:
            element._set_dirty()
            if element.settings.on_mouse_enter:
                element.settings.on_mouse_enter(element)
            if _UIManager.hover_sound is not None:
                _UIManager.hover_sound.play()

        if not self.hovering and was_hovering:
            element._set_dirty()
            if element.settings.on_mouse_exit:
                element.settings.on_mouse_exit(element)

        if self.pressing and element.settings.on_pressed:
            element.settings.on_pressed(element)

        if was_pressing and not self.pressing:
            element._set_dirty()
            self._started_pressing = False
            self._released = True
            if element.settings.on_release:
                element.settings.on_release(element)

        if not was_pressing and self.pressing:
            element._set_dirty()
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
            if _UIManager.click_sound is not None:
                _UIManager.click_sound.play()


class _Element:
    def __init__(self, **kwargs):
        self._children: list["_Element"] = []
        self._parent: "_Element" | None = None
        self.settings: _Settings = _Settings()
        self.settings.offset, self.settings.scroll_offset = pygame.Vector2(), pygame.Vector2()
        self.status: _Status = _Status(self)
        self._topleft = pygame.Vector2()
        self._rect = pygame.Rect(
            self._topleft, (self.settings.width, self.settings.height))
        self._rel_rect = self._rect.copy()
        self._bg_image: pygame.Surface | None = None
        self._bg_rect: pygame.Rect | None = None
        self._surface = pygame.Surface((1, 1), pygame.SRCALPHA)
        self._root_index = -1
        self._is_cont = False
        self._always_top = False
        self._dirty = True
        if _UIManager.last_element:
            _UIManager.last_element._add_to_queue(self)
            self._parent = _UIManager.last_element
            self._root_element = self._parent._get_root()
        else:
            _UIManager.last_element = self
            self._root_index = len(_UIManager.root_elements)
            _UIManager.root_elements.append(self)
            self._root_element = self
        _UIManager.all_elements.append(self)

        self._on_init()
        self.set(**kwargs)

    def _get_root(self):
        if self in _UIManager.root_elements:
            return self
        elif self.parent:
            return self.parent._get_root()

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
        self._set_dirty()
        self.settings.width = pygame.math.clamp(
            w, self.settings.min_width, self.settings.max_width if self.settings.max_width != 0 else float("inf"))

    def _set_h(self, h):
        if self.settings.height == h or not self.settings.auto_resize_v:
            return
        self._set_dirty()
        self.settings.height = pygame.math.clamp(
            h, self.settings.min_height, self.settings.max_height if self.settings.max_height != 0 else float("inf"))

    def _set_dirty(self):
        if not self._dirty and self.settings.visible:
            self._dirty = True
            if self._parent:
                self._parent._set_dirty()

    def _raycast(self, pos, draw_top=False):
        if (self.settings.draw_top and not draw_top) or not self.settings.visible or not self.settings.active:
            return None
        for child in self._children:
            if (result := child._raycast(pos)):
                return result
        if self._rect.collidepoint(pos):
            return self
        return None

    def set(self, **kwargs: dict[str, typing.Any]) -> typing.Self:
        for name, val in kwargs.items():
            if hasattr(self.settings, name):
                setattr(self.settings, name, val)

        if "min_max_size" in kwargs:
            self.settings.width = self.settings.min_width = self.settings.max_width = int(kwargs[
                "min_max_size"][0])
            self.settings.height = self.settings.min_height = self.settings.max_height = int(kwargs[
                "min_max_size"][1])
        if "min_size" in kwargs:
            self.settings.min_width = int(kwargs["min_size"][0])
            self.settings.min_height = int(kwargs["min_size"][1])
        if "max_size" in kwargs:
            self.settings.max_width = int(kwargs["max_size"][0])
            self.settings.max_height = int(kwargs["max_size"][1])
        if "size" in kwargs:
            self.settings.width = int(kwargs["size"][0])
            self.settings.height = int(kwargs["size"][1])
        if "min_max_width" in kwargs:
            self.settings.width = self.settings.max_width = self.settings.min_width = int(kwargs[
                "min_max_width"])
        if "min_max_height" in kwargs:
            self.settings.height = self.settings.max_height = self.settings.min_height = int(kwargs[
                "min_max_height"])
        if "text_align" in kwargs:
            if isinstance(kwargs["text_align"], int):
                self.settings.font.align = kwargs["text_align"]
            else:
                if kwargs["text_align"] in ["center", "left", "right"]:
                    self.settings.text_align = _FONT_ALIGN_LOOKUP[kwargs["text_align"]]
                    self.settings.font.align = self.settings.text_align
                else:
                    raise _WithUIException(
                        f"Text alignment can only be left, right or center, not '{kwargs['text_align']}'")
            self._on_font_change()
        if "font_size" in kwargs or "font_name" in kwargs:
            func = pygame.font.SysFont if self.settings.sysfont_name else pygame.font.Font
            font_name = self.settings.sysfont_name if self.settings.sysfont_name else self.settings.font_name
            self.settings.font = func(font_name, self.settings.font_size)
            self.settings.font.align = self.settings.text_align
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
        if "background_image" in kwargs:
            self._bg_image = kwargs["background_image"]
            if self._bg_image:
                self._bg_rect = self._bg_image.get_rect()
                _anchor_inner(self.settings.background_anchor, self._rel_rect,
                              self._bg_rect, self.settings.background_padding)
                self._bg_rect.topleft -= self._topleft+self.settings.offset
        if "on_toggle" in kwargs:
            self.settings.on_select = self.settings.on_deselect = kwargs["on_toggle"]

        self._set_dirty()
        self._on_set(**kwargs)
        return self

    def _add_child(self, child):
        self._children.append(child)
        self._set_dirty()

    def _add_to_queue(self, child):
        self._children_queue.append(child)

    def __enter__(self):
        self._children_queue: list["_Element"] = []
        self._previous_last = _UIManager.last_element if self._parent else None
        _UIManager.last_element = self
        self._on_enter()
        return self

    def __exit__(self, exc_type=None, exc_val=None, exc_tb=None):
        _UIManager.last_element = self._previous_last
        for child in self._children_queue:
            self._add_child(child)
        self._on_exit()
        del self._children_queue

    def _pre_update(self):
        if self.settings.free_position:
            self._topleft = self.settings.free_position
        self._rect.topleft = self._real_topleft
        self._rel_rect.topleft = self._topleft+self.settings.offset
        if self.settings.width_percent and self.parent:
            prev = self.settings.width
            self.settings.width = self.settings.min_width = self.settings.max_width = (
                (self.parent.settings.width-(self.settings.margin*2+(self.settings.margin*(len(self._parent._children)-2) if
                                                                     self._parent._h_cont else 0))-self.parent._scroll_margin_h) *
                self.settings.width_percent)/100
            if prev != self.settings.width:
                self._set_dirty()
        if self.settings.height_percent and self.parent:
            prev = self.settings.height
            self.settings.height = self.settings.min_height = self.settings.max_height = (
                (self.parent.settings.height-(self.settings.margin*2+(self.settings.margin*(len(self._parent._children)-2) if
                                                                      self._parent._v_cont else 0))-self.parent._scroll_margin_v) *
                self.settings.height_percent)/100
            if prev != self.settings.height:
                self._set_dirty()
        if self._bg_image:
            if self._bg_image.get_width() != self._bg_rect.w or self._bg_image.get_height() != self._bg_rect.h:
                self._bg_rect = self._bg_image.get_rect()
        if self.settings.resize_background and self.settings.background_image:
            if self._rect.w != (self._bg_rect.w - self.settings.background_padding*2) or self._rect.h != (self._bg_rect.h-self.settings.background_padding*2):
                self._bg_image = pygame.transform.scale(self.settings.background_image, (int(
                    self._rect.w-self.settings.background_padding*2), int(self._rect.h-self.settings.background_padding*2)))
                self._bg_rect.size = (self._rect.w-self.settings.background_padding*2,
                                      self._rect.h-self.settings.background_padding*2)
                self._set_dirty()
        elif self.settings.adapt_to_bg and self._bg_image:
            if self.settings.width != (self._bg_rect.w + self.settings.background_padding*2) or self.settings.height != (self._bg_rect.h + self.settings.background_padding*2):
                self._set_w(
                    (self._bg_rect.w + self.settings.background_padding*2))
                self._set_h(
                    (self._bg_rect.h + self.settings.background_padding*2))
        if self._bg_image:
            pp = self._bg_rect.topleft
            _anchor_inner(self.settings.background_anchor, self._rel_rect,
                          self._bg_rect, self.settings.background_padding)
            self._bg_rect.topleft -= self._topleft+self.settings.offset
            if pp != self._bg_rect.topleft:
                self._set_dirty()
        self._rect.w = self.settings.width
        self._rect.h = self.settings.height
        self._rel_rect.size = self._rect.size
        if self.settings.active:
            self.status._update(self)
        if self._surface.get_width() != int(self.settings.width) or self._surface.get_height() != int(self.settings.height):
            self._surface = pygame.Surface(
                (max(int(self.settings.width), 1), max(int(self.settings.height), 1)), pygame.SRCALPHA)
            self._on_font_change()
            self._set_dirty()

    def _post_update(self):
        if not self.settings.active:
            return
        for child in self._children:
            child._update()

    def _draw(self, surface: pygame.Surface):
        if not self.settings.visible:
            return
        if self._dirty:
            self._surface.fill(0)
        if self.settings.has_background and self._dirty:
            bg_col = self.settings.click_color if (self.status.pressing or self.status.selected) and self.settings.show_press else \
                self.settings.hover_color if self.status.hovering and self.settings.show_hover else \
                self.settings.dark_bg_color if self.settings.has_dark_bg else \
                self.settings.background_color
            pygame.draw.rect(self._surface, bg_col, ((
                0, 0), self._rect.size), border_radius=self.settings.border_radius)
        if self._bg_image and self._dirty:
            fill_col = self.settings.click_color if (self.status.pressing or self.status.selected) and self.settings.show_press else \
                self.settings.hover_color if self.status.hovering and self.settings.show_hover else None
            flag = self.settings.bg_press_flag if (self.status.pressing or self.status.selected) and self.settings.show_press else \
                self.settings.bg_hover_flag if self.status.hovering and self.settings.show_hover else None
            self._surface.blit(self._bg_image, self._bg_rect)
            if fill_col is not None:
                fill_col = (*fill_col, self.settings.bg_effect_alpha)
                self._surface.fill(fill_col, special_flags=flag)
        if self._dirty:
            self._on_draw()
            for child in self._children:
                if not child.settings.draw_top:
                    child._draw(self._surface)
        if self.settings.has_outline and self._dirty:
            pygame.draw.rect(self._surface, self.settings.outline_color,
                             ((0, 0), self._rect.size),
                             self.settings.outline_width,
                             self.settings.border_radius)
        if self is _UIManager.tabbed_element:
            pygame.draw.rect(self._surface, self.settings.navigation_color,
                             ((0, 0), self._rect.size), max(self.settings.navigation_size, 1))
        surface.blit(self._surface, (self._topleft +
                                     self.settings.offset -
                                     ((self._parent.settings.scroll_offset if not self.settings.ignore_scroll else _ZERO_VEC)
                                      if self._parent else _ZERO_VEC))
                     if not self.settings.draw_top else self._real_topleft)
        self._dirty = False

    def _kill(self):
        self._set_dirty()
        if self._parent:
            self._parent._remove_child(self)
        if self in _UIManager.top_elements:
            _UIManager.top_elements.remove(self)
        if self in _UIManager.root_elements:
            _UIManager.root_elements.remove(self)
        if self in _UIManager.all_elements:
            _UIManager.all_elements.remove(self)
        for child in self.children:
            child._kill()
        if self is _UIManager.last_element:
            _UIManager.last_element = self._parent if self._parent else None
        del self

    def _remove_child(self, child):
        self._set_dirty()
        if child in self._children:
            self._children.remove(child)

    @property
    def _real_topleft(self):
        return (self._topleft +
                self.settings.offset +
                (self._parent._real_topleft if self._parent else _ZERO_VEC) -
                ((self._parent.settings.scroll_offset if not self.settings.ignore_scroll else _ZERO_VEC)
                    if self._parent else _ZERO_VEC))

    def move_in_parent(self, places: int = 1) -> bool:
        if not self._parent:
            return False
        if len(self._parent.children) <= 1:
            return False
        try:
            my_idx = prev_idx = self._parent._children.index(self)
        except ValueError:
            return False
        else:
            my_idx += places
            my_idx = pygame.math.clamp(
                my_idx, 0, len(self._parent._children)-1)
            if my_idx == prev_idx:
                return False
            self._parent._children.remove(self)
            self._parent._children.insert(my_idx, self)
            return True

    def show(self):
        self._set_dirty()
        self.settings.visible = True

    def hide(self):
        self._set_dirty()
        self.settings.visible = False

    def activate(self):
        self._set_dirty()
        self.settings.active = True

    def deactivate(self):
        self._set_dirty()
        self.settings.active = False

    def point_hovering(self, point: _Coordinate) -> bool:
        return self._rect.collidepoint(point)

    def is_root(self) -> bool:
        return self in _UIManager.root_elements

    def kill(self):
        self._kill()

    @property
    def parent(self) -> "_Element":
        return self._parent

    @property
    def children(self) -> list["_Element"]:
        return self._children.copy()

    @property
    def absolute_rect(self) -> pygame.Rect:
        return self._rect.copy()

    @property
    def relative_rect(self) -> pygame.Rect:
        return self._rel_rect.copy()

    @property
    def root(self) -> "_Element":
        return self._root_element


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
