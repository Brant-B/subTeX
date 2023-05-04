import atexit
import os
from PySide2 import QtWidgets
from PySide2.QtCore import QSizeF, QMarginsF
from PySide2.QtGui import QPainter, QPdfWriter, QFontDatabase

"""
"The basic unit is PT"
"""
PT = 1
INCH = 72
INDENT = INCH / 4
MM = 25.4 / 72
DPI = 1200 / 72
"""
 dots per inch
 pixels per inch
"""

class QtWriter(object):

    def __init__(self, path, width_pt, height_pt):
        if QtWidgets.QApplication.instance() is None:
            raise RuntimeError(
                'before using Qt to render a PDF, create an application:\n'
                '    from PySide2.QtWidgets import QApplication\n'
                '    QApplication([])'
            )
        self.writer = QPdfWriter(path)
        self.writer.setPageSizeMM(QSizeF(width_pt * MM, height_pt * MM))
        self.writer.setPageMargins(QMarginsF(0, 0, 0, 0))
        self.painter = QPainter(self.writer)
        atexit.register(self.close)

    def close(self):
        if self.painter.isActive():
            self.painter.end()

    def load_font(self, path):
        QFontDatabase.addApplicationFont(path)

    def get_fonts(self, font_specs):
        fonts = {}
        database = QFontDatabase()
        for key, family, style, size in font_specs:
            weight = database.weight(family, style)
            qt_font = database.font(family, style, size)
            actual_family = qt_font.family()
            if weight == -1 or family != actual_family:
                print('Cannot find font: {!r} {!r}'.format(family, style))
                os._exit(1)
            self.painter.setFont(qt_font)
            metrics = self.painter.fontMetrics()
            fonts[key] = QtFont(qt_font, metrics)
        return fonts

    def new_page(self):
        self.writer.newPage()

    def set_font(self, font):
        self.painter.setFont(font.qt_font)

    def draw_text(self, x_pt, y_pt, text):
        self.painter.drawText(x_pt * DPI, y_pt * DPI, text)


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

class QtFont(object):
    """
    convert from pixels to points
    """
    def __init__(self, qt_font, metrics):
        self.qt_font = qt_font
        self._qt_metrics = metrics
        self.ascent = metrics.ascent() / DPI
        self.descent = metrics.descent() / DPI
        self.height = metrics.height() / DPI
        self.leading = metrics.lineSpacing() / DPI - self.height

    def width_of(self, text):
        return self._qt_metrics.width(text) / DPI


