import argparse
import os
import sys
from PySide2.QtWidgets import QApplication
from subTeX.composing import (
    compose,
    vskip,
    centered_paragraph,
    section_break,
    draw_texts,
    draw_header_and_footer,
    parse_essay,

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
        (centered_paragraph, [('title', '老人与海')]),
        my_break,
        (centered_paragraph, [('italic', '海明威')]),
        (vskip, 0.75 * INCH),
    ]
    actions.extend(parse_essay(source_text, my_break))

    QApplication([])
    writer = QtWriter('book.pdf', page_width, page_height)
    writer.load_font('/Users/Skywalker/PycharmProjects/subTeX/fonts/PingFang.ttc')
    writer.load_font('/Users/Skywalker/PycharmProjects/subTeX/fonts/STHeiti Medium.ttc')
    writer.load_font('/Users/Skywalker/PycharmProjects/subTeX/fonts/Songti.ttc')

    fonts = writer.get_fonts([
        ('italic', 'Songti SC', 'Regular', 14),
        ('title', 'Heiti SC', 'Medium', 30),
        ('roman', '.PingFang SC', 'Regular', 12),
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
            draw_header_and_footer(current_page, page_no, fonts, writer, '老人与海')
        for graphic in line.graphics:
            function, *args = graphic
            if function == 'texts':
                function = draw_texts
            function(fonts, line, writer, *args)


if __name__ == '__main__':
    main(sys.argv[1:])
