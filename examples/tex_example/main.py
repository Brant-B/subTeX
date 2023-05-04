import argparse
import os
import sys

from PySide2.QtWidgets import QApplication

from subTeX.composing import compose
from subTeX.parser import tex_parser
from subTeX.skeleton import single_column_layout, unroll
from subTeX.writer_qt import QtWriter,draw_texts, draw_header_and_footer, INCH


page_width = 8.27 * INCH
page_height = 11.69 * INCH


def main(argv):
    parser = argparse.ArgumentParser(description='typeset the source.txt')
    parser.parse_args(argv)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    with open('source.tex') as f:
        source_text = f.read()

    next_line = single_column_layout(
        page_width, page_height,
        1 * INCH, 1 * INCH,
        0.8 * INCH, 0.8 * INCH
    )
    actions = [
    ]
    actions.extend(tex_parser(source_text))

    QApplication([])
    writer = QtWriter('output.pdf', page_width, page_height)
    writer.load_font(os.path.join(script_dir, '../../fonts/GenBasB.ttf'))
    writer.load_font(os.path.join(script_dir, '../../fonts/GenBasI.ttf'))
    writer.load_font(os.path.join(script_dir, '../../fonts/GenBasR.ttf'))

    fonts = writer.get_fonts([
        ('italic', 'Gentium Basic', 'Italic', 14),
        ('bigrm', 'Gentium Basic', 'Regular', 30),
        ('roman', 'Gentium Basic', 'Regular', 12),
        ('subtitle', 'Gentium Basic', 'Italic', 18),
        ('bf', 'Gentium Basic', 'Bold', 18)

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
            draw_header_and_footer(current_page, page_no, fonts, writer, 'this is header')
        for graphic in line.graphics:
            function, *args = graphic
            if function == 'texts':
                function = draw_texts
            elif function == 'draw_texts':
                function = draw_texts
            function(fonts, line, writer, *args)


if __name__ == '__main__':
    main(sys.argv[1:])
