import pygame

from . import _base as _wuib
from ._buttons import Button
from ._containers import HCont


class Image(_wuib._Element):
    def _on_init(self):
        self._inner_anchor: str = "center"
        self._inner_surf = None
        self._inner_rect = None
        self.set(has_background=False, has_outline=False,
                 show_hover=False, show_press=False)

    def _on_set(self, **kwargs):
        if "inner_anchor" in kwargs:
            self._inner_anchor = kwargs["inner_anchor"]
        if "surface" in kwargs:
            self._inner_surf = kwargs["surface"]
            if self._inner_surf:
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
    def surface(self)->pygame.Surface|None:
        return self._inner_surf

    @surface.setter
    def surface(self, value):
        self._text = ""
        self._inner_surf = value
        if self._inner_surf:
            self._inner_rect = self._inner_surf.get_rect()
            self._set_h(self._inner_rect.height+self.settings.padding*2)
            self._set_w(self._inner_rect.width+self.settings.padding*2)


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
    def surface(self) -> pygame.Surface:
        return self.image._inner_surf
