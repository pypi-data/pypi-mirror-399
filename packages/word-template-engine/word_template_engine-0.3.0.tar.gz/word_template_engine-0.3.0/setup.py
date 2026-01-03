import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="word-template-engine",                  # 包名称
    version="0.3.0",                                   # 包版本
    author="sixsfish",                           # 作者
    license='MIT',                                     # 协议简写
    author_email="sixsfish@foxmail.com",                 # 作者邮箱
    description="A python of Word template engine,一个支持根据word模板生成word文档的docx引擎",             # 工具包简单描述
    long_description=long_description,                 # readme 部分
    long_description_content_type="text/markdown",     # readme 文件类型
    install_requires=[                                 # 工具包的依赖包
    'lxml>=6.0.2',
    'python-docx>=1.2.0',
    'requests>=2.32.5',
    ],
    url="https://github.com/sixsfish/word_template_engine",
    packages=["word_template_engine", "word_template_engine.utils"],  # 明确指定包名，避免包含其他目录
    classifiers=[                                      # PyPI 分类标签
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Office/Business :: Office Suites",
        "Topic :: Text Processing :: Markup",
    ],
    python_requires=">=3.12",                           # Python 版本要求
)
