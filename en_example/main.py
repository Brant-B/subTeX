import argparse
import os
import sys
from PySide2.QtWidgets import QApplication
from subTeX.composing import (
    compose,
    vskip,
    centered_paragraph,
    section_break,
)
from subTeX.knuth import knuth_paragraph
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
        (centered_paragraph, [('title', 'The Old Man and the Sea')]),
        my_break,
        (centered_paragraph, [('roman', 'Ernest Hemingway')]),
        (vskip, 0.75 * INCH),
    ]
    actions.extend(parse_essay(source_text, my_break))

    QApplication([])
    writer = QtWriter('book.pdf', page_width, page_height)
    writer.load_font('/Users/Skywalker/PycharmProjects/subTeX/fonts/GenBasB.ttf')
    writer.load_font('/Users/Skywalker/PycharmProjects/subTeX/fonts/GenBasI.ttf')
    writer.load_font('/Users/Skywalker/PycharmProjects/subTeX/fonts/GenBasR.ttf')

    fonts = writer.get_fonts([
        ('italic', 'Gentium Basic', 'Italic', 12),
        ('title', 'Gentium Basic', 'Regular', 30),
        ('roman', 'Gentium Basic', 'Regular', 12),
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
            draw_header_and_footer(current_page, page_no, fonts, writer)
        for graphic in line.graphics:
            function, *args = graphic
            if function == 'texts':
                function = draw_texts
            function(fonts, line, writer, *args)


def parse_essay(text, my_break):
    sections = text.strip().split('\n\n\n')
    for i, section in enumerate(sections):
        if i:
            yield my_break
        section = section.strip()
        paragraphs = section.split('\n\n')
        for j, paragraph in enumerate(paragraphs):
            indent = INDENT
            # yield avoid_widows_and_orphans,
            yield knuth_paragraph, 0, indent, [('roman', paragraph.strip())]


def draw_header_and_footer(page, page_no, fonts, writer):
    font = fonts['roman']
    text = str(page_no)
    width = font.width_of(text)
    x = (page.width - width) / 2
    y = page.height - INCH * 2 / 3

    writer.set_font(font)
    writer.draw_text(x, y, text)

    font = fonts['italic']
    text = 'the old man an the sea'
    width = font.width_of(text)
    x = (page.width - width) / 2
    y = INCH * 3 / 4

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


if __name__ == '__main__':
    main(sys.argv[1:])
