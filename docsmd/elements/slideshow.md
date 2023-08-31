[<- back to elements](../elements.md)

# Slideshow

## inherit HCont

A wrapper element that has an `Image` in the center and 2 arrow buttons at the sides. The image shows a surface and the buttons allow to go to the next or previous surface.

When the user change surface, the `on_select` callback is called and the current surface is passed.

The `surface` property will return the current surface.

You can use this settings:
- surfaces
- surface_index

`image`, `left_arrow` and `right_arrow` elements are available as attributes.