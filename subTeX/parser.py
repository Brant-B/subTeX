import re

from subTeX.composing import INDENT, knuth_paragraph, centerline, vskip, INCH, beginsection

"""
parse markdown_code to actions
"""


def markdown_parser(text):
    lines = text.split('\n')
    in_paragraph = False
    paragraph = ''
    for line in lines:
        if line.startswith('# '):
            if in_paragraph:
                yield from paragraph_parser(INDENT, paragraph)
                in_paragraph = False
                paragraph = ''
            title = line[2:]
            yield vskip, .75 * INCH
            yield centerline, [('title', title)]
            yield vskip, .75 * INCH
        elif line.startswith('## '):
            if in_paragraph:
                yield from paragraph_parser(INDENT, paragraph)
                in_paragraph = False
                paragraph = ''
            heading = line[3:]
            yield vskip, .25 * INCH
            yield beginsection, [('subtitle', heading)]
        elif line.strip() == '':
            if in_paragraph:
                yield from paragraph_parser(INDENT, paragraph)
                in_paragraph = False
                paragraph = ''
        else:
            if not in_paragraph:
                in_paragraph = True
                paragraph = line
            else:
                paragraph += '\n' + line
    if in_paragraph:
        yield from paragraph_parser(INDENT, paragraph)


def txt_parser(text, my_break):
    sections = text.strip().split('\n\n\n')
    for i, section in enumerate(sections):
        if i:
            yield my_break
        section = section.strip()
        paragraphs = section.split('\n\n')
        for j, paragraph in enumerate(paragraphs):
            yield from paragraph_parser(INDENT, paragraph)


def paragraph_parser(indent, text):
    yield knuth_paragraph, 0, indent, [('roman', text.strip())]


"""
parse tex code to actions
"""


def tex_parser(text):
    pattern = r"(\\[a-zA-Z]+)(?:\{(\\[a-zA-Z]+)?(.*?)\})?"
    matches = list(re.finditer(pattern, text, re.DOTALL))
    for i in range(len(matches) + 1):
        if i == 0:
            content_start = 0
        else:
            content_start = matches[i - 1].end()

        if i < len(matches):
            content_end = matches[i].start()
            match = matches[i]
            command_code = match.group(1)[1:]
            font = match.group(2)
            content = match.group(3)

            if font is not None:
                font = font[1:]
        else:
            content_end = len(text)
        no_command_text = text[content_start:content_end].strip()
        if no_command_text:
            yield from paragraph_parser(INDENT, no_command_text)
        if i < len(matches):
            if command_code == 'centerline':
                if font:
                    yield centerline, [(font, content)]
                else:
                    yield centerline, [('italic', content)]
            elif command_code == 'beginsection':
                if font:
                    yield beginsection, [(font, content)]
                else:
                    yield beginsection, [('subtitle', content)]
            elif command_code == 'bigskip':
                yield vskip, .75 * INCH
            else:
                yield vskip, .25 * INCH
