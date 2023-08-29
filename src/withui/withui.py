import _withuibase as _wuib
import pygame


class Button(_wuib._Element):
    def _on_init(self):
        self.text = ""
        self.anchor = "center"
        self._inner_surf = None
        self._inner_rect = None

    def _on_set(self, **kwargs):
        if "anchor" in kwargs:
            self.anchor = kwargs["anchor"]
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
            self._inner_rect = self._inner_surf.get_rect()
            self._set_h(self._inner_rect.height+self.settings.padding*2)
            self._set_w(self._inner_rect.width+self.settings.padding*2)

    def _on_draw(self):
        if self._inner_surf:
            _wuib._anchor_inner(self.anchor, self._rect,
                                self._inner_rect, self.settings.padding)
            self._surface.blit(
                self._inner_surf, self._inner_rect.topleft-self._real_topleft)


class Label(_wuib._Element):
    def _on_init(self):
        self.text = ""
        self.anchor = "center"
        self._inner_surf = None
        self._inner_rect = None
        self.set(has_background=False, has_outline=False)

    def _on_set(self, **kwargs):
        if "anchor" in kwargs:
            self.anchor = kwargs["anchor"]
        if "text" in kwargs:
            self.text = str(kwargs["text"])
            self._inner_surf = self.settings.font.render(
                self.text, self.settings.font_antialas, self.settings.text_color)
            self._inner_rect = self._inner_surf.get_rect()
            self._set_h(self._inner_rect.height+self.settings.padding*2)
            self._set_w(self._inner_rect.width+self.settings.padding*2)

    def _on_draw(self):
        if self._inner_surf:
            _wuib._anchor_inner(self.anchor, self._rect,
                                self._inner_rect, self.settings.padding)
            self._surface.blit(
                self._inner_surf, self._inner_rect.topleft-self._real_topleft)


class Image(_wuib._Element):
    def _on_init(self):
        self.anchor = "center"
        self._inner_surf = None
        self._inner_rect = None
        self.set(has_background=False, has_outline=False,
                 show_hover=False, show_press=False)

    def _on_set(self, **kwargs):
        if "anchor" in kwargs:
            self.anchor = kwargs["anchor"]
        if "surface" in kwargs:
            self._inner_surf = kwargs["surface"]
            self._inner_rect = self._inner_surf.get_rect()
            self._set_h(self._inner_rect.height+self.settings.padding*2)
            self._set_w(self._inner_rect.width+self.settings.padding*2)

    def _on_draw(self):
        if self._inner_surf:
            _wuib._anchor_inner(self.anchor, self._rect,
                                self._inner_rect, self.settings.padding)
            self._surface.blit(
                self._inner_surf, self._inner_rect.topleft-self._real_topleft)


class VCont(_wuib._Element):
    def _on_enter(self):
        self.v_scrollbar = _wuib._VScrollbar()
        self.h_scrollbar = _wuib._HScrollbar()

    def _update(self):
        self._pre_update()
        last: _wuib._Element = None
        tot_h = longest = 0
        for child in self._children:
            if child.settings.draw_top or child.settings.free_position:
                continue
            if last:
                topleft = last._topleft.copy()
                topleft.y += last.settings.height+child.settings.margin//2
                tot_h += child.settings.margin//2+child.settings.height
            else:
                topleft = pygame.Vector2()
                topleft.y += child.settings.margin
                tot_h += child.settings.margin*2+child.settings.height

            topleft.x = self.settings.width//2 - \
                (child.settings.width)//2 if self.settings.center_elements else child.settings.margin

            child._topleft = topleft
            last = child

            if child.settings.width + child.settings.margin * 2 > longest:
                longest = child.settings.width + child.settings.margin * 2

        self._set_h(tot_h)
        self._set_w(longest)

        if self.settings.center_elements and self.settings.height > tot_h:
            for child in self._children:
                child._topleft.y += self.settings.height//2-tot_h//2
        self.tot_h = tot_h
        self.tot_w = longest
        self._post_update()

    def _on_init(self):
        self.set(has_dark_bg=True, show_hover=False, show_press=False)


class HCont(_wuib._Element):
    def _on_enter(self):
        self.v_scrollbar = _wuib._VScrollbar()
        self.h_scrollbar = _wuib._HScrollbar()

    def _update(self):
        self._pre_update()
        last: _wuib._Element = None
        tot_w = tallest = 0
        for child in self._children:
            if child.settings.draw_top or child.settings.free_position:
                continue
            if last:
                topleft = last._topleft.copy()
                topleft.x += last.settings.width+child.settings.margin//2
                tot_w += child.settings.margin//2+child.settings.width
            else:
                topleft = pygame.Vector2()
                topleft.x += child.settings.margin
                tot_w += child.settings.margin*2+child.settings.width

            topleft.y = self.settings.height//2 - \
                (child.settings.height)//2 if self.settings.center_elements else child.settings.margin

            child._topleft = topleft
            last = child

            if child.settings.height + child.settings.margin * 2 > tallest:
                tallest = child.settings.height + child.settings.margin * 2

        self._set_h(tallest)
        self._set_w(tot_w)

        if self.settings.center_elements and self.settings.width > tot_w:
            for child in self._children:
                child._topleft.x += self.settings.width//2-tot_w//2
        self.tot_w = tot_w
        self.tot_h = tallest
        self._post_update()

    def _on_init(self):
        self.set(has_dark_bg=True, can_hover=False, can_press=False)


class UserSettings:
    settings: dict[str, dict] = {}

    @classmethod
    def add(cls, name: str, **kwargs):
        cls.settings[name] = kwargs

    @classmethod
    def get(cls, name: str):
        return cls.settings[name]


INVISIBLE = {
    "has_background": False,
    "has_outline": False
}

SCROLLABLE = {
    "can_scroll_h": True,
    "can_scroll_v": True
}


def min_max_width(width):
    return {
        "width": width,
        "min_width": width,
        "max_width": width
    }


def min_max_height(height):
    return {
        "height": height,
        "min_height": height,
        "max_height": height
    }


def update_ui():
    _wuib._UIManager.update()
    _wuib._UIManager.top_element._update()


def draw_ui(surface):
    _wuib._UIManager.top_element._draw(surface)
    for el in _wuib._UIManager.top_elements:
        el._draw(surface)
