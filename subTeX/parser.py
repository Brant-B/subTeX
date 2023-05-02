import markdown

# 定义action类型
from subTeX.composing import INDENT, knuth_paragraph, centered_place, vskip, INCH, ragged_place

TITLE = 'title'
HEADING = 'heading'
PARAGRAPH = 'paragraph'


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
            yield centered_place, [('title', title)]
            yield vskip, .75 * INCH
        elif line.startswith('## '):
            if in_paragraph:
                yield from paragraph_parser(INDENT, paragraph)
                in_paragraph = False
                paragraph = ''
            heading = line[3:]
            yield vskip, .25 * INCH
            yield ragged_place, [('subtitle', heading)]
        elif line.strip() == '':
            if in_paragraph:
                yield from paragraph_parser(INDENT,paragraph)
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
