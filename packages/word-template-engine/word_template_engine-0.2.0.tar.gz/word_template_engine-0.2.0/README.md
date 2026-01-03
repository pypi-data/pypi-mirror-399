# Word模板引擎---CHINESE

word_template_engine是一个类似于docx-template的Word模板引擎，使用Python直接解析Word文档的XML结构实现，根据docx格式的模板生成对应word文件，**完全保留所有样式信息**。

仓库链接：https://github.com/sixsfish/word_template_engine
## 功能特性

1. **字符串文本替换**: `{{data.my_text}}` - 替换为对应的数据值（**不需要结束标签**）

2. **表格行循环**: `{{#data.tableList}}` - 在表格头部标记，根据数据循环生成表格行，使用`[field_name]`作为字段占位符（**不需要结束标签**）

3. **条件区块**: `{{?data.field != null && data.field.size() > 0}}...{{/}}` - 根据条件显示或隐藏内容块（**需要结束标签 {{/}}**）

4. **图片插入**: `{{@var}}` - 插入图片，var格式: `{'url': '', 'conf': {'w': '18cm', 'h': '12cm'}}`（**不需要结束标签**）


## 标签说明

### 有结束标签的标签

- **区块**: `{{?condition}}...{{/}}`
  - 只有区块需要结束标签
  - 支持嵌套
  - 示例：
    ```
    {{?data.cond_A == ''}}
    无
    {{/}}
    ```

## 安装

使用pip安装依赖：

```bash
pip install word_template_engine
```

**注意**: 本引擎直接解析Word文档的XML结构，这样可以完整保留所有样式信息。

## 使用方法

### 1. 创建Word模板

在Word文档中使用以下占位符：

#### 文本替换
- 普通文本 `{{data.my_text}}`
- 格式化日期文本 `{{data.my_date|y/m/d}}`，

#### 表格行循环
在表格行的单元格中写入 `{{#data.tableList}}`，其他单元格使用方括号占位符：
- `[child1]`
- `[child2]`
- `[child3]`


#### 条件区块
```text
{{?data.condi_list.size() > 0}}
这部分内容只有在条件为真时才会显示
{{/}}
```

支持的条件：
- `size() > 0`
- `==数字`

#### 图片
方式1: 使用变量名
```
{{@data.image_config}}
```

方式2: 直接写JSON
```
{{@{'url':'path/to/image.jpg','conf':{'w':'18cm','h':'12cm'}}}}
```

支持的尺寸单位: cm


### 2. 使用Python代码渲染

```python
from word_template_engine import WordTemplateEngine

# 创建引擎实例
engine = WordTemplateEngine('template.docx')

# 准备数据
data = {
    'data': {
        'my_name': '小马',
        'infoList': [
            {'name': '小明', 'age': 12, "sex":"男",'desc': '我是12岁男孩'},
            {'name': '小花', 'age': 8, "sex":"女",'desc': '我是8岁女孩'},
        ],
        'table_count': 2,
        'image_conf':{'url': '/opt/my_name.png', 'conf': {'w': '18cm', 'h': '12cm'}},
        'baseList': {
            'info':[
                {'name': '小明', 'desc': '我是12岁男孩'},
                {'name': '小花', 'age': 8, "sex":"女",'desc': '我是8岁女孩'},
        	],
            'rela_info':[
                {'name': '小明','desc': '哥哥'},
                {'name': '小花', 'desc': '妹妹'},
        	]
        },
    }
}

# 渲染并保存
engine.render(data, 'output.docx')
```

名字：{{#data.my_name}}

+ 模板表格如下

## 信息

{{?data.table_count==2}}

| {{#data.infoList}}名字 | 年龄  | 性别  | 描述   |
| ---------------------- | ----- | ----- | ------ |
| [name]                 | [age] | [sex] | [desc] |

{{/}}

{{?data.table_count!=2}}

| 名字 | 年龄  | 性别  | 描述   |
| ----------------------- | ----- | ----- | ------ |
| 无数据 |

{{/}}



关系列表

| {{#data.baseList}}名字 | 描述   |
| ----------------------| ------ |
| {{+info}}[name]描述            | [desc]{{/info}} |
| {{+rela_info}}[name]关系            | [desc]{{/rela_info}} |

图片

{{@data.image_conf}}


---

# Word Template Engine---ENGLISH

`word_template_engine` is a Word template engine similar to docx-template, implemented by directly parsing Word document XML structures using Python. It generates corresponding Word files based on docx format templates and **completely preserves all style information**.

Repository: https://github.com/sixsfish/word_template_engine

## Features

1. **Text Replacement**: `{{data.my_text}}` - Replace with corresponding data values (**no closing tag required**)

2. **Table Row Loop**: `{{#data.tableList}}` - Mark in table header, generate table rows based on data, use `[field_name]` as field placeholders (**no closing tag required**)

3. **Conditional Blocks**: `{{?data.field != null && data.field.size() > 0}}...{{/}}` - Show or hide content blocks based on conditions (**closing tag {{/}} required**)

4. **Image Insertion**: `{{@var}}` - Insert images, var format: `{'url': '', 'conf': {'w': '18cm', 'h': '12cm'}}` (**no closing tag required**)

## Tag Reference

### Tags with Closing Tags

- **Block**: `{{?condition}}...{{/}}`
  - Only blocks require closing tags
  - Supports nesting
  - Example:
    ```
    {{?data.cond_A == ''}}
    无
    {{/}}
    ```

## Installation

Install using pip:

```bash
pip install word-template-engine
```

**Note**: This engine directly parses Word document XML structures, which allows complete preservation of all style information.

## Usage

### 1. Create Word Template

Use the following placeholders in Word documents:

#### Text Replacement
- Plain text: `{{data.my_text}}`
- Formatted date text: `{{data.my_date|y/m/d}}`

#### Table Row Loop
Write `{{#data.tableList}}` in table row cells, use square bracket placeholders in other cells:
- `[child1]`
- `[child2]`
- `[child3]`

#### Conditional Blocks
```text
{{?data.condi_list.size() > 0}}
This content will only be displayed when the condition is true
{{/}}
```

Supported conditions:
- `size() > 0`
- `==number`

#### Images
Method 1: Use variable name
```
{{@data.image_config}}
```

Method 2: Write JSON directly
```
{{@{'url':'path/to/image.jpg','conf':{'w':'18cm','h':'12cm'}}}}
```

Supported size units: cm

### 2. Render with Python Code

```python
from word_template_engine import WordTemplateEngine

# Create engine instance
engine = WordTemplateEngine('template.docx')

# Prepare data
data = {
    'data': {
        'my_name': 'Xiao Ma',
        'infoList': [
            {'name': 'Xiao Ming', 'age': 12, "sex":"Male",'desc': 'I am a 12-year-old boy'},
            {'name': 'Xiao Hua', 'age': 8, "sex":"Female",'desc': 'I am an 8-year-old girl'},
        ],
        'table_count': 2,
        'image_conf':{'url': '/opt/my_name.png', 'conf': {'w': '18cm', 'h': '12cm'}},
        'baseList': {
            'info':[
                {'name': 'Xiao Ming', 'desc': 'I am a 12-year-old boy'},
                {'name': 'Xiao Hua', 'age': 8, "sex":"Female",'desc': 'I am an 8-year-old girl'},
            ],
            'rela_info':[
                {'name': 'Xiao Ming','desc': 'Brother'},
                {'name': 'Xiao Hua', 'desc': 'Sister'},
            ]
        },
    }
}

# Render and save
engine.render(data, 'output.docx')
```

Name: {{#data.my_name}}

+ Template table as follows

## Information

{{?data.table_count==2}}

| {{#data.infoList}}Name | Age  | Gender | Description   |
| ---------------------- | ----- | ----- | ------ |
| [name]                 | [age] | [sex] | [desc] |

{{/}}

{{?data.table_count!=2}}

| Name | Age  | Gender | Description   |
| ----------------------- | ----- | ----- | ------ |
| No data |

{{/}}

## Relationship List

| {{#data.baseList}}Name | Description   |
| ----------------------| ------ |
| {{+info}}[name]Description            | [desc]{{/info}} |
| {{+rela_info}}[name]Relationship            | [desc]{{/rela_info}} |

## Image

{{@data.image_conf}}
