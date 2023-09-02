import pygame

from . import _base as _wuib
from . import _containers as _conts
from . import _texts as _txts


class TooltipManager:
    def __init__(self, width: int = 150, activate_after_ms: int = 800):
        with _conts.VCont(can_navigate=False, min_max_width=width, auto_resize_h=False, visible=False, free_position=pygame.Vector2()) as tooltip_cont:
            self._tooltip_cont = tooltip_cont
            self._tooltip_cont._root_index = 999999
            self._tooltip_cont._always_top = True
            self._title_label = _txts.Label(
                text="Tooltip Title", auto_resize_h=False, min_max_width=width, font_size=25)
            self._description_label = _txts.Label(
                text="Tooltip Description", auto_resize_h=False, min_max_width=width, font_size=17, text_align="left")
        self._default_activate_after: int = activate_after_ms
        self._data: list[dict[str, int | _wuib._Element | str | bool]] = []

    def update(self):
        self._tooltip_cont.settings.visible = False
        for tooltip in self._data:
            was_hovering = tooltip["was_hovering"]
            if tooltip["element"].status.hovering or self._tooltip_cont.status._absolute_hover:
                tooltip["was_hovering"] = True
                if not was_hovering:
                    tooltip["start_hover"] = pygame.time.get_ticks()
                else:
                    if pygame.time.get_ticks()-tooltip["start_hover"] >= tooltip["activate_after"]:
                        self._tooltip_cont.settings.visible = True
                        if self._title_label._text != tooltip["title"]:
                            self._title_label.set(text=tooltip["title"])
                        if self._description_label._text != tooltip["description"]:
                            self._description_label.set(
                                text=tooltip["description"])
                        mouse_top_half = _wuib._UIManager.mouse_pos[1] <= pygame.display.get_window_size()[
                            1]//2
                        self._tooltip_cont.settings.free_position = pygame.Vector2((tooltip["element"]._rect.midtop if not mouse_top_half else tooltip["element"]._rect.midbottom)) - \
                            (pygame.Vector2(self._tooltip_cont.settings.width//2, self._tooltip_cont.settings.height+self._tooltip_cont.settings.margin) if
                             not mouse_top_half else
                             pygame.Vector2(self._tooltip_cont.settings.width//2, self._tooltip_cont.settings.margin))
            else:
                tooltip["was_hovering"] = False

    def register_tooltip(self, element: _wuib._Element, tooltip_title: str, tooltip_description: str, activate_after_ms: int | None = None):
        if activate_after_ms is None:
            activate_after_ms = self._default_activate_after
        self._data.append({
            "element": element,
            "title": tooltip_title,
            "description": tooltip_description,
            "activate_after": activate_after_ms,
            "start_hover": 0,
            "was_hovering": False
        })

    @property
    def tooltip_container(self) -> _conts.VCont:
        return self._tooltip_cont

    @property
    def tooltip_title(self) -> _txts.Label:
        return self._title_label

    @property
    def tooltip_description(self) -> _txts.Label:
        return self._description_label


class TypingAnimation:
    ...


class HoverGrowAnimation:
    ...
