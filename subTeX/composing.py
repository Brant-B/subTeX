from .skeleton import unroll
import re
from .texlib import ObjectList, Box, Glue, Penalty
from .hyphenate import hyphenate_word

INCH = 72
INDENT = INCH / 4
_zero_width_break = Glue(0, .5, .3333)


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


def add_leading(line, next_line, leading=9999):
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

def section_break(actions, a, fonts, line, next_line, font_name='roman', graphic='* * * * *'):
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
        line2 = next_line(line, 9999, height)
        line2.graphics.append(graphic)
        line3 = next_line(line2, leading, height)
        return a1, line3

    # Re-run the following content, forcing it on to the next page.
    a = add_leading(line3, next_line)
    return call_action(actions, a1, fonts, line3, a)


def beginsection(actions, a, fonts, line, next_line, fonts_and_texts):
    """ format the line as heading"""
    leading = max(fonts[name].leading for name, text in fonts_and_texts)
    height = max(fonts[name].height for name, text in fonts_and_texts)

    tmpline = next_line(line, leading, height)

    unwrapped_lines = _split_texts_into_lines(fonts_and_texts)
    wrapped_lines = _wrap_long_lines(fonts, unwrapped_lines,
                                     tmpline.column.width)

    for tuples in wrapped_lines:
        print(tuples)
        line = next_line(line, leading, height)
        x = 0
        for font_name, text, width in tuples:
            line.graphics.append(('texts', [(x, font_name, text)]))
            x += width

    return a + 1, line


def centerline(actions, a, fonts, line, next_line, fonts_and_texts):
    """Format text as a centered paragraph."""

    leading = max(fonts[name].leading for name, text in fonts_and_texts)
    height = max(fonts[name].height for name, text in fonts_and_texts)

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


def knuth_paragraph(actions, a, fonts, line, next_line,
                    indent, first_indent, fonts_and_texts):
    font_name = fonts_and_texts[0][0]
    font = fonts[font_name]
    width_of = font.width_of

    leading = max(fonts[name].leading for name, text in fonts_and_texts)
    height = max(fonts[name].height for name, text in fonts_and_texts)

    line = next_line(line, leading, height)
    line_lengths = [line.column.width]

    if first_indent is True:
        first_indent = font.height

    olist = ObjectList()
    olist.debug = False

    if first_indent:
        olist.append(Glue(first_indent, 0, 0))

    space_width = width_of(' ')
    space_glue = Glue(space_width, space_width * .5, space_width * .3333)

    indented_lengths = [length - indent for length in line_lengths]

    for font_name, text in fonts_and_texts:
        font = fonts[font_name]
        width_of = font.width_of
        boxes = break_text_into_boxes(text, font_name, width_of, space_glue)
        olist.extend(boxes)

    if olist[-1] is space_glue:
        olist.pop()

    olist.add_closing_penalty()

    for tolerance in 1, 2, 3, 4, 5, 6, 7:
        try:
            breaks = olist.compute_breakpoints(
                indented_lengths, tolerance=tolerance)
        except RuntimeError:
            pass
        else:
            break
    else:
        print('FAIL')
        breaks = [0, len(olist) - 1]

    assert breaks[0] == 0
    start = 0

    for i, breakpoint in enumerate(breaks[1:]):
        r = olist.compute_adjustment_ratio(start, breakpoint, i,
                                           indented_lengths)

        # r = 1.0

        xlist = []
        x = 0
        for i in range(start, breakpoint):
            box = olist[i]
            if box.is_glue():
                x += box.compute_width(r)
            elif box.is_box():
                font_name, text = box.content
                xlist.append((x + indent, font_name, text))
                x += box.width

        bbox = olist[breakpoint]
        if bbox.is_penalty() and bbox.width:
            xlist.append((x + indent, font_name, '-'))

        line.graphics.append(('texts', xlist))
        line = next_line(line, leading, height)
        start = breakpoint + 1

    return a + 1, line.previous


# Regular expression that scans text for control codes, words, punction,
# and runs of contiguous space.  If it works correctly, any possible
# string will consist entirely of contiguous matches of this regular
# expression.
pattern = r'([\u00a0]?)([\da-zA-Z]+|[\u4e00-\u9fa5]|)([^\u00a0\w\s]*)([ \n]*)'
_text_findall = re.compile(pattern).findall


def is_Chinese(text):
    return bool(re.match(r'[\u4e00-\u9fa5]', text))


def break_text_into_boxes(text, font_name, width_of, space_glue):
    # print(repr(text))
    for control_code, word, punctuation, space in _text_findall(text):
        # print((control_code, word, punctuation, space))
        if control_code:
            if control_code == '\u00a0':
                yield Penalty(0, 1000)
                yield space_glue
            else:
                print('Unsupported control code: %r' % control_code)
        if word:
            if is_Chinese(word):
                yield _zero_width_break
            strings = hyphenate_word(word)
            if punctuation:
                strings[-1] += punctuation
            for i, string in enumerate(strings):
                if i:
                    yield Penalty(width_of('-'), 100)
                yield Box(width_of(string), (font_name, string))

        elif punctuation:
            yield Box(width_of(punctuation), (font_name, punctuation))
        if punctuation == '-':
            yield _zero_width_break
        if space:
            yield space_glue


def draw_header_and_footer(page, page_no, fonts, writer, text):
    font = fonts['italic']
    width = font.width_of(text)
    x = (page.width - width) / 2
    y = INCH * 3 / 4

    writer.set_font(font)
    writer.draw_text(x, y, text)

    font = fonts['roman']
    text = str(page_no)
    width = font.width_of(text)
    x = (page.width - width) / 2
    y = page.height - INCH * 2 / 3

    writer.set_font(font)
    writer.draw_text(x, y, text)


def draw_texts(fonts, line, writer, xlist):
    current_font_name = None
    for x, font_name, text in xlist:
        if font_name != current_font_name:
            font = fonts[font_name]
            writer.set_font(font)
            current_font_name = font_name
        writer.draw_text(line.column.x + x,
                         line.column.y + line.y - font.descent,
                         text)
