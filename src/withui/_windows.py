import pygame

from . import _base as _wuib
from ._buttons import Button
from ._containers import VCont, HCont
from ._separators import Line


class Window(VCont):
    def _on_init(self):
        self._super = super()
        self._super._on_init()
        if self not in _wuib._UIManager.root_elements:
            raise _wuib._WithUIException(
                f"Window elements should be declared at the top and not have any parent")
        self._finished_instantiating = False
        self.__enter__()
        self._title_cont = HCont(has_background=False, has_outline=False)
        self._title_cont.__enter__()
        self._title_button = Button(
            text="Wui Window", inner_anchor="midleft", margin=0)
        self._close_button = Button(
            text="X", margin=0, on_click=self._on_close_click)
        self._title_cont.__exit__()
        self._line_separator = Line(
            height=self.settings.outline_width, width_percent=100)
        self._elements_cont = VCont(
            has_background=False, has_outline=False, margin=0, can_scroll_v=True, can_scroll_h=True)
        self.__exit__()
        self._finished_instantiating = True
        self._on_close = None
        self._can_drag = True

    def __enter__(self):
        if not self._finished_instantiating:
            self._children_queue: list["_wuib._Element"] = []
            _wuib._UIManager.last_element = self
            self._on_enter()
            return self
        self._elements_cont.__enter__()
        return self

    def __exit__(self, exc_type=None, exc_val=None, exc_tb=None):
        if not self._finished_instantiating:
            _wuib._UIManager.last_element = self._parent
            for child in self._children_queue:
                self._add_child(child)
            self._on_exit()
            del self._children_queue
            return
        self._elements_cont.__exit__()
        _wuib._UIManager.last_element = self._parent

    def _on_set(self, **kwargs):
        if "title" in kwargs:
            self._title_button.set(text=kwargs["title"])
        if "on_close" in kwargs:
            self._on_close = kwargs["on_close"]
        if "topleft" in kwargs:
            self._topleft = pygame.Vector2(kwargs["topleft"])
        if "can_drag" in kwargs:
            self._can_drag = kwargs["can_drag"]

    def _update(self):
        self._elements_cont.settings.height = self._elements_cont.settings.min_height = self._elements_cont.settings.max_height = max(
            1, self.settings.height-self._title_cont.settings.height-self._title_cont.settings.margin*2-(self._line_separator.settings.height+self._line_separator.settings.margin if self._line_separator.settings.visible else 0))
        self._elements_cont.settings.width = self._elements_cont.settings.min_width = self._elements_cont.settings.max_width = max(
            1, self.settings.width-self.settings.margin)
        self._title_cont.settings.width = self._title_cont.settings.min_width = self._title_cont.settings.max_width = max(
            1, self.settings.width)
        self._close_button.settings.width = self._close_button.settings.height
        self._title_button.settings.width = self._title_button.settings.min_width = self._title_button.settings.max_width = max(
            1, self.settings.width-self._close_button.settings.width-self._title_cont.settings.margin*2)
        if self._can_drag and self._title_button.status.pressing and self.settings.active:
            self._topleft += pygame.Vector2(_wuib._UIManager.mouse_rel)
        if self.status._absolute_hover and _wuib._UIManager.mouse_buttons[0] and self.settings.active:
            atleastone = False
            for element in _wuib._UIManager.root_elements:
                if element._root_index > self._root_index and not element._always_top:
                    element._root_index -= 1
                    atleastone = True
            if atleastone:
                self._root_index += 1
                
        self._super._update()

    def _on_close_click(self, btn):
        self.hide()
        if self._on_close:
            self._on_close(self)

    @property
    def title_button(self) -> Button:
        return self._title_button

    @property
    def close_button(self) -> Button:
        return self._close_button

    @property
    def inner_container(self) -> VCont:
        return self._elements_cont

    @property
    def line_separator(self) -> Line:
        return self._line_separator
