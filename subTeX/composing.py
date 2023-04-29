import sys
from .skeleton import unroll


def compose(actions, fonts, line, next_line):
    """
    Apply a list of actions to a line of text and return the resulting line.

    Args:
        actions: A list of actions to apply to the line. Each action is either a string
            representing the name of the action, or a tuple containing the name of the
            action and its arguments.
        fonts: A dictionary containing information about different fonts.
        line: The current line of text to apply the actions to.
        next_line: The next line of text, which may be used by some actions.

    Returns:
        The resulting line of text after applying all the actions.

    """

    a = 0
    while a < len(actions):
        a, line = call_action(actions, a, fonts, line, next_line)
    return line


def call_action(actions, a, fonts, line, next_line):
    action, *args = actions[a]
    return action(actions, a, fonts, line, next_line, *args)


def add_leading(line, next_line, leading=9999999):
    """Add `leading` points to the leading of the first line after `line`."""

    def next_line2(line2, leading2, height):
        if line2 is line:
            leading2 += leading
        return next_line(line2, leading2, height)

    return next_line2


def vskip(actions, a, fonts, line, next_line, leading):
    """Action: adds `vskip` points of leading to the next line generated."""
    alt_next_line = add_leading(line, next_line, leading)
    return call_action(actions, a + 1, fonts, line, alt_next_line)


def new_page(actions, a, fonts, line, next_line):
    """Action: moves the next generated line onto a new page."""
    if line is None:
        return a + 1, line

    def next_line2(line2, leading, height):
        if line2 is line:
            leading = 9999999
        return next_line(line2, leading, height)

    return call_action(actions, a + 1, fonts, line, next_line2)


def new_recto_page(actions, a, fonts, line, next_line):
    if line is None:
        return a + 1, line
    if line.column.id % 2:
        line = next_line(line, 9999999, 0)
    return new_page(actions, a, fonts, line, next_line)


def blank_line(actions, a, fonts, line, next_line, graphic):
    line2 = next_line(line, 2, 10)
    if line2.column is not line.column:
        line2 = next_line(line, 9999999, 0)
    return a + 1, line2


def section_break(actions, a, fonts, line, next_line, font_name, graphic):
    """Action: insert a section break.

    In the middle of a page, a section break is simply a blank line.
    But if the section break falls between pages, then it inserts a
    graphic to make clear that a new section is starting.

    """
    font = fonts[font_name]
    leading = font.leading
    height = font.height

    at_top = line is None
    a1 = a + 1
    if at_top:
        return a1, line

    at_bottom = a1 == len(actions)
    if at_bottom:
        return a1, line

    # Add a blank line.
    line2 = next_line(line, leading, height)

    if line2.column is not line.column:
        # Our attempt to add a blank line pushed us to the next page.
        # Instead, use the line for the graphic.
        line2.graphics.append(graphic)
        line3 = next_line(line2, leading, height)
        return a1, line3

    # See what the following content does after the blank line.
    a2, line3 = call_action(actions, a1, fonts, line2, next_line)
    lines = unroll(line2, line3)
    assert line2 is lines[0]
    if line2.column is lines[1].column:
        # A simple blank line works! The following content (at least its
        # first line) stayed here on the same page.
        return a2, line3

    # A blank line pushed the following content to the next page. Add a
    # separator graphic.
    line3 = next_line(line2, leading, height)
    line3.graphics.append(graphic)

    if line3.column is not line.column:
        # The separator landed on the next page! To avoid the extra
        # blank line at the bottom of the column, rebuild atop `line`,
        # and put a blank line after the separator instead.
        line2 = next_line(line, 9999999, height)
        line2.graphics.append(graphic)
        line3 = next_line(line2, leading, height)
        return a1, line3

    # Re-run the following content, forcing it on to the next page.
    a = add_leading(line3, next_line)
    return call_action(actions, a1, fonts, line3, a)


def centered_paragraph(actions, a, fonts, line, next_line, fonts_and_texts):
    """(Work-in-progress) Format text as a centered paragraph."""

    # Just like a ragged paragraph, but with different x's. TODO: can
    # probably be refectored to share more code; but can they shared
    # more code without making them both more complicated?
    leading = max(fonts[name].leading for name, text in fonts_and_texts)
    height = max(fonts[name].height for name, text in fonts_and_texts)

    # TODO: this is ugly, creating a throw-away line to learn the width
    # of the upcoming column. Maybe ask for lines as we need them,
    # instead?
    tmpline = next_line(line, leading, height)

    unwrapped_lines = _split_texts_into_lines(fonts_and_texts)
    wrapped_lines = _wrap_long_lines(fonts, unwrapped_lines,
                                     tmpline.column.width)

    for tuples in wrapped_lines:
        print(tuples)
        line = next_line(line, leading, height)
        content_width = sum(width for font_name, text, width in tuples)
        x = (line.column.width - content_width) / 2.0
        for font_name, text, width in tuples:
            line.graphics.append(('texts', [(x, font_name, text)]))
            x += width

    return a + 1, line


def _wrap_long_lines(fonts, lines, width):
    return [list(_wrap_long_line(fonts, line, width)) for line in lines]


def _wrap_long_line(fonts, texts_and_fonts, width):
    for font_name, text in texts_and_fonts:
        width = fonts[font_name].width_of(text)
        yield font_name, text, width


def _split_texts_into_lines(fonts_and_texts):
    line = []
    for font_name, text in fonts_and_texts:
        pieces = text.split('\n')
        if pieces[0]:
            line.append((font_name, pieces[0]))
        for piece in pieces[1:]:
            yield line
            line = []
            if piece:
                line.append((font_name, piece))
    yield line
