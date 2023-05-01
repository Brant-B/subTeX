import argparse
import os
import sys

from PySide2.QtWidgets import QApplication

from subTeX.composing import (
    compose,
    vskip,
    centered_place,
    section_break,
    draw_header_and_footer,
    draw_texts, parse_essay,
    ragged_place
)
from subTeX.skeleton import (
    single_column_layout,
    unroll
)
from subTeX.writer_qt import QtWriter

INCH = 74
INDENT = INCH / 4


def main(argv):
    parser = argparse.ArgumentParser(description='typeset the source.txt')
    parser.parse_args(argv)
    os.chdir(os.path.dirname(__file__))
    with open('source.txt') as f:
        source_text = f.read()

    page_width = 8.27 * INCH
    page_height = 11.69 * INCH
    next_line = single_column_layout(
        page_width, page_height,
        1 * INCH, 1 * INCH,
        0.8 * INCH, 0.8 * INCH
    )
    my_break = section_break, 'roman', ('texts', [(0, 'roman', '* * *')])

    actions = [
        (vskip, 0.75 * INCH),
        (centered_place, [('title', 'The Old Man and the Sea')]),
        my_break,
        (centered_place, [('roman', 'Ernest Hemingway')]),
        (vskip, 0.75 * INCH),
        (ragged_place, [('subtitle', '1. first section')]),
    ]
    actions.extend(parse_essay(source_text, my_break))
    actions.append((ragged_place, [('subtitle', 'The End')]))

    QApplication([])
    writer = QtWriter('book.pdf', page_width, page_height)
    writer.load_font('/Users/Skywalker/PycharmProjects/subTeX/fonts/GenBasB.ttf')
    writer.load_font('/Users/Skywalker/PycharmProjects/subTeX/fonts/GenBasI.ttf')
    writer.load_font('/Users/Skywalker/PycharmProjects/subTeX/fonts/GenBasR.ttf')

    fonts = writer.get_fonts([
        ('italic', 'Gentium Basic', 'Italic', 12),
        ('title', 'Gentium Basic', 'Regular', 30),
        ('roman', 'Gentium Basic', 'Regular', 12),
        ('subtitle','Gentium Basic', 'Italic', 18)
    ])

    end_line = compose(actions, fonts, None, next_line)
    lines = unroll(None, end_line)[1:]
    current_page = lines[0].column.page
    page_no = 1
    for line in lines:
        if line.column.page is not current_page:
            current_page = line.column.page
            writer.new_page()
            page_no += 1
            draw_header_and_footer(current_page, page_no, fonts, writer, 'the old man an the sea')
        for graphic in line.graphics:
            function, *args = graphic
            if function == 'texts':
                function = draw_texts
            elif function == 'draw_texts':
                function = draw_texts
            function(fonts, line, writer, *args)


if __name__ == '__main__':
    main(sys.argv[1:])
