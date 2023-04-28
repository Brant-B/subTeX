import atexit
import os
from PySide2 import QtWidgets
from PySide2.QtCore import QSizeF, QMarginsF
from PySide2.QtGui import QPainter, QPdfWriter, QFontDatabase

MM = 25.4 / 72
PT = 1200 / 72

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
        for key, family, style, size in font_specs:
            weight = QFontDatabase.weight(family, style)
            qt_font = QFontDatabase.font(family, style, size)
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
        # if self.include_crop_marks:
        #     self.draw_crop_marks()

    def set_font(self, font):
        self.painter.setFont(font.qt_font)

    def draw_text(self, x_pt, y_pt, text):
        self.painter.drawText(x_pt * PT, y_pt * PT, text)

class QtFont(object):
    def __init__(self, qt_font, metrics):
        self.qt_font = qt_font
        self._qt_metrics = metrics
        self.ascent = metrics.ascent() * 72 / 1200
        self.descent = metrics.descent() * 72 / 1200
        self.height = metrics.height() * 72 / 1200
        self.leading = metrics.lineSpacing() * 72 / 1200 - self.height

    def width_of(self, text):
        return self._qt_metrics.width(text) * 72 / 1200
