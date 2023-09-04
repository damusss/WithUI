import pygame

from . import _base as _wuib


class Label(_wuib._Element):
    def _on_init(self):
        self._text: str = ""
        self._inner_anchor: str = "center"
        self._inner_surf = None
        self._inner_rect = None
        self.set(has_background=False, has_outline=False)

    def _on_set(self, **kwargs):
        if "inner_anchor" in kwargs:
            self._inner_anchor = kwargs["inner_anchor"]
        if "text" in kwargs:
            self._text = str(kwargs["text"])
            self._refresh_text()

    def _on_font_change(self):
        if not self._text:
            return
        self._refresh_text()

    def _on_draw(self):
        if self._inner_surf:
            _wuib._anchor_inner(self._inner_anchor, self._rect,
                                self._inner_rect, self.settings.padding)
            self._surface.blit(
                self._inner_surf, self._inner_rect.topleft-self._real_topleft)

    def _refresh_text(self):
        self._inner_surf = self.settings.font.render(
            self._text, self.settings.font_antialas, self.settings.text_color,  wraplength=self.settings.width if not self.settings.auto_resize_h else 0)
        self._inner_rect = self._inner_surf.get_rect()
        self._set_h(self._inner_rect.height+self.settings.padding*2)
        self._set_w(self._inner_rect.width+self.settings.padding*2)

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value):
        self.text = str(value)
        self._refresh_text()


class Entryline(_wuib._Element):
    def _on_init(self):
        self._text = ""
        self._inner_surf = self._inner_rect = None
        self._cursor = 0
        self._blink_time = 400
        self._show_cursor = True
        self._focused = False
        self._cursor_width = 2
        self._last_blink = 0
        self._text_x = 0
        self._cut_width = 0
        self._last_action = None
        self._action_time = 0
        self._action_cooldown = 40
        self._start_action = 0
        self._wait_cooldown = 800
        self._selecting = False
        self._sel_start = 0
        self._sel_end = 0
        self._can_be_empty = False
        self._placeholder = "Insert text..."
        self._on_focus = self._on_change = self._on_copy = self._on_paste = None
        self.set(text="")

    def _on_set(self, **kwargs):
        if "text" in kwargs:
            self._text = str(kwargs["text"])
            if self._text: self._cursor = len(self._text)
            self._inner_surf = self.settings.font.render(
                self._text, self.settings.font_antialas, self.settings.text_color)
        if "cursor_width" in kwargs:
            self._cursor_width = kwargs["cursor_width"]
        if "blink_time" in kwargs:
            self._blink_time = kwargs["blink_time"]
        if "enable_empty" in kwargs:
            self._can_be_empty = kwargs["enable_empty"]
        if "placeholder" in kwargs:
            self._placeholder = str(kwargs["placeholder"])
        if "focused" in kwargs:
            self.focused = kwargs["focused"]
        if "on_focus" in kwargs:
            self._on_focus = kwargs["on_focus"]
        if "on_change" in kwargs:
            self._on_change = kwargs["on_change"]
        if "on_copy" in kwargs:
            self._on_copy = kwargs["on_copy"]
        if "on_paste" in kwargs:
            self._on_paste = kwargs["on_paste"]

    def _on_font_change(self):
        if not self._text:
            return
        self._inner_surf = self.settings.font.render(
            self._text, self.settings.font_antialas, self.settings.text_color)

    def _on_draw(self):
        if self._inner_surf:
            cy = self.settings.height//2 - \
                (ish := self._inner_surf.get_height())//2
            if self._text and self._selecting and self._sel_start != self._sel_end:
                sel_s, sel_e = self._sel_order()
                sel_s_cw, sel_e_cw = self._sel_cut_w(sel_s, sel_e)
                pygame.draw.rect(self._surface, self.settings.inner_color, (
                    self._text_x+sel_s_cw +
                    self.settings.padding, cy, (sel_e_cw-sel_s_cw), ish
                ))
            self._surface.blit(self._inner_surf, (
                self._text_x+self.settings.padding,
                cy
            ))
            if self._focused and self._show_cursor:
                pygame.draw.rect(self._surface, self.settings.text_color, (
                    self._text_x+self._cut_width +
                    self.settings.padding, cy, self._cursor_width, ish
                ))

    def _update(self):
        if self._inner_surf:
            self._set_h(self._inner_surf.get_height()+self.settings.padding*2)
            
        self._pre_update()
        if not self.settings.active: return
        
        previous_text = self._text
        if self._focused:
            for event in _wuib._UIManager.frame_events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        if _wuib._UIManager.keys[pygame.K_LCTRL]:
                            self._copy()
                            continue
                    if event.key == pygame.K_v:
                        if _wuib._UIManager.keys[pygame.K_LCTRL]:
                            self._paste()
                            continue
                    if event.key == pygame.K_LCTRL:
                        self._selecting = True
                        self._sel_start = self._sel_end = self._cursor
                    elif event.key == pygame.K_ESCAPE:
                        self._char_escape()
                    elif event.key == pygame.K_LEFT:
                        self._char_left()
                        self._start_action = _wuib._UIManager.ticks
                    elif event.key == pygame.K_RIGHT:
                        self._char_right()
                        self._start_action = _wuib._UIManager.ticks
                    elif event.key == pygame.K_DELETE:
                        self._char_delete()
                        self._start_action = _wuib._UIManager.ticks
                    elif event.key == pygame.K_BACKSPACE:
                        self._char_backspace()
                        self._start_action = _wuib._UIManager.ticks
                    elif event.unicode:
                        self._char_unicode(event.unicode)
                        self._start_action = _wuib._UIManager.ticks
                if event.type == pygame.KEYUP:
                    self._last_action = None

            if _wuib._UIManager.mouse_buttons[0]:
                if not self.status.hovering:
                    self._focused = False
                    self._last_action = None
                    if self._on_focus:
                        self._on_focus(self)
                self._selecting = False
                self._sel_start = self._sel_end = 0

            if self._last_action:
                if _wuib._UIManager.ticks - self._start_action >= self._wait_cooldown:
                    if _wuib._UIManager.ticks - self._action_time >= self._action_cooldown:
                        if self._last_action == pygame.K_LEFT:
                            self._char_left()
                        elif self._last_action == pygame.K_RIGHT:
                            self._char_right()
                        elif self._last_action == pygame.K_BACKSPACE:
                            self._char_backspace()
                        elif self._last_action == pygame.K_DELETE:
                            self._char_delete()
                        elif (char := pygame.key.name(self._last_action)):
                            self._char_unicode(char)

        else:
            if not self._text and not self._can_be_empty:
                self._text = self._placeholder
                self._cursor = len(self._text)
            if self.status.pressing:
                self._focused = True
                if self._on_focus:
                    self._on_focus(self)

        if self._text:
            if self._cursor < 0:
                self._cursor = 0
            if self._cursor >= len(self._text)+1:
                self._cursor = len(self._text)
            cut_text = self._text[:self._cursor]
            self._cut_width = self.settings.font.size(cut_text)[0]
            if self._cut_width > self.settings.width+self.settings.padding*2:
                self._text_x = -(self._cut_width -
                                 (self.settings.width-self.settings.padding*3))
            else:
                self._text_x = 0
        else:
            self._text_x = 0
            self._cursor = 0
            self._cut_width = 0

        if self._text != previous_text:
            self._inner_surf = self.settings.font.render(
                self._text, self.settings.font_antialas, self.settings.text_color)
            
        self._post_update()

        if _wuib._UIManager.ticks - self._last_blink >= self._blink_time:
            self._show_cursor = not self._show_cursor
            self._last_blink = _wuib._UIManager.ticks
        if self._last_action:
            self._show_cursor = True

    def _sel_order(self):
        if self._sel_end < self._sel_start:
            return self._sel_end, self._sel_start
        return self._sel_start, self._sel_end

    def _sel_cut_w(self, sel_s, sel_e):
        return self.settings.font.size(self._text[:sel_s])[0], self.settings.font.size(self._text[:sel_e])[0]

    def _remove_selection(self):
        if not self._text or not self._selecting or self._sel_start == self._sel_end:
            return
        sel_s, sel_e = self._sel_order()
        sel_str = self._text[sel_s:sel_e]
        self._text = self._text.replace(sel_str, "")
        self._cursor = sel_s
        self._selecting = False
        self._sel_start = self._sel_end = 0

    def _copy(self):
        if not self._text or not self._selecting and self._sel_start != self._sel_end:
            return
        sel_s, sel_e = self._sel_order()
        copy_str = self._text[sel_s:sel_e]
        pygame.scrap.put_text(copy_str)
        if self._on_copy:
            self._on_copy(self)

    def _paste(self):
        self._remove_selection()
        paste_str = pygame.scrap.get_text()
        self._add_text(paste_str)
        if self._on_paste:
            self._on_paste(self)

    def _add_text(self, text_str):
        if not text_str:
            return
        if self._text:
            if self._cursor == 0:
                self._text = text_str+self._text
                self._cursor = len(text_str)
            elif self._cursor == len(self._text):
                self._text += text_str
                self._cursor += len(text_str)
            else:
                left, right = self._text[0:self._cursor], self._text[self._cursor::]
                self._text = left+text_str+right
                self._cursor += len(text_str)
        else:
            self._text = text_str
            self._cursor = len(text_str)
        if self._on_change:
            self._on_change(self)

    def _char_escape(self):
        self.unfocus()
        if self._on_focus:
            self._on_focus(self)

    def _char_unicode(self, char):
        self._remove_selection()
        self._add_text(char)
        self._last_action = pygame.key.key_code(char)
        self._action_time = _wuib._UIManager.ticks

    def _char_backspace(self):
        if not self._text:
            return
        if self._selecting:
            self._remove_selection()
            return
        if self._cursor == len(self._text):
            self._text = self._text[:-1]
            self._cursor -= 1
        else:
            left, right = self._text[0:self._cursor], self._text[self._cursor::]
            self._text = left[:-1]+right
            self._cursor -= 1
        if self._on_change:
            self._on_change(self)
        self._last_action = pygame.K_BACKSPACE
        self._action_time = _wuib._UIManager.ticks

    def _char_delete(self):
        if not self._text:
            return
        if self._selecting:
            self._remove_selection()
            return
        if self._cursor < len(self._text):
            if self._cursor == 0:
                self._text = self._text[1:]
            else:
                left, right = self._text[0:self._cursor], self._text[self._cursor::]
                self._text = left+right[1:]
        if self._on_change:
            self._on_change(self)
        self._last_action = pygame.K_DELETE
        self._action_time = _wuib._UIManager.ticks

    def _char_left(self):
        if not self._text:
            return
        if self._cursor > 0:
            self._cursor -= 1
        self._last_action = pygame.K_LEFT
        self._action_time = _wuib._UIManager.ticks
        if self._selecting:
            self._sel_end = self._cursor

    def _char_right(self):
        if not self._text:
            return
        if self._cursor < len(self._text):
            self._cursor += 1
        self._last_action = pygame.K_RIGHT
        self._action_time = _wuib._UIManager.ticks
        if self._selecting:
            self._sel_end = self._cursor

    def focus(self):
        self._focused = True

    def unfocus(self):
        self._focused = False
        self._selecting = False
        self._sel_start = self._sel_end = 0

    def add_at_cursor(self, text: str):
        self._add_text(text)

    def remove_selection(self):
        self._remove_selection()

    def get_selection(self) -> str | None:
        if not self._selecting or not self._text or self._sel_start == self._sel_end:
            return None
        sel_s, sel_e = self._sel_order()
        sel_str = self._text[sel_s:sel_e]
        return sel_str

    def select_all(self):
        if not self._text:
            return
        self._selecting = True
        self._sel_start = 0
        self._sel_end = len(self._text)

    def select(self, cursor_start: int, cursor_end: int):
        if not self._text or cursor_start == cursor_end:
            return
        self._selecting = True
        self._sel_start = pygame.math.clamp(
            int(cursor_start), 0, len(self._text))
        self._sel_end = pygame.math.clamp(int(cursor_end), 0, len(self._text))

    def place_cursor(self, index: int):
        if not self._text:
            return
        self._cursor = pygame.math.clamp(int(index), 0, len(self._text))

    def is_selecting(self) -> bool:
        return self._selecting

    def stop_selecting(self):
        self._selecting = False
        self._sel_start = self._sel_end = 0

    @property
    def focused(self) -> bool:
        return self._focused

    @focused.setter
    def focused(self, value):
        if value:
            self.focus()
        else:
            self.unfocus()

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value):
        self._text = str(value)
        if self._text: self._cursor = len(self._text)
        self._inner_surf = self.settings.font.render(
            self._text, self.settings.font_antialas, self.settings.text_color)
