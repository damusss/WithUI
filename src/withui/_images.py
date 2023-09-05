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
            self._refresh_surface()

    def _on_draw(self):
        if self._inner_surf:
            _wuib._anchor_inner(self._inner_anchor, self._rect,
                                self._inner_rect, self.settings.padding)
            self._surface.blit(
                self._inner_surf, self._inner_rect.topleft-self._real_topleft)

    def _refresh_surface(self):
        if self._inner_surf:
            self._inner_rect = self._inner_surf.get_rect()
            self._set_h(self._inner_rect.height+self.settings.padding*2)
            self._set_w(self._inner_rect.width+self.settings.padding*2)
        self._set_dirty()

    @property
    def surface(self) -> pygame.Surface | None:
        return self._inner_surf

    @surface.setter
    def surface(self, value):
        self._inner_surf = value
        self._refresh_surface()


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
        if self.settings.on_select:
            self.settings.on_select(
                self.image._inner_surf, self._surface_index)
        self._set_dirty()

    def _on_right_click(self, btn):
        self._surface_index += 1
        if self._surface_index >= len(self._surfaces):
            self._surface_index = 0
        self.image.set(surface=self._surfaces[self._surface_index] if len(
            self._surfaces) > 0 else None)
        if self.settings.on_select:
            self.settings.on_select(
                self.image._inner_surf, self._surface_index)
        self._set_dirty()

    @property
    def surface(self) -> pygame.Surface:
        return self.image._inner_surf

class GIF(_wuib._Element):
    def _on_init(self):
        self.set(has_background=False,has_outline=False,can_press=False,can_hover=False)
        self._frames = []
        self._inner_surf = None
        self._inner_rect = None
        self._inner_anchor = "center"
        self._frame_index = 0
        self._frame_cooldown = 100
        self._last_change = 0
        
    def _on_set(self, **kwargs):
        if "inner_anchor" in kwargs:
            self._inner_anchor = kwargs["inner_anchor"]
        if "frames" in kwargs:
            self._frames = kwargs["frames"]
            self._frame_index = 0
            if self._frames:
                self._inner_surf = self._frames[int(self._frame_index)]
                self._inner_rect = self._inner_surf.get_rect()
                self._set_h(self._inner_rect.height+self.settings.padding*2)
                self._set_w(self._inner_rect.width+self.settings.padding*2)
        if "frame_cooldown" in kwargs:
            self._frame_cooldown = kwargs["frame_cooldown"]
        
    def _on_draw(self):
        if self._inner_surf:
            _wuib._anchor_inner(self._inner_anchor, self._rect,
                                self._inner_rect, self.settings.padding)
            self._surface.blit(
                self._inner_surf, self._inner_rect.topleft-self._real_topleft)
        
    def _update(self):
        self._pre_update()
        
        if not self.settings.active or not self._frames: return
        if _wuib._UIManager.ticks - self._last_change >= self._frame_cooldown:
            self._last_change = pygame.time.get_ticks()
            self._frame_index += 1
            if self._frame_index >= len(self._frames):
                self._frame_index = 0
            self._inner_surf = self._frames[int(self._frame_index)]
            self._inner_rect = self._inner_surf.get_rect()
            self._set_h(self._inner_rect.height+self.settings.padding*2)
            self._set_w(self._inner_rect.width+self.settings.padding*2)
            self._set_dirty()
        
        self._post_update()
        
    @property
    def frame(self):
        return self._inner_surf