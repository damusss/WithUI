import pygame

from . import _withuibase as _wuib

DefaultSettings = _wuib._Settings
EmptyElement = _wuib._Element


class Button(_wuib._Element):
    def _on_init(self):
        self.text: str = ""
        self.inner_anchor: str = "center"
        self._inner_surf = None
        self._inner_rect = None

    def _on_set(self, **kwargs):
        if "inner_anchor" in kwargs:
            self.inner_anchor = kwargs["inner_anchor"]
        if "text" in kwargs:
            self.text = str(kwargs["text"])
            self._inner_surf = self.settings.font.render(
                self.text, self.settings.font_antialas, self.settings.text_color)
            self._inner_rect = self._inner_surf.get_rect()
            self._set_h(self._inner_rect.height+self.settings.padding*2)
            self._set_w(self._inner_rect.width+self.settings.padding*2)
        elif "surface" in kwargs:
            self.text = ""
            self._inner_surf = kwargs["surface"]
            if self._inner_surf:
                self._inner_rect = self._inner_surf.get_rect()
                self._set_h(self._inner_rect.height+self.settings.padding*2)
                self._set_w(self._inner_rect.width+self.settings.padding*2)

    def _on_draw(self):
        if self._inner_surf:
            _wuib._anchor_inner(self.inner_anchor, self._rect,
                                self._inner_rect, self.settings.padding)
            self._surface.blit(
                self._inner_surf, self._inner_rect.topleft-self._real_topleft)


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


class Label(_wuib._Element):
    def _on_init(self):
        self.text: str = ""
        self.inner_anchor: str = "center"
        self._inner_surf = None
        self._inner_rect = None
        self.set(has_background=False, has_outline=False)

    def _on_set(self, **kwargs):
        if "inner_anchor" in kwargs:
            self.inner_anchor = kwargs["inner_anchor"]
        if "text" in kwargs:
            self.text = str(kwargs["text"])
            self._inner_surf = self.settings.font.render(
                self.text, self.settings.font_antialas, self.settings.text_color)
            self._inner_rect = self._inner_surf.get_rect()
            self._set_h(self._inner_rect.height+self.settings.padding*2)
            self._set_w(self._inner_rect.width+self.settings.padding*2)

    def _on_draw(self):
        if self._inner_surf:
            _wuib._anchor_inner(self.inner_anchor, self._rect,
                                self._inner_rect, self.settings.padding)
            self._surface.blit(
                self._inner_surf, self._inner_rect.topleft-self._real_topleft)


class Entryline(_wuib._Element):
    def _on_init(self):
        self._text = ""
        self._inner_surf = None
        self._inner_rect = None
        self._cursor = 0
        self._blink_time = 400
        self._show_cursor = True
        self._focused = False
        self._cursor_width = 2
        self._last_blink = 0
        self._text_x = 0
        self._cut_width = 0
        self._last_action = None
        self._action_time = None
        self._action_cooldown = 80
        self._start_action = 0
        self._wait_cooldown = 800
        self._selecting = False
        self._sel_start = 0
        self._sel_end = 0

    def _on_set(self, **kwargs):
        if "text" in kwargs:
            self._text = kwargs["text"]
        if "cursor_width" in kwargs:
            self._cursor_width = kwargs["cursor_width"]
        if "blink_time" in kwargs:
            self._blink_time = kwargs["blink_time"]

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
            self.settings.height = self._inner_surf.get_height()+self.settings.padding*2
        self._pre_update()
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
            if not self._text:
                self._text = "Insert text..."
                self._cursor = len(self._text)
            if self.status.pressing:
                self._focused = True

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
        sel_s_txt = self._text[:sel_s]
        sel_s_cw = self.settings.font.size(sel_s_txt)[0]
        sel_e_txt = self._text[:sel_e]
        sel_e_cw = self.settings.font.size(sel_e_txt)[0]
        return sel_s_cw, sel_e_cw

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

    def _paste(self):
        self._remove_selection()
        paste_str = pygame.scrap.get_text()
        if not paste_str:
            return
        if self._text:
            if self._cursor == 0:
                self._text = paste_str+self._text
                self._cursor = len(paste_str)
            elif self._cursor == len(self._text):
                self._text += paste_str
                self._cursor += len(paste_str)
            else:
                left, right = self._text[0:self._cursor], self._text[self._cursor::]
                self._text = left+paste_str+right
                self._cursor += len(paste_str)
        else:
            self._text = paste_str
            self._cursor = len(paste_str)

    def _char_escape(self):
        self.unfocus()

    def _char_unicode(self, char):
        self._remove_selection()
        if self._text:
            if self._cursor == 0:
                self._text = char + self._text
                self._cursor = 1
            elif self._cursor == len(self._text):
                self._text += char
                self._cursor += 1
            else:
                left, right = self._text[0:self._cursor], self._text[self._cursor::]
                self._text = left+char+right
                self._cursor += 1
        else:
            self._text = char
            self._cursor = 1
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

    @property
    def focused(self):
        return self._focused

    @focused.setter
    def focused(self, value):
        if value:
            self.focus()
        else:
            self.unfocus()

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value


class Image(_wuib._Element):
    def _on_init(self):
        self.inner_anchor: str = "center"
        self._inner_surf = None
        self._inner_rect = None
        self.set(has_background=False, has_outline=False,
                 show_hover=False, show_press=False)

    def _on_set(self, **kwargs):
        if "inner_anchor" in kwargs:
            self.inner_anchor = kwargs["inner_anchor"]
        if "surface" in kwargs:
            self._inner_surf = kwargs["surface"]
            if self._inner_surf:
                self._inner_rect = self._inner_surf.get_rect()
                self._set_h(self._inner_rect.height+self.settings.padding*2)
                self._set_w(self._inner_rect.width+self.settings.padding*2)

    def _on_draw(self):
        if self._inner_surf:
            _wuib._anchor_inner(self.inner_anchor, self._rect,
                                self._inner_rect, self.settings.padding)
            self._surface.blit(
                self._inner_surf, self._inner_rect.topleft-self._real_topleft)


class Separator(_wuib._Element):
    def _on_init(self):
        self.set(**INVISIBLE, **STATIC)


class Line(_wuib._Element):
    def _on_init(self):
        self.set(**STATIC, height=2)

    def _on_draw(self):
        self.settings.background_color = self.settings.outline_color


class ProgressBar(_wuib._Element):
    def _on_init(self):
        self.set(show_press=False, show_hover=False,
                 padding=0, has_dark_bg=True)
        self.min_value: _wuib._Number = 0
        self.max_value: _wuib._Number = 100
        self.value: _wuib._Number = 50
        self.value_percent: _wuib._Number = None
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
        self.set(**STATIC, has_dark_bg=True,
                 height=_wuib._SLIDER_SIZE, margin=_wuib._HANDLE_SIZE//2)
        self._direction = "horizontal"
        self.handle = Button(free_position=pygame.Vector2(0, 0))
        self._handle_pos = 0
        self._handle_size = _wuib._HANDLE_SIZE
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
                self.settings.height = _wuib._SLIDER_SIZE
            else:
                self.settings.width = _wuib._SLIDER_SIZE
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

        self._post_update()
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

    @property
    def value_percent(self):
        return self.value*100


class VCont(_wuib._Element):
    def _on_enter(self):
        self._v_scrollbar._kill() if self._v_scrollbar else None
        self._h_scrollbar._kill() if self._h_scrollbar else None
        self._v_scrollbar = _wuib._VScrollbar()
        self._h_scrollbar = _wuib._HScrollbar()

    def _update(self):
        self._pre_update()
        last: _wuib._Element = None
        tot_h = longest = 0
        self._scroll_margin_h = _wuib._SCROLLBAR_SIZE if self._v_scrollbar.settings.visible and self._v_scrollbar.settings.active else 0
        self._scroll_margin_v = _wuib._SCROLLBAR_SIZE if self._h_scrollbar.settings.visible and self._h_scrollbar.settings.active else 0
        for child in self._children:
            if child.settings.draw_top or child.settings.free_position or not child.settings.visible or not child.settings.active:
                continue
            if last:
                topleft = last._topleft.copy()
                topleft.y += last.settings.height + \
                    ((child.settings.margin+last.settings.margin)/2)
                tot_h += ((child.settings.margin+last.settings.margin)/2) + \
                    child.settings.height
            else:
                topleft = pygame.Vector2()
                topleft.y += child.settings.margin
                tot_h += child.settings.margin*2+child.settings.height

            if not child.settings.parent_anchor and self.settings.center_elements:
                child.settings.parent_anchor = "center"
            if child.settings.parent_anchor:
                match child.settings.parent_anchor:
                    case "left":
                        topleft.x = child.settings.margin
                    case "right":
                        topleft.x = max(self._tot_w, self.settings.width) - \
                            child.settings.margin-child.settings.width-self._scroll_margin_h
                    case "center":
                        topleft.x = (max(self._tot_w, self.settings.width) -
                                     self._scroll_margin_h)//2 - (child.settings.width)//2
                    case _:
                        topleft.x = child.settings.margin
            else:
                topleft.x = child.settings.margin

            child._topleft = topleft
            last = child

            if child.settings.width + child.settings.margin * 2 + self._scroll_margin_h > longest:
                longest = child.settings.width + child.settings.margin * 2 + self._scroll_margin_h

        self._set_h(tot_h)
        self._set_w(longest)

        if self.settings.center_elements and self.settings.height > tot_h:
            for child in self._children:
                child._topleft.y += (self.settings.height -
                                     self._scroll_margin_v)//2-tot_h//2
        self._tot_h = tot_h
        self._tot_w = longest
        self._post_update()

    def _on_init(self):
        self.set(has_dark_bg=True, show_hover=False, show_press=False)
        self._tot_w, self._tot_h = self.settings.width, self.settings.height
        self._scroll_margin_h = self._scroll_margin_v = 0
        self._v_scrollbar = self._h_scrollbar = None


class HCont(_wuib._Element):
    def _on_enter(self):
        self._v_scrollbar._kill() if self._v_scrollbar else None
        self._h_scrollbar._kill() if self._h_scrollbar else None
        self._v_scrollbar = _wuib._VScrollbar()
        self._h_scrollbar = _wuib._HScrollbar()

    def _update(self):
        self._pre_update()
        last: _wuib._Element = None
        tot_w = tallest = 0
        self._scroll_margin_h = _wuib._SCROLLBAR_SIZE if self._v_scrollbar.settings.visible and self._v_scrollbar.settings.active else 0
        self._scroll_margin_v = _wuib._SCROLLBAR_SIZE if self._h_scrollbar.settings.visible and self._h_scrollbar.settings.active else 0
        for child in self._children:
            if child.settings.draw_top or child.settings.free_position or not child.settings.visible or not child.settings.active:
                continue
            if last:
                topleft = last._topleft.copy()
                topleft.x += last.settings.width + \
                    ((child.settings.margin+last.settings.margin)/2)
                tot_w += ((child.settings.margin+last.settings.margin)/2) + \
                    child.settings.width
            else:
                topleft = pygame.Vector2()
                topleft.x += child.settings.margin
                tot_w += child.settings.margin*2+child.settings.width

            if not child.settings.parent_anchor and self.settings.center_elements:
                child.settings.parent_anchor = "center"
            if child.settings.parent_anchor:
                match child.settings.parent_anchor:
                    case "top":
                        topleft.y = child.settings.margin
                    case "bottom":
                        topleft.y = max(self._tot_h, self.settings.height) - \
                            child.settings.margin-child.settings.height-self._scroll_margin_v
                    case "center":
                        topleft.y = (max(self._tot_h, self.settings.height) -
                                     self._scroll_margin_v)//2 - (child.settings.height)//2
                    case _:
                        topleft.y = child.settings.margin
            else:
                topleft.y = child.settings.margin

            child._topleft = topleft
            last = child

            if child.settings.height + child.settings.margin * 2 + self._scroll_margin_v > tallest:
                tallest = child.settings.height + child.settings.margin * 2 + self._scroll_margin_v

        self._set_h(tallest)
        self._set_w(tot_w)

        if self.settings.center_elements and self.settings.width > tot_w:
            for child in self._children:
                child._topleft.x += (self.settings.width -
                                     self._scroll_margin_h)//2-tot_w//2
        self._tot_w = tot_w
        self._tot_h = tallest
        self._post_update()

    def _on_init(self):
        self.set(has_dark_bg=True, can_hover=False, can_press=False)
        self._tot_w, self._tot_h = self.settings.width, self.settings.height
        self._scroll_margin_h = self._scroll_margin_v = 0
        self._v_scrollbar = self._h_scrollbar = None


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
    def current_surface(self) -> pygame.Surface:
        return self.image._inner_surf


class SelectionList(VCont):
    def _on_init(self):
        super()._on_init()
        self._option_buttons: list["Button"] = []
        self._multi_select = False
        self.set(**STATIC, **SCROLLABLE, width=100)

    def _on_set(self, **kwargs):
        if "options" in kwargs:
            previously_selected = [btn.text for btn in self._option_buttons]
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
            if self.settings.on_select:
                self.settings.on_select(
                    [button.text for button in self._option_buttons if button.status.selected])
        else:
            for btn in self._option_buttons:
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
        self._down_arrow_string = "v"  # ▼
        self._up_arrow_string = "^"  # ▲
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
        self.set(**STATIC, **INVISIBLE, menu_open=False, width=100)

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

    def get_selected(self):
        return self._selected_button.text

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
    def menu_open(self):
        return self._options_cont.settings.visible

    @menu_open.setter
    def menu_open(self, value):
        if value:
            self.open_menu()
        else:
            self.close_menu()


class Window(VCont):
    def _on_init(self):
        self._super = super()
        self._super._on_init()
        if self not in _wuib._UIManager.tree_elements:
            raise _wuib._WithUIException(
                f"Window elements should be declared at the top and not have any parent")
        self._finished_instantiating = False
        self.__enter__()
        self._title_cont = HCont(**INVISIBLE)
        self._title_cont.__enter__()
        self._title_button = Button(
            text="Wui Window", inner_anchor="midleft", margin=0)
        self._close_button = Button(
            text="X", margin=0, on_click=self._on_close_click)
        self._title_cont.__exit__()
        self._line_separator = Line(
            height=self.settings.outline_width, width_percent=100)
        self._elements_cont = VCont(**INVISIBLE, margin=0, **SCROLLABLE)
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
        if self._can_drag and self._title_button.status.pressing:
            self._topleft += pygame.Vector2(_wuib._UIManager.mouse_rel)
        if self.status.pressing:
            atleastone = False
            for element in _wuib._UIManager.tree_elements:
                if element._tree_index > self._tree_index:
                    element._tree_index -= 1
                    atleastone = True
            if atleastone:
                self._tree_index += 1
        self._super._update()

    def _on_close_click(self, btn):
        self.hide()
        if self._on_close:
            self._on_close(self)

    @property
    def title_button(self):
        return self._title_button

    @property
    def close_button(self):
        return self._close_button

    @property
    def inner_container(self):
        return self._elements_cont

    @property
    def line_separator(self):
        return self._line_separator


class UserSettings:
    settings: dict[str, dict[str, _wuib.typing.Any]] = {}

    @classmethod
    def add(cls, name: str, **kwargs: dict[str, _wuib.typing.Any]) -> dict[str, _wuib.typing.Any]:
        cls.settings[name] = kwargs
        return kwargs

    @classmethod
    def get(cls, name: str) -> dict[str, _wuib.typing.Any]:
        return cls.settings[name]


class Themes:
    PURPLE = {
        'background_color': (65, 0, 117),
        'hover_color': (101, 0, 171),
        "dark_bg_color": (31, 0, 61),
        "click_color": (45, 0, 75),
        "outline_color": (67, 0, 137),
        "inner_color": "purple",
        "text_color": "white",
    }
    GREEN = {
        "background_color": (0, 78, 18),
        "dark_bg_color": (0, 35, 8),
        "hover_color": (0, 115, 35),
        "click_color": (0, 58, 14),
        "outline_color": (0, 95, 20),
        "inner_color": (0, 255, 155),
        "text_color": "white",
    }
    BLUE = {
        "dark_bg_color": (0, 10, 60),
        "background_color": (0, 30, 125),
        "hover_color": (0, 48, 170),
        "click_color": (0, 20, 105),
        "outline_color": (0, 50, 145),
        "inner_color": (0, 100, 255),
        "text_color": "white",
    }
    RED = {
        "dark_bg_color": (55, 0, 0),
        "background_color": (115, 0, 0),
        "hover_color": (155, 0, 0),
        "click_color": (100, 0, 0),
        "outline_color": (135, 0, 0),
        "inner_color": (255, 0, 0),
        "text_color": "white",
    }
    DARK = {
        "dark_bg_color": (15, 15, 15),
        "background_color": (30, 30, 30),
        "hover_color": (40, 40, 40),
        "click_color": (22, 22, 22),
        "outline_color": (50, 50, 50),
        "inner_color": (0, 100, 200),
        "text_color": "white",
    }

    LIGHT = {
        "dark_bg_color": (245, 245, 245),
        "background_color": (255, 255, 255),
        "hover_color": (242, 242, 242),
        "click_color": (230, 230, 230),
        "outline_color": (230, 230, 230),
        "inner_color": (0, 150, 255),
        "text_color": "black",
    }

    @classmethod
    def set_default(cls, builtin_color_theme_or_name):
        theme = None
        if isinstance(builtin_color_theme_or_name, str):
            themes = {"red": cls.RED, "blue": cls.BLUE, "green": cls.GREEN, "purple": cls.PURPLE, "dark": cls.DARK,
                      "light": cls.LIGHT, "black": cls.DARK, "white": cls.LIGHT}
            if builtin_color_theme_or_name.lower() not in themes:
                raise _wuib._WithUIException(
                    f"There isn't any builtin theme with name '{builtin_color_theme_or_name}'. Available are red, blue, green, purple, dark, light")
            theme = themes[builtin_color_theme_or_name.lower()]
        else:
            theme = builtin_color_theme_or_name
            for col in ["dark_bg_col", "background_color", "hover_color",
                        "click_color", "outline_color", "inner_color", "text_color", ]:
                if col not in theme:
                    raise _wuib._WithUIException(
                        f"The theme dict provided must contain the '{col}' key")
        _wuib._Settings.dark_bg_color = theme["dark_bg_color"]
        _wuib._Settings.background_color = theme["background_color"]
        _wuib._Settings.hover_color = theme["hover_color"]
        _wuib._Settings.click_color = theme["click_color"]
        _wuib._Settings.outline_color = theme["outline_color"]
        _wuib._Settings.inner_color = theme["inner_color"]
        _wuib._Settings.text_color = theme["text_color"]


INVISIBLE: dict[str, bool] = {
    "has_background": False,
    "has_outline": False
}

SCROLLABLE: dict[str, bool] = {
    "can_scroll_h": True,
    "can_scroll_v": True
}

STATIC: dict[str, bool] = {
    "can_press": False,
    "can_hover": False,
    "can_select": False,
}

MODERN_DOWN_ARROW = "▼"
MODERN_UP_ARROW = "▲"


def settings_help(element: str | type[_wuib._Element] | _wuib._Element = "Element", setting: str = None) -> str | dict[str, str]:
    element_name = element
    if isinstance(element_name, type):
        element_name = element.__name__
    elif isinstance(element_name, _wuib._Element):
        element_name = element.__class__.__name__
    if element_name in _wuib._SETTINGS_HELP:
        settings = _wuib._SETTINGS_HELP[element_name].copy()
        if element_name != "Element":
            settings.update(_wuib._SETTINGS_HELP["Element"])
        if setting is not None:
            if setting in settings:
                return settings[setting]
            else:
                raise _wuib._WithUIException(
                    f"Element '{element_name}' has no setting '{setting}'")
        else:
            return settings
    else:
        raise _wuib._WithUIException(
            f"No element exist with name '{element_name}'. Available are: '{_wuib._SETTINGS_HELP.keys()}'")


def pretty_print(json_like_object: _wuib.typing.Any):
    if isinstance(json_like_object, str):
        print(json_like_object)
        return
    formatted = _wuib.json.dumps(json_like_object, indent=2)
    print(formatted)


def pretty_format(json_like_object: _wuib.typing.Any) -> str:
    if isinstance(json_like_object, str):
        return json_like_object
    formatted = _wuib.json.dumps(json_like_object, indent=2)
    return formatted


def register_event(event: pygame.event.Event):
    if _wuib._UIManager.frame_ended:
        _wuib._UIManager.frame_ended = False
        _wuib._UIManager.frame_events = []
    _wuib._UIManager.frame_events.append(event)


def update_ui():
    if _wuib._UIManager.frame_ended:
        _wuib._UIManager.frame_ended = False
        _wuib._UIManager.frame_events = []
    _wuib._UIManager.update()
    for element in _wuib._UIManager.tree_elements:
        element._update()
    _wuib._UIManager.frame_ended = True


def draw_ui(surface: pygame.Surface):
    for element in sorted(_wuib._UIManager.tree_elements, key=lambda tel: tel._tree_index):
        element._draw(surface)
        for el in _wuib._UIManager.top_elements:
            if el._tree_element._tree_index == element._tree_index:
                el._draw(surface)
