import pygame

from . import _base as _wuib


class Button(_wuib._Element):
    def _on_init(self):
        self._text: str = ""
        self._inner_anchor: str = "center"
        self._inner_surf = None
        self._inner_rect = None

    def _on_set(self, **kwargs):
        if "inner_anchor" in kwargs:
            self._inner_anchor = kwargs["inner_anchor"]
        if "text" in kwargs:
            self._text = str(kwargs["text"])
            self._inner_surf = self.settings.font.render(
                self.text, self.settings.font_antialas, self.settings.text_color)
            self._inner_rect = self._inner_surf.get_rect()
            self._set_h(self._inner_rect.height+self.settings.padding*2)
            self._set_w(self._inner_rect.width+self.settings.padding*2)
        elif "surface" in kwargs:
            self._text = ""
            self._inner_surf = kwargs["surface"]
            if self._inner_surf:
                self._inner_rect = self._inner_surf.get_rect()
                self._set_h(self._inner_rect.height+self.settings.padding*2)
                self._set_w(self._inner_rect.width+self.settings.padding*2)
                
    def _on_font_change(self):
        if not self._text: return
        self._inner_surf = self.settings.font.render(
            self._text, self.settings.font_antialas, self.settings.text_color)
        self._inner_rect = self._inner_surf.get_rect()
        self._set_h(self._inner_rect.height+self.settings.padding*2)
        self._set_w(self._inner_rect.width+self.settings.padding*2)

    def _on_draw(self):
        if self._inner_surf:
            _wuib._anchor_inner(self._inner_anchor, self._rect,
                                self._inner_rect, self.settings.padding)
            self._surface.blit(
                self._inner_surf, self._inner_rect.topleft-self._real_topleft)

    @property
    def text(self)->str:
        return self._text

    @text.setter
    def text(self, value):
        self._text = str(value)
        self._inner_surf = self.settings.font.render(
            self.text, self.settings.font_antialas, self.settings.text_color)
        self._inner_rect = self._inner_surf.get_rect()
        self._set_h(self._inner_rect.height+self.settings.padding*2)
        self._set_w(self._inner_rect.width+self.settings.padding*2)

    @property
    def surface(self)->pygame.Surface:
        return self._inner_surf

    @surface.setter
    def surface(self, value):
        self._text = ""
        self._inner_surf = value
        if self._inner_surf:
            self._inner_rect = self._inner_surf.get_rect()
            self._set_h(self._inner_rect.height+self.settings.padding*2)
            self._set_w(self._inner_rect.width+self.settings.padding*2)


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
