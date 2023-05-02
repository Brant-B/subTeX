import markdown

# 定义action类型
TITLE = 'title'
HEADING = 'heading'
PARAGRAPH = 'paragraph'


def markdown_parser(text):
    actions = []
    in_paragraph = False
    paragraph_text = ''
    lines = text.split('\n')
    for line in lines:
        if line.startswith('# '):
            # 解析标题
            title = line[2:]
            if in_paragraph:
                actions.append((PARAGRAPH, paragraph_text))
                in_paragraph = False
                paragraph_text = ''
            actions.append((TITLE, title))
        elif line.startswith('## '):
            # 解析二级标题
            heading = line[3:]
            if in_paragraph:
                actions.append((PARAGRAPH, paragraph_text))
                in_paragraph = False
                paragraph_text = ''
            actions.append((HEADING, heading))
        elif line.strip() == '':
            # 处理空行
            if in_paragraph:
                # actions.append((PARAGRAPH, paragraph_text))
                in_paragraph = False
                paragraph_text = ''
        else:
            # 处理段落
            if not in_paragraph:
                in_paragraph = True
                paragraph_text = line
            else:
                paragraph_text += ' ' + line
    if in_paragraph:
        actions.append((PARAGRAPH, paragraph_text))
    return actions
# 测试代码
markdown_text = """# Prologue
## 1. Concerning Hobbits
Hobbits are an unobtrusive...
For they are a little people...
fdsafdsafdas 
## 2. Concerning Pipe-weed
There is another astonishing...
"""
actions = markdown_parser(markdown_text)
print(actions)
