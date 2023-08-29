import pygame
pygame.init()


class _WithUIException(Exception):
    ...


class _UIManager:
    last_element: "_Element" = None
    top_element: "_Element" = None
    top_elements: list["_Element"] = []
    mouse_buttons = None
    mouse_pos = None
    mouse_rel = None
    keys = None
    was_clicking = False

    @classmethod
    def update(cls):
        if cls.mouse_buttons:
            cls.was_clicking = cls.mouse_buttons[0]
        cls.mouse_buttons = pygame.mouse.get_pressed()
        cls.mouse_pos = pygame.mouse.get_pos()
        cls.mouse_rel = pygame.mouse.get_rel()
        cls.keys = pygame.key.get_pressed()


class _Settings:
    # positioning
    offset = pygame.Vector2()
    margin = 4
    center_elements = False
    free_position = None
    draw_top = False
    ignore_scroll = False
    # style
    border_radius = 7
    outline_width = 2
    padding = 5
    # style color
    background_color = (30, 30, 30)
    dark_bg_color = (15, 15, 15)
    hover_color = (40, 40, 40)
    click_color = (22, 22, 22)
    outline_color = (50, 50, 50)
    text_color = (255, 255, 255)
    # style flags
    has_background = True
    has_outline = True
    has_dark_bg = False
    # text
    font_size = 22
    font_name = None
    sysfont_name = "Segoe UI"
    font_antialas = True
    font = pygame.font.SysFont(sysfont_name, font_size)
    # size
    width = 0
    height = 0
    min_width = 0
    min_height = 0
    max_width = 0
    max_height = 0
    # flags
    visible = True
    active = True
    # events
    on_hover = None
    on_click = None
    on_release = None
    on_pressed = None
    on_select = None
    on_deselect = None
    # event flags
    can_hover = True
    can_press = True
    can_select = False
    show_press = True
    show_hover = True
    # scrolling
    can_scroll_h = False
    can_scroll_v = False
    scroll_offset = pygame.Vector2()


class _Status:
    hovering = False
    pressing = False
    selected = False
    _clicked = False
    _released = False
    _started_pressing = False

    def check_click(self):
        return self._clicked

    def check_release(self):
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
            if not el is element and not el is element._parent and el.settings.visible and el.settings.active and el._rect.collidepoint(_UIManager.mouse_pos):
                any_other = True
        was_hovering = self.hovering
        self.hovering = element._rect.collidepoint(
            _UIManager.mouse_pos) and element.settings.can_hover and not any_other
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
        self.settings = _Settings()
        self.status = _Status()
        self._topleft = pygame.Vector2()
        self._rect = pygame.Rect(
            self._topleft, (self.settings.width, self.settings.height))
        self._surface = pygame.Surface((1, 1), pygame.SRCALPHA)
        if _UIManager.last_element:
            _UIManager.last_element._add_to_queue(self)
            self._parent = _UIManager.last_element
        else:
            _UIManager.last_element = self
            _UIManager.top_element = self
        self._on_init()
        self.set(**kwargs)

    def _on_init(self): ...
    def _on_set(self, **kwargs): ...
    def _on_enter(self): ...
    def _on_exit(self): ...

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

    def set(self, **kwargs):
        for name, val in kwargs.items():
            if hasattr(self.settings, name):
                setattr(self.settings, name, val)
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

    def _add_child(self, child):
        self._children.append(child)

    def _add_to_queue(self, child):
        self._children_queue.append(child)

    def __enter__(self):
        self._children_queue: list["_Element"] = []
        _UIManager.last_element = self
        self._on_enter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
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
        self._rect.w = self.settings.width
        self._rect.h = self.settings.height
        self.status._update(self)
        if self._surface.get_width() != self.settings.width or self._surface.get_height() != self.settings.height:
            self._surface = pygame.Surface(
                (self.settings.width, self.settings.height), pygame.SRCALPHA)

    def _post_update(self):
        if not self.settings.active:
            return
        for child in self._children:
            child._update()

    def _update(self):
        self._pre_update()
        self._post_update()

    def _on_draw(self): ...

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

    def point_hovering(self, point):
        return self._rect.collidepoint(point)

    @property
    def parent(self):
        return self._parent

    @property
    def children(self):
        return self._children


_SCROLLBAR_SIZE = 15


class _VScrollbar(_Element):
    def _on_init(self):
        self.set(can_press=False, can_hover=False, has_dark_bg=True, width=_SCROLLBAR_SIZE,
                 min_width=_SCROLLBAR_SIZE, max_width=_SCROLLBAR_SIZE, ignore_scroll=True, draw_top=True)
        _UIManager.last_element = self
        self._children_queue = []
        self.handle = _Element()
        self._children.append(self.handle)
        self.handle.set(width=_SCROLLBAR_SIZE, min_width=_SCROLLBAR_SIZE,
                        max_width=_SCROLLBAR_SIZE, ignore_scroll=True)
        self.handle_pos = 0
        _UIManager.last_element = self._parent
        del self._children_queue

    def _update(self):
        if not self._parent.settings.can_scroll_v or self._parent.settings.height >= self._parent.tot_h:
            self.settings.active = False
            self.settings.visible = False
        self.settings.height = self.settings.max_height = self.settings.min_height = self._parent.settings.height
        self.settings.free_position = pygame.Vector2(
            self._parent.settings.width-self.settings.width, 0)

        self._pre_update()

        self.handle_size = (self.settings.height *
                            self._parent.settings.height)/self._parent.tot_h
        scroll_v = (self.handle_pos*self._parent.tot_h)/self.settings.height
        self.handle.settings.free_position = pygame.Vector2(0, self.handle_pos)
        self.handle.settings.height = self.handle.settings.min_height = self.handle.settings.max_height = self.handle_size
        self._parent.settings.scroll_offset.y = scroll_v

        self._post_update()

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
        if not self._parent.settings.can_scroll_h or self._parent.settings.width >= self._parent.tot_w:
            self.settings.active = False
            self.settings.visible = False
        self.settings.width = self.settings.max_width = self.settings.min_width = self._parent.settings.width
        self.settings.free_position = pygame.Vector2(
            0, self._parent.settings.height-self.settings.height)

        self._pre_update()

        self.handle_size = (self.settings.width *
                            self._parent.settings.width)/self._parent.tot_w
        scroll_v = (self.handle_pos*self._parent.tot_w)/self.settings.width
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
