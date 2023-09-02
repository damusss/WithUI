import pygame

from ._constants import _SLIDER_SIZE, _HANDLE_SIZE
from . import _base as _wuib
from ._buttons import Button


class ProgressBar(_wuib._Element):
    def _on_init(self):
        self.set(show_press=False, show_hover=False,
                 padding=0, has_dark_bg=True)
        self.min_value: float = 0
        self.max_value: float = 100
        self.value: float = 50
        self.value_percent: float = None
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


class Slider(_wuib._Element):
    def _on_init(self):
        self.set(can_hover=False, can_press=False, can_select=False, has_dark_bg=True,
                 height=_SLIDER_SIZE, margin=_HANDLE_SIZE//2)
        self._direction = "horizontal"
        self.handle: Button = Button(free_position=pygame.Vector2(0, 0))
        self._handle_pos = 0
        self._handle_size = _HANDLE_SIZE
        self._on_move = None
        self.value: float = 0

    def _on_set(self, **kwargs):
        if "slider_size" in kwargs:
            if "direction" in kwargs:
                self._direction = kwargs["direction"]
                if self._direction not in ["horizontal", "vertical"]:
                    raise _wuib._WithUIException(
                        f"Supported slider directions are horizontal and vertical, not '{self._direction}'")
            if self._direction == "horizontal":
                self.settings.width = kwargs["slider_size"]
            else:
                self.settings.height = kwargs["slider_size"]
        if "direction" in kwargs:
            self._direction = kwargs["direction"]
            if self._direction not in ["horizontal", "vertical"]:
                raise _wuib._WithUIException(
                    f"Supported slider directions are horizontal and vertical, not '{self._direction}'")
            if self._direction == "horizontal":
                self.settings.height = _SLIDER_SIZE
            else:
                self.settings.width = _SLIDER_SIZE
        if "value" in kwargs:
            self.value = pygame.math.clamp(kwargs["value"], 0, 1)
            if self._direction == "horizontal":
                self._handle_pos = self.settings.width*self.value
            else:
                self._handle_pos = self.settings.height*self.value
        if "value_percent" in kwargs:
            self.value = pygame.math.clamp(kwargs["value_percent"], 0, 100)/100
            if self._direction == "horizontal":
                self._handle_pos = self.settings.width*self.value
            else:
                self._handle_pos = self.settings.height*self.value
        if "handle_size" in kwargs:
            self._handle_size = kwargs["handle_size"]
            self.settings.margin = self._handle_size//2
        if "on_move" in kwargs:
            self._on_move = kwargs["on_move"]

    def _update(self):
        self._pre_update()

        self.handle.settings.width = self.handle.settings.height = self._handle_size
        if self._direction == "horizontal":
            self.handle.settings.free_position = pygame.Vector2(
                self._topleft.x+self._handle_pos-self._handle_size//4, self._topleft.y+self.settings.height//2-self._handle_size//2)
        else:
            self.handle.settings.free_position = pygame.Vector2(
                self._topleft.x+self.settings.width//2-self._handle_size//2, self._topleft.y+self._handle_pos-self._handle_size//4)
        
        if not self.settings.active: return
        
        previous = self._handle_pos
        if self.handle.status.pressing:
            self._handle_pos += _wuib._UIManager.mouse_rel[0 if self._direction ==
                                                           "horizontal" else 1]
            if self._handle_pos < 0:
                self._handle_pos = 0
            size = self.settings.width if self._direction == "horizontal" else self.settings.height
            if self._handle_pos > size-self._handle_size//2:
                self._handle_pos = size-self._handle_size//2

        if self._handle_pos == 0:
            self.value = 0
        else:
            self.value = self._handle_pos / \
                ((self.settings.width if self._direction ==
                 "horizontal" else self.settings.height)-self._handle_size//2)

        if previous != self._handle_pos and self._on_move:
            self._on_move(self, self._handle_pos-previous)
            
        self._post_update()

    @property
    def value_percent(self) -> float:
        return self.value*100
