import pygame

from . import _base as _wuib


class Separator(_wuib._Element):
    def _on_init(self):
        self.set(has_background=False, has_outline=False,
                 can_hover=False, can_press=False, can_select=False)


class Line(_wuib._Element):
    def _on_init(self):
        self.set(can_hover=False, can_press=False, can_select=False, height=2)

    def _on_draw(self):
        self.settings.background_color = self.settings.outline_color
