from collections import namedtuple

Font = namedtuple('Font', 'ascent descent height leading')
Page = namedtuple('Page', 'width height')
Column = namedtuple('Column', 'page id x y width height')
Line = namedtuple('Line', 'previous column y graphics')


def single_column_layout(width: float, height: float, top: float, bottom: float,
                         inner: float, outer: float) -> callable:
    """
    Returns a function that generates a single-column layout of a document.

    Args:
        width: The width of the document.
        height: The height of the document.
        top: The top margin.
        bottom: The bottom margin.
        inner: The width of the inner margin.
        outer: The width of the outer margin.

    Returns:
        A function that takes a leading and height as arguments, and generates a new line
        in the single-column layout of the document.
    """
    column_width = width - inner - outer
    column_height = height - top - bottom

    def new_page() -> Page:
        """Creates a new page with the given width and height."""
        return Page(width, height)

    def next_column(column: Column) -> Column:
        """Creates a new column after the given column."""
        page = new_page()
        id = column.id + 1 if column else 1
        if id % 2:
            left = inner
        else:
            left = outer
        return Column(page, id, left, top, column_width, column_height)

    def next_line(line: Line, leading: float, height: float) -> Line:
        """
        Creates a new line after the given line, with the given leading and height.

        Args:
            line: The previous line.
            leading: The leading (i.e. line spacing) for the new line.
            height: The height of the new line.

        Returns:
            A new line with the given height and leading, placed after the previous line.
        """
        if line:
            column = line.column
            y = line.y + height + leading
            if y <= column.height:
                return Line(line, column, y, [])
        else:
            column = None
        return Line(line, next_column(column), height, [])

    return next_line


def unroll(start_line: Line, end_line: Line):
    """
    Unrolls a single-column layout of a document into a flat list of lines.

    Args:
        start_line: The first line of the layout.
        end_line: The last line of the layout.

    Returns:
        A flattened list of lines, containing all the lines from the layout in the order
        they appear in the document.
    """
    lines = [end_line]
    while end_line is not start_line:
        end_line = end_line.previous
        lines.append(end_line)
    lines.reverse()
    return lines
