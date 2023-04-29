import re

pattern = r'([\u00a0]?)([\da-zA-Z]+|[\u4e00-\u9fa5])([^\u00a0\w\s]*)([ \n]*)'
_text_findall = re.compile(pattern).findall

text = "hello, world"
result = _text_findall(text)
print(result)
