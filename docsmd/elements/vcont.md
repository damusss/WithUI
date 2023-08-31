[<- back to elements](../elements.md)

# VCont

Container that organizes the children elements vertically.

![VCont Example](../images/vcont.png)

The horizontal anchor of elements is decided by their `parent_anchor` setting.

Scrolling is enabled by the `can_scroll_h` and `can_scroll_v` settings.

If `center_elements` is enabled, the container will try to center the elements vertically (and horizontally if the element has no parent anchor).

`auto_resize_h` and `auto_resize_v` among with min and max width and height decide whether the container should adapt to its children size.
