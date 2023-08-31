[<- back to elements](../elements.md)

# Slider

A multidirectional slider element.

Available directions:
- horizontal
- vertical

The value goes from 0 to 1, the value_percent goes from 0-100

You can get the value_percent with the `value_percent` property

When the slider moves the `on_move` callback is called.

You can modify this settings:
- slider_size (width or height depends on direction)
- direction
- value
- value_percent
- handle_size
- on_move - callback

The handle is available as the `handle` attribute.