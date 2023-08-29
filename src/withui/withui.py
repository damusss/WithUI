from . import _withuibase as _wuib
import pygame


class Button(_wuib._Element):
    def _on_init(self):
        self.text: str = ""
        self.inner_anchor: str = "center"
        self._inner_surf = None
        self._inner_rect = None

    def _on_set(self, **kwargs):
        if "inner_anchor" in kwargs:
            self.inner_anchor = kwargs["inner_anchor"]
        if "text" in kwargs:
            self.text = str(kwargs["text"])
            self._inner_surf = self.settings.font.render(
                self.text, self.settings.font_antialas, self.settings.text_color)
            self._inner_rect = self._inner_surf.get_rect()
            self._set_h(self._inner_rect.height+self.settings.padding*2)
            self._set_w(self._inner_rect.width+self.settings.padding*2)
        elif "surface" in kwargs:
            self.text = ""
            self._inner_surf = kwargs["surface"]
            if self._inner_surf:
                self._inner_rect = self._inner_surf.get_rect()
                self._set_h(self._inner_rect.height+self.settings.padding*2)
                self._set_w(self._inner_rect.width+self.settings.padding*2)

    def _on_draw(self):
        if self._inner_surf:
            _wuib._anchor_inner(self.inner_anchor, self._rect,
                                self._inner_rect, self.settings.padding)
            self._surface.blit(
                self._inner_surf, self._inner_rect.topleft-self._real_topleft)


class Checkbox(_wuib._Element):
    def _on_init(self):
        self.set(can_select=True)

    def _on_draw(self):
        if self.status.selected:
            iw, ih = self.settings.width-self.settings.padding * \
                2, self.settings.height-self.settings.padding*2
            pygame.draw.rect(self._surface, self.settings.inner_color,
                             (self.settings.width//2-iw//2,
                              self.settings.height//2-ih//2, iw, ih),
                             0, self.settings.border_radius)


class Label(_wuib._Element):
    def _on_init(self):
        self.text: str = ""
        self.inner_anchor: str = "center"
        self._inner_surf = None
        self._inner_rect = None
        self.set(has_background=False, has_outline=False)

    def _on_set(self, **kwargs):
        if "inner_anchor" in kwargs:
            self.inner_anchor = kwargs["inner_anchor"]
        if "text" in kwargs:
            self.text = str(kwargs["text"])
            self._inner_surf = self.settings.font.render(
                self.text, self.settings.font_antialas, self.settings.text_color)
            self._inner_rect = self._inner_surf.get_rect()
            self._set_h(self._inner_rect.height+self.settings.padding*2)
            self._set_w(self._inner_rect.width+self.settings.padding*2)

    def _on_draw(self):
        if self._inner_surf:
            _wuib._anchor_inner(self.inner_anchor, self._rect,
                                self._inner_rect, self.settings.padding)
            self._surface.blit(
                self._inner_surf, self._inner_rect.topleft-self._real_topleft)


class Image(_wuib._Element):
    def _on_init(self):
        self.inner_anchor: str = "center"
        self._inner_surf = None
        self._inner_rect = None
        self.set(has_background=False, has_outline=False,
                 show_hover=False, show_press=False)

    def _on_set(self, **kwargs):
        if "inner_anchor" in kwargs:
            self.inner_anchor = kwargs["inner_anchor"]
        if "surface" in kwargs:
            self._inner_surf = kwargs["surface"]
            if self._inner_surf:
                self._inner_rect = self._inner_surf.get_rect()
                self._set_h(self._inner_rect.height+self.settings.padding*2)
                self._set_w(self._inner_rect.width+self.settings.padding*2)

    def _on_draw(self):
        if self._inner_surf:
            _wuib._anchor_inner(self.inner_anchor, self._rect,
                                self._inner_rect, self.settings.padding)
            self._surface.blit(
                self._inner_surf, self._inner_rect.topleft-self._real_topleft)


class Separator(_wuib._Element):
    def _on_init(self):
        self.set(**INVISIBLE, **STATIC)


class Line(_wuib._Element):
    def _on_init(self):
        self.set(**STATIC)

    def _on_draw(self):
        self.settings.background_color = self.settings.outline_color


class ProgressBar(_wuib._Element):
    def _on_init(self):
        self.set(show_press=False, show_hover=False,
                 padding=0, has_dark_bg=True)
        self.min_value: _wuib._Number = 0
        self.max_value: _wuib._Number = 100
        self.value: _wuib._Number = 50
        self.value_percent: _wuib._Number = None
        self.direction: str = "left-right"
        self._inner_rect = pygame.Rect(0, 0, 0, 0)

    def _on_set(self, **kwargs):
        if "min_value" in kwargs:
            self.min_value = kwargs["min_value"]
        if "max_value" in kwargs:
            self.max_value = kwargs["max_value"]
        if "value" in kwargs:
            self.value = kwargs["value"]
        if "value_percent" in kwargs:
            self.value_percent = kwargs["value_percent"]
        if "direction" in kwargs:
            self.direction = kwargs["direction"]
            if self.direction not in (dirs := ["left-right", "right-left", "top-bottom", "bottom-top"]):
                raise _wuib._WithUIException(
                    f"ProgressBar supported directions are '{dirs}', not '{self.direction}'")

    def _update(self):
        self._pre_update()

        if self.value_percent != None:
            self.value = self.min_value + \
                ((self.max_value-self.min_value)*self.value_percent)/100
        self.value = pygame.math.clamp(
            self.value, self.min_value, self.max_value)

        if "left" in self.direction:
            self._inner_rect.width = ((self.value-self.min_value)*self.settings.width)/(
                self.max_value-self.min_value)-self.settings.padding*2
            self._inner_rect.height = self.settings.height-self.settings.padding*2
        if "top" in self.direction:
            self._inner_rect.height = ((self.value-self.min_value)*self.settings.height)/(
                self.max_value-self.min_value)-self.settings.padding*2
            self._inner_rect.width = self.settings.width-self.settings.padding*2
        if self.direction == "left-right" or self.direction == "top-bottom":
            self._inner_rect.topleft = (
                self.settings.padding, self.settings.padding)
        elif self.direction == "right-left" or self.direction == "bottom-top":
            self._inner_rect.bottomright = (
                self.settings.width-self.settings.padding, self.settings.height-self.settings.padding)

        self._post_update()

    def _on_draw(self):
        if self._inner_rect:
            pygame.draw.rect(self._surface, self.settings.inner_color,
                             self._inner_rect, 0, self.settings.border_radius)


class VCont(_wuib._Element):
    def _on_enter(self):
        self._v_scrollbar._kill() if self._v_scrollbar else None
        self._h_scrollbar._kill() if self._h_scrollbar else None
        self._v_scrollbar = _wuib._VScrollbar()
        self._h_scrollbar = _wuib._HScrollbar()

    def _update(self):
        self._pre_update()
        last: _wuib._Element = None
        tot_h = longest = 0
        self._scroll_margin_h = _wuib._SCROLLBAR_SIZE if self._v_scrollbar.settings.visible and self._v_scrollbar.settings.active else 0
        self._scroll_margin_v = _wuib._SCROLLBAR_SIZE if self._h_scrollbar.settings.visible and self._h_scrollbar.settings.active else 0
        for child in self._children:
            if child.settings.draw_top or child.settings.free_position or not child.settings.visible or not child.settings.active:
                continue
            if last:
                topleft = last._topleft.copy()
                topleft.y += last.settings.height+child.settings.margin
                tot_h += child.settings.margin+child.settings.height
            else:
                topleft = pygame.Vector2()
                topleft.y += child.settings.margin
                tot_h += child.settings.margin*2+child.settings.height

            if not child.settings.parent_anchor and self.settings.center_elements:
                child.settings.parent_anchor = "center"
            if child.settings.parent_anchor:
                match child.settings.parent_anchor:
                    case "left":
                        topleft.x = child.settings.margin
                    case "right":
                        topleft.x = max(self._tot_w, self.settings.width) - \
                            child.settings.margin-child.settings.width-self._scroll_margin_h
                    case "center":
                        topleft.x = (max(self._tot_w, self.settings.width) -
                                     self._scroll_margin_h)//2 - (child.settings.width)//2
                    case _:
                        topleft.x = child.settings.margin
            else:
                topleft.x = child.settings.margin

            child._topleft = topleft
            last = child

            if child.settings.width + child.settings.margin * 2 + self._scroll_margin_h > longest:
                longest = child.settings.width + child.settings.margin * 2 + self._scroll_margin_h

        self._set_h(tot_h)
        self._set_w(longest)

        if self.settings.center_elements and self.settings.height > tot_h:
            for child in self._children:
                child._topleft.y += (self.settings.height -
                                     self._scroll_margin_v)//2-tot_h//2
        self._tot_h = tot_h
        self._tot_w = longest
        self._post_update()

    def _on_init(self):
        self.set(has_dark_bg=True, show_hover=False, show_press=False)
        self._tot_w, self._tot_h = self.settings.width, self.settings.height
        self._scroll_margin_h = self._scroll_margin_v = 0
        self._v_scrollbar = self._h_scrollbar = None


class HCont(_wuib._Element):
    def _on_enter(self):
        self._v_scrollbar._kill() if self._v_scrollbar else None
        self._h_scrollbar._kill() if self._h_scrollbar else None
        self._v_scrollbar = _wuib._VScrollbar()
        self._h_scrollbar = _wuib._HScrollbar()

    def _update(self):
        self._pre_update()
        last: _wuib._Element = None
        tot_w = tallest = 0
        self._scroll_margin_h = _wuib._SCROLLBAR_SIZE if self._v_scrollbar.settings.visible and self._v_scrollbar.settings.active else 0
        self._scroll_margin_v = _wuib._SCROLLBAR_SIZE if self._h_scrollbar.settings.visible and self._h_scrollbar.settings.active else 0
        for child in self._children:
            if child.settings.draw_top or child.settings.free_position or not child.settings.visible or not child.settings.active:
                continue
            if last:
                topleft = last._topleft.copy()
                topleft.x += last.settings.width+child.settings.margin
                tot_w += child.settings.margin+child.settings.width
            else:
                topleft = pygame.Vector2()
                topleft.x += child.settings.margin
                tot_w += child.settings.margin*2+child.settings.width

            if not child.settings.parent_anchor and self.settings.center_elements:
                child.settings.parent_anchor = "center"
            if child.settings.parent_anchor:
                match child.settings.parent_anchor:
                    case "top":
                        topleft.y = child.settings.margin
                    case "bottom":
                        topleft.y = max(self._tot_h, self.settings.height) - \
                            child.settings.margin-child.settings.height-self._scroll_margin_v
                    case "center":
                        topleft.y = (max(self._tot_h, self.settings.height) -
                                     self._scroll_margin_v)//2 - (child.settings.height)//2
                    case _:
                        topleft.y = child.settings.margin
            else:
                topleft.y = child.settings.margin

            child._topleft = topleft
            last = child

            if child.settings.height + child.settings.margin * 2 + self._scroll_margin_v > tallest:
                tallest = child.settings.height + child.settings.margin * 2 + self._scroll_margin_v

        self._set_h(tallest)
        self._set_w(tot_w)

        if self.settings.center_elements and self.settings.width > tot_w:
            for child in self._children:
                child._topleft.x += (self.settings.width -
                                     self._scroll_margin_h)//2-tot_w//2
        self._tot_w = tot_w
        self._tot_h = tallest
        self._post_update()

    def _on_init(self):
        self.set(has_dark_bg=True, can_hover=False, can_press=False)
        self._tot_w, self._tot_h = self.settings.width, self.settings.height
        self._scroll_margin_h = self._scroll_margin_v = 0
        self._v_scrollbar = self._h_scrollbar = None


class Slideshow(HCont):
    def _on_init(self):
        super()._on_init()
        self._surfaces = []
        self._surface_index = 0
        self.__enter__()
        self.left_arrow: Button = Button(
            text="<", on_click=self._on_left_click, height_percent=50)
        self.image: Image = Image(surface=self._surfaces[self._surface_index] if len(
            self._surfaces) > 0 else None)
        self.right_arrow: Button = Button(
            text=">", on_click=self._on_right_click, height_percent=50)
        self.__exit__()
        self.set(center_elements=True)

    def _on_set(self, **kwargs):
        if "surfaces" in kwargs:
            self._surfaces = kwargs["surfaces"]
            if self._surface_index >= len(self._surfaces):
                self._surface_index = len(self._surfaces)-1
            self.image.set(surface=self._surfaces[self._surface_index] if len(
                self._surfaces) > 0 else None)
        if "surface_index" in kwargs:
            self._surface_index = pygame.math.clamp(
                kwargs["surface_index"], 0, len(self._surfaces)-1)
            self.image.set(surface=self._surfaces[self._surface_index] if len(
                self._surfaces) > 0 else None)

    def _on_left_click(self, btn):
        self._surface_index -= 1
        if self._surface_index < 0:
            self._surface_index = len(self._surfaces)-1
        self.image.set(surface=self._surfaces[self._surface_index] if len(
            self._surfaces) > 0 else None)

    def _on_right_click(self, btn):
        self._surface_index += 1
        if self._surface_index >= len(self._surfaces):
            self._surface_index = 0
        self.image.set(surface=self._surfaces[self._surface_index] if len(
            self._surfaces) > 0 else None)

    @property
    def current_surface(self) -> pygame.Surface:
        return self.image._inner_surf


class SelectionList(VCont):
    def _on_init(self):
        super()._on_init()
        self._option_buttons: list["Button"] = []
        self._multi_select = False
        self.set(**STATIC, **SCROLLABLE)

    def _on_set(self, **kwargs):
        if "options" in kwargs:
            previously_selected = [btn.text for btn in self._option_buttons]
            for btn in self._option_buttons:
                btn._kill()
            self.__enter__()
            for option in kwargs["options"]:
                btn = Button(text=option, width_percent=100, has_outline=False,
                             can_select=True, on_select=self._on_select)
                if option in previously_selected:
                    btn.status.select()
                self._option_buttons.append(btn)
            self.__exit__()
        if "multi_select" in kwargs:
            was = self._multi_select
            self._multi_select = kwargs["multi_select"]
            if was and not self._multi_select:
                for i, btn in enumerate(self._option_buttons):
                    if i > 0:
                        btn.status.deselect()
        if "selected_option" in kwargs:
            if self._multi_select:
                raise _wuib._WithUIException(
                    f"If multi select is enabled, only the 'selected_options' setting is available, not 'selected_option'")
            for btn in self._option_buttons:
                if btn.text == kwargs["selected_option"]:
                    btn.status.select()
                else:
                    btn.status.deselect()
        if "selected_options" in kwargs:
            if not self._multi_select:
                raise _wuib._WithUIException(
                    f"If multi select is disabled, only the 'selected_option' setting is available, not 'selected_options'")
            for btn in self._option_buttons:
                if btn.text in kwargs["selected_option"]:
                    btn.status.select()
                else:
                    btn.status.deselect()

    def _on_select(self, button):
        if self._multi_select:
            if self.settings.on_select:
                self.settings.on_select(
                    [button.text for button in self._option_buttons if button.status.selected])
        else:
            for btn in self._option_buttons:
                if btn.text != button.text:
                    btn.status.deselect()
            if self.settings.on_select:
                self.settings.on_select(button.text)

    def get_selection(self) -> str:
        if self._multi_select:
            raise _wuib._WithUIException(
                f"If multi select is enabled, you can only call 'get_multi_selection', not 'get_selection'")
        for btn in self._option_buttons:
            if btn.status.selected:
                return btn.text

    def get_multi_selection(self) -> list[str]:
        if not self._multi_select:
            raise _wuib._WithUIException(
                f"If multi select is disabled, you can only call 'get_selection', not 'get_multi_selection'")
        return [button.text for button in self._option_buttons if button.status.selected]


class UserSettings:
    settings: dict[str, dict[str, _wuib.typing.Any]] = {}

    @classmethod
    def add(cls, name: str, **kwargs: dict[str, _wuib.typing.Any]) -> dict[str, _wuib.typing.Any]:
        cls.settings[name] = kwargs
        return kwargs

    @classmethod
    def get(cls, name: str) -> dict[str, _wuib.typing.Any]:
        return cls.settings[name]


INVISIBLE: dict[str, bool] = {
    "has_background": False,
    "has_outline": False
}

SCROLLABLE: dict[str, bool] = {
    "can_scroll_h": True,
    "can_scroll_v": True
}

STATIC: dict[str, bool] = {
    "can_press": False,
    "can_hover": False,
    "can_select": False,
}


def min_max_width(width: _wuib._Number) -> dict[str, _wuib._Number]:
    return {
        "width": width,
        "min_width": width,
        "max_width": width
    }


def min_max_height(height: _wuib._Number) -> dict[str, _wuib._Number]:
    return {
        "height": height,
        "min_height": height,
        "max_height": height
    }


def min_max_square(size: _wuib._Number) -> dict[str, _wuib._Number]:
    return {
        "width": size,
        "min_width": size,
        "max_width": size,
        "height": size,
        "min_height": size,
        "max_height": size
    }


def settings_help(element: str | type[_wuib._Element] | _wuib._Element = "Element", setting: str = None) -> str | dict[str, str]:
    element_name = element
    if isinstance(element_name, type):
        element_name = element.__name__
    elif isinstance(element_name, _wuib._Element):
        element_name = element.__class__.__name__
    if element_name in _wuib._SETTINGS_HELP:
        settings = _wuib._SETTINGS_HELP[element_name].copy()
        if element_name != "Element":
            settings.update(_wuib._SETTINGS_HELP["Element"])
        if setting is not None:
            if setting in settings:
                return settings[setting]
            else:
                raise _wuib._WithUIException(
                    f"Element '{element_name}' has no setting '{setting}'")
        else:
            return settings
    else:
        raise _wuib._WithUIException(
            f"No element exist with name '{element_name}'. Available are: '{_wuib._SETTINGS_HELP.keys()}'")


def pretty_print(json_like_object: _wuib.typing.Any):
    if isinstance(json_like_object, str):
        print(json_like_object)
        return
    formatted = _wuib.json.dumps(json_like_object, indent=2)
    print(formatted)


def pretty_format(json_like_object: _wuib.typing.Any) -> str:
    if isinstance(json_like_object, str):
        return json_like_object
    formatted = _wuib.json.dumps(json_like_object, indent=2)
    return formatted


def update_ui():
    _wuib._UIManager.update()
    _wuib._UIManager.top_element._update()


def draw_ui(surface):
    _wuib._UIManager.top_element._draw(surface)
    for el in _wuib._UIManager.top_elements:
        el._draw(surface)
