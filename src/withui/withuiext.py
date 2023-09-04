import pygame
import pathlib
import os

from . import _base as _wuib
from . import _containers as _conts
from . import _texts as _txts
from . import _buttons as _btns
from . import _windows as _wins
from . import _menus


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
                        mouse_top_half = _wuib._UIManager.mouse_pos[1] <= (ds := pygame.display.get_window_size()[
                            1])//2
                        xp = max(0, min(self._tooltip_cont.settings.width //
                                 2, ds-self._tooltip_cont.settings.width))
                        self._tooltip_cont.settings.free_position = pygame.Vector2((tooltip["element"]._rect.midtop if not mouse_top_half else tooltip["element"]._rect.midbottom)) - \
                            (pygame.Vector2(xp, self._tooltip_cont.settings.height+self._tooltip_cont.settings.margin) if
                             not mouse_top_half else
                             pygame.Vector2(xp, self._tooltip_cont.settings.margin))
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


class AnimationsManager:
    animations: list[_wuib.typing.Union["TypingAnimation",
                                        "HoverGrowAnimation"]] = []

    @classmethod
    def update(cls, delta_time_s: float = 1):
        for animation in cls.animations:
            animation.update(delta_time_s)


class TypingAnimation:
    def __init__(self, element_supporting_text: _txts.Label | _txts.Entryline | _btns.Button, text: str, speed: int = 25, speed_comma: int = 150, speed_dot: int = 300, speed_newline: int = 400):
        self._element = element_supporting_text
        self._text = text
        self._speed = speed
        self._speed_comma = speed_comma
        self._speed_dot = speed_dot
        self._speed_newline = speed_newline
        self._next_cooldown = self._speed
        self._last_char = 0
        self._char_index = 0
        AnimationsManager.animations.append(self)

    def start(self):
        if not self._text:
            return
        self._char_index = 0
        self._next_cooldown = 0
        self._last_char = 0
        self._element.set(text="")

    def finish(self):
        if not self._text:
            return
        self._char_index = len(self._text)-1
        self._element.set(text=self._text)

    def update(self, delta_time_s: float = 1):
        if not self._text:
            return
        if self._char_index < len(self._text):
            if _wuib._UIManager.ticks - self._last_char >= self._next_cooldown:
                self._last_char = _wuib._UIManager.ticks
                self._char_index += 1
                if self._char_index >= len(self._text):
                    self._char_index = len(self._text)-1
                    self.finish()
                else:
                    self._element.set(text=self._text[:self._char_index])
                    if self._char_index == 0:
                        return
                    cur_char = self._text[self._char_index-1]
                    match cur_char:
                        case ",":
                            self._next_cooldown = self._speed_comma
                        case "." | "!" | "?":
                            self._next_cooldown = self._speed_dot
                        case "\n":
                            self._next_cooldown = self._speed_newline
                        case _:
                            self._next_cooldown = self._speed

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        self._char_index = len(self._text)


class HoverGrowAnimation:
    def __init__(self, element: _wuib._Element, background_image: pygame.Surface, grow_factor: float = 1.1, speed: float = 1):
        self._element = element
        self._bg_image = background_image
        self._full_size = pygame.transform.scale_by(
            self._bg_image, grow_factor).get_size()
        self._modified_image = self._bg_image
        self._grow_factor = grow_factor
        self._speed = speed
        self._factor = 1
        self._grow_dir = 0
        self._element.set(on_mouse_enter=self._element_mouse_enter, on_mouse_exit=self._element_mouse_exit, auto_resize_h=False, auto_resize_v=False,
                          min_max_size=pygame.Vector2(self._full_size)+pygame.Vector2(element.settings.background_padding)*2)
        AnimationsManager.animations.append(self)

    def _element_mouse_enter(self, el):
        self._grow_dir = 1

    def _element_mouse_exit(self, el):
        self._grow_dir = -1

    def update(self, delta_time_s: float):
        prev = self._factor
        self._factor += self._grow_dir*self._speed*delta_time_s
        self._factor = pygame.math.clamp(self._factor, 1, self._grow_factor)
        if prev != self._factor:
            self._modified_image = pygame.transform.scale_by(
                self._bg_image, self._factor)
            self._element.set(background_image=self._modified_image,)

    @property
    def background_image(self) -> pygame.Surface:
        return self._bg_image

    @background_image.setter
    def background_image(self, value):
        self._bg_image = value
        self._full_size = pygame.transform.scale_by(
            self._bg_image, self._grow_factor).get_size()
        self._element.set(on_mouse_enter=self._element_mouse_enter, on_mouse_exit=self._element_mouse_exit, auto_resize_h=False, auto_resize_v=False,
                          min_max_size=pygame.Vector2(self._full_size)+pygame.Vector2(self._element.settings.background_padding))

    @property
    def current_image(self) -> pygame.Surface:
        return self._modified_image


class FileDialog:
    def __init__(self,
                 topleft: _wuib._Coordinate,
                 width: float,
                 height: float,
                 title: str = "Choose a file...",
                 on_close: _wuib.typing.Callable[[
                     pathlib.Path | None], None] | None = None,
                 on_cancel: _wuib.typing.Callable[[
                     pathlib.Path | None], None] | None = None,
                 on_ok: _wuib.typing.Callable[[
                     pathlib.Path | None], None] | None = None,
                 start_path: str | None = None,
                 allow_folders: bool = True,
                 filter_extensions: list[str] | None = None):
        self._path = pathlib.Path(
            os.getcwd() if not start_path else start_path)
        self._allow_folders = allow_folders
        self._filter = filter_extensions
        self._on_close, self._on_cancel, self._on_ok = on_close, on_cancel, on_ok
        with _wins.Window(title=title, topleft=topleft, min_max_width=width, min_max_height=height, on_close=self._on_window_close) as win:
            self._window = win
            self._path_entry = _txts.Entryline(
                text=str(self._path), width_percent=100, on_change=self._on_path_change)
            self._item_list = _menus.SelectionList(width_percent=100)
            with _conts.HCont(center_elements=True, parent_anchor="right", has_outline=False, has_background=False, margin=0) as cont:
                self._cont = cont
                self._back_btn = _btns.Button(
                    text="<-", on_click=self._on_back_click)
                self._open_btn = _btns.Button(
                    text="Open", on_click=self._on_open_click)
                self._ok_btn = _btns.Button(
                    text="Ok", on_click=self._on_ok_click)
                self._cancel_btn = _btns.Button(
                    text="Cancel", on_click=self._on_cancel_click)
        _wuib._UIManager.root_elements.append(self)
        self._root_index = 0
        self._refresh_items()
        self._refresh_path_entry()

    def _validate_path(self, path, full=False):
        if not self._allow_folders and os.path.isdir(str(path)) and full:
            return False
        if self._filter is not None:
            if os.path.isfile(str(path)) and not path.name.split(".")[1] in self._filter:
                return False
        return True

    def _refresh_items(self):
        try:
            items = os.listdir(str(self._path))
        except NotADirectoryError:
            if self._on_ok:
                self._on_ok(self._path)
            self._window.kill()
            del self
        except FileNotFoundError:
            if self._on_close:
                self._on_close()
            self._window.kill()
            del self
        else:
            self._item_list.set(
                options=[item for item in items if self._validate_path(self._path/item)])

    def _refresh_path_entry(self):
        self._path_entry.set(text=str(self._path))
        self._path_entry.place_cursor(len(self._path_entry._text))

    def _on_path_change(self, entry):
        if os.path.exists(self._path_entry.text) and self._validate_path(pathlib.Path(self._path_entry.text)):
            self._path = pathlib.Path(self._path_entry.text)
            self._refresh_items()

    def _on_window_close(self, win):
        if self._on_close:
            self._on_close()
        self._window.kill()
        del self

    def _on_back_click(self, btn):
        self._path = self._path.parent
        self._refresh_items()
        self._refresh_path_entry()

    def _on_ok_click(self, btn):
        if self._on_ok:
            if sel := self._item_list.get_selection():
                if self._validate_path(self._path/sel, True):
                    self._on_ok(self._path/sel)
                    self._window.kill()
                    del self
            else:
                if self._validate_path(self._path, True):
                    self._on_ok(self._path)
                    self._window.kill()
                    del self

    def _on_cancel_click(self, btn):
        if self._on_cancel:
            self._on_cancel()
        self._window.kill()
        del self

    def _on_open_click(self, btn):
        if sel := self._item_list.get_selection():
            self._path = self._path/sel
            self._refresh_items()
            self._refresh_path_entry()

    def _update(self):
        self._item_list.set(min_max_height=(self._window._elements_cont.settings.height - self._cont.settings.height -
                            self._path_entry.settings.height-self._cont.settings.margin*4-self._path_entry.settings.margin*4))

    def _draw(self, _): ...

    @property
    def open_path(self) -> pathlib.Path:
        return pathlib.Path(str(self._path))

    @open_path.setter
    def open_path(self, value):
        self._path = pathlib.Path(str(value))
        self._refresh_items()
        self._refresh_path_entry()

    @property
    def selected_path(self) -> pathlib.Path:
        if sel := self._item_list.get_selection():
            return self._path/sel
        return pathlib.Path(str(self._path))
