# subTeX

`subTeX` 是一个受TeX 激发的Python 排版库。

本系统通过较为简单的Python代码实现了TeX 格式的排版。

简易TeX 我称为 subTeX，subTeX 名字 意为 TeX 这个排版引擎的子集，实现了在实际使用中最常用功能的排版引擎，通过简单的步骤就能生成 TeX 样式，精美的排版。

subTeX是一个使用Python 语言，主要使用Pyside2 库实现的排版程序。

## 功能介绍
它可以将 文本文件，Markdown 文件，tex 文件，经过语法分析转化为subTeX 内部支持命令格式，然后逐行将内容绘制到目标文件上，最后生成PDF 格式的目标文件。

subTeX 内部命令支持的功能有：
- 居中绘制
- 左对齐绘制
- 段落绘制
    - 生成所有可行的断行位置，并计算得出最优的断行位置
    - 连字算法，
- 设置行间距
- 增加纵向间隔
- 绘制页眉页尾
- 字体选择
- 页面格式设置

subTeX是一个简单的命令行工具。它的目的是为了探索TeX 的核心原理，以及如何用Python 实现一个简单的排版系统。
## version 2
  增加了对Markdown 文件和 tex 文件的编译支持。
通过将markdown和tex 解析到 subTeX 使用的命令，完成Pdf 格式的输出。

在下文markdown 示例， tex 示例可以看到subTeX 生成与其他引擎生成的pdf 的对比。

---
## 示例
### 中文示例
![img.png](attchments/img.png)
[zh_example/book.pdf](https://github.com/Brant-B/subTeX/blob/master/zh_example/book.pdf)

### 英文示例
![img.png](attchments/img1.png)
[en_example/book.pdf](https://github.com/Brant-B/subTeX/blob/master/en_example/book.pdf)

### markdown示例
subTeX 生成：
![md_img.png](attchments/md_img.png)
markdown 软件生成：
![markdown 软件生成](attchments/md_img2.png)
### tex 示例
subTeX 生成：
![subTeX生成](attchments/tex1.png)

plain TeX 引擎生成：
![plainTeX生成](attchments/tex2.png)

---
