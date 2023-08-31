[<- back to elements](../elements.md)

# Entryline

Very featureful input box of a single line.
Also supports selection, copy/paste and some callbacks.

Customize it with the following settings:
- text
- cursor_width
- blink_time
- enable_empty
- placeholder
- focused
- on_focus - callback
- on_change - callback
- on_copy - call_back
- on_paste - callback

The text and the focused setting can be obtained/modified with the `text` and `focused` properties.

You can only select using CTRL and left or right arrows.

## focus(), unfocus()

Same as `entryline.focused = True` and `entryline.focused = False`

## add_at_cursor(text: str)

Add text where the cursor currently is

## remove_selection()

Delete what is currently selected

## get_selection() -> str | None

Return the text that is currently selected

## is_selecting() -> bool

Returm whether the user is selecting something

## stop_selecting()

Remove the selection without deleting the text

## select_all()

Select all the text

## select(cursor_start: int, cursor_end: int)

Select the text given the start and end index

## place_cursor(index: int)

Place the cursor at the given index