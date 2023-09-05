import pygame

from . import _base as _wuib
from ._buttons import Button
from ._containers import HCont, VCont


class SelectionList(VCont):
    def _on_init(self):
        super()._on_init()
        self._option_buttons: list["Button"] = []
        self._multi_select = False
        self.set(can_hover=False, can_press=False, can_select=False,
                 can_scroll_h=True, can_scroll_v=True, width=100)

    def _on_set(self, **kwargs):
        if "options" in kwargs:
            previously_selected = [btn.text for btn in self._option_buttons if btn.status.selected]
            for btn in self._option_buttons:
                btn._kill()
            self.__enter__()
            for option in kwargs["options"]:
                btn = Button(text=option, width_percent=100, has_outline=False,
                             can_select=True, on_select=self._on_select, margin=int(self.settings.margin//2), border_radius=0)
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
            for opt in self._option_buttons:
                opt._set_dirty()
            if self.settings.on_select:
                self.settings.on_select(
                    [button.text for button in self._option_buttons if button.status.selected])
        else:
            for btn in self._option_buttons:
                btn._set_dirty()
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

    def apply_settings_to_options(self, **kwargs):
        for btn in self._option_buttons:
            btn.set(**kwargs)


class DropMenu(HCont):
    def _on_init(self):
        self._super = super()
        self._super._on_init()
        self._down_arrow_string = " v "  # ▼
        self._up_arrow_string = " ^ "  # ▲
        self.__enter__()
        self._selected_button = Button(
            text="", on_click=self._selected_click, margin=1)
        self._arrow_button = Button(
            text=self._down_arrow_string, on_click=self._arrow_click, margin=1)
        self.__exit__()
        w = max(self.settings.width-self._arrow_button.settings.width -
                self._selected_button.settings.margin*3, 1)
        self._selected_button.set(width=w, min_width=w, max_width=w)
        self._options_cont = VCont(draw_top=True)
        self._option_buttons: list[Button] = []
        self._direction = "down"
        self.set(can_hover=False, can_press=False, can_select=False,
                 has_background=False, has_outline=False, menu_open=False, width=100)

    def _on_set(self, **kwargs):
        if "selected_option" in kwargs:
            self._selected_button.set(text=kwargs["selected_option"])
        if "options" in kwargs:
            for btn in self._option_buttons:
                btn._kill()
            self._options_cont.__enter__()
            for option in kwargs["options"]:
                btn = Button(text=option, has_outline=False,
                             on_click=self._option_click, width_percent=100, margin=int(self.settings.margin//2), border_radius=0)
                self._option_buttons.append(btn)
            self._options_cont.__exit__()
            if not self._selected_button.text and len(kwargs["options"]) > 0:
                self._selected_button.set(text=kwargs["options"][0])
        if "menu_open" in kwargs:
            if kwargs["menu_open"]:
                self.open_menu()
            else:
                self.close_menu()
        if "direction" in kwargs:
            self._direction = kwargs["direction"]
            self.toggle_menu()
            self.toggle_menu()
            if not kwargs["direction"] in ["down", "up"]:
                raise _wuib._WithUIException(
                    f"Only down and up directions are allowed for drop menus, not '{self._direction}'")
        if "down_arrow" in kwargs:
            self._down_arrow_string = kwargs["down_arrow"]
            self.toggle_menu()
            self.toggle_menu()
        if "up_arrow" in kwargs:
            self._up_arrow_string = kwargs["up_arrow"]
            self.toggle_menu()
            self.toggle_menu()

    def _option_click(self, btn):
        self._selected_button.set(text=btn.text)
        for opt in self._option_buttons:
            opt._set_dirty()
        self.close_menu()
        if self.settings.on_select:
            self.settings.on_select(btn.text)

    def _arrow_click(self, btn):
        self.toggle_menu()

    def _selected_click(self, btn):
        self.toggle_menu()

    def _update(self):
        self._super._update()
        if self._direction == "down":
            self._options_cont.settings.free_position = pygame.Vector2(
                self._topleft.x+self._selected_button.settings.margin, self._topleft.y+self.settings.height)
        else:
            self._options_cont.settings.free_position = pygame.Vector2(
                self._topleft.x+self._selected_button.settings.margin, self._topleft.y-self._options_cont.settings.height)
        self._options_cont.settings.width = self._options_cont.settings.min_width = self._options_cont.settings.max_width = max(
            self.settings.width-self._selected_button.settings.margin-self._arrow_button.settings.margin, 1)
        w = max(self.settings.width-self._arrow_button.settings.width -
                self._selected_button.settings.margin*3, 1)
        self._selected_button.settings.width = self._selected_button.settings.max_width = self._selected_button.settings.min_width = w
        self._arrow_button.settings.height = self._arrow_button.settings.min_height = self._arrow_button.settings.max_height = self._selected_button.settings.height

    def open_menu(self):
        self._options_cont.settings.visible = True
        self._arrow_button.set(
            text=self._up_arrow_string if self._direction == "down" else self._down_arrow_string)

    def close_menu(self):
        self._options_cont.settings.visible = False
        self._arrow_button.set(
            text=self._down_arrow_string if self._direction == "down" else self._up_arrow_string)

    def toggle_menu(self):
        self._options_cont.settings.visible = not self._options_cont.settings.visible
        self._arrow_button.set(text=(self._up_arrow_string if self._direction == "down" else self._down_arrow_string)
                               if self._options_cont.settings.visible
                               else (self._down_arrow_string if self._direction == "down" else self._up_arrow_string))

    def apply_settings_to_options(self, **kwargs):
        for btn in self._option_buttons:
            btn.set(**kwargs)

    @property
    def selected(self) -> str:
        return self._selected_button._text

    @selected.setter
    def selected(self, value):
        self._selected_button.set(text=value)

    @property
    def menu_open(self) -> bool:
        return self._options_cont.settings.visible

    @menu_open.setter
    def menu_open(self, value):
        if value:
            self.open_menu()
        else:
            self.close_menu()
