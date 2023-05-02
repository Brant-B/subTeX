from PySide2.QtGui import QFontDatabase
from PySide2.QtWidgets import QApplication

app = QApplication([])
database = QFontDatabase()

font_paths = [
    '/Users/Skywalker/PycharmProjects/subTeX/fonts/GenBasB.ttf',
    '/Users/Skywalker/PycharmProjects/subTeX/fonts/GenBasI.ttf',
    '/Users/Skywalker/PycharmProjects/subTeX/fonts/GenBasR.ttf'
]


def main():
    for font_path in font_paths:
        font_id = database.addApplicationFont(font_path)
        if font_id == -1:
            print(f"Failed to load font: {font_path}")
        else:
            families = database.applicationFontFamilies(font_id)
            for family in families:
                print(f"Loaded font '{family}' from '{font_path}'")
                styles = database.styles(family)
                for style in styles:
                    print(f"Style: {style}")


if __name__ == '__main__':
    main()