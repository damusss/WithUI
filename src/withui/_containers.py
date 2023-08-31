import pygame

from . import _base as _wuib


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
