"""
Text placeholder processing.
"""
import re
from datetime import datetime, date
from copy import deepcopy
from typing import Any, Dict, List
from docx.text.paragraph import Paragraph

from .common import get_nested_value, process_block, evaluate_condition


PLACEHOLDER_PATTERN = re.compile(r"\{\{([^@#?/$*}]+)\}\}")
BRACKET_FMT_PATTERN = re.compile(r"\[([^\]|]+)\|([^\]]+)\]")
NORMAL_FMT_PATTERN = re.compile(r"\{\{([^\]|]+)\|([^\]]+)\}\}")


def format_bracket_with_item(flag,text: str, item: Any, root_data: Dict[str, Any]) -> str:
    def repl(m: re.Match) -> str:
        key = m.group(1).strip()
        fmt = m.group(2).strip().lower()

        # 1) 优先从当前 item 中取值（行数据）
        val = None
        if isinstance(item, dict) and key in item:
            val = item.get(key)
        else:
            # 2) 否则从全局 data 中按路径取值
            val = get_nested_value(root_data, key)

        if not val:
            return ""

        s = str(val).strip()
        if fmt in ["y-m-d", "y/m/d"]:
            date = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
        if fmt == "y-m-d":
            return date.strftime("%Y-%m-%d")
        elif fmt == 'y/m/d':
            return date.strftime("%Y/%m/%d")

        # 其他格式直接返回原字符串
        return s
    if flag =='tab':
        return BRACKET_FMT_PATTERN.sub(repl, text)
    elif flag == 'nomal':
        return NORMAL_FMT_PATTERN.sub(repl, text)



def _has_non_text_elements(run) -> bool:
    """Check if a run contains non-text elements like images, charts, drawings, etc."""
    if run._element is None or len(run._element) == 0:
        return False
    # 检查是否包含图片、图表、绘图对象等
    # drawing: 绘图对象（包括图表、线条、形状等）
    # pict: 图片
    # object: 嵌入对象
    # fldChar: 字段字符（可能包含图表）
    for child in run._element:
        tag = child.tag if hasattr(child, 'tag') else str(child)
        if any(keyword in tag.lower() for keyword in ['drawing', 'pict', 'object', 'chart', 'shape']):
            return True
    return False


def _paragraph_has_non_text_elements(paragraph: Paragraph) -> bool:
    """Check if a paragraph contains non-text elements like images, charts, drawings, etc."""
    for run in paragraph.runs:
        if _has_non_text_elements(run):
            return True
    # 检查段落元素本身是否包含非文本元素
    if paragraph._element is not None and len(paragraph._element) > 0:
        for child in paragraph._element:
            tag = child.tag if hasattr(child, 'tag') else str(child)
            if any(keyword in tag.lower() for keyword in ['drawing', 'pict', 'object', 'chart', 'shape', 'tbl']):
                return True
    return False


def _rewrite_paragraph_text(paragraph: Paragraph, new_text: str) -> None:
    """
    Rewrite text into existing runs to preserve styles and non-text elements.
    保留包含图表、线条、图片等非文本元素的 run，只修改纯文本 run。
    """
    runs = list(paragraph.runs)  # 创建副本以避免迭代时修改
    remaining = new_text
    
    # 分离包含非文本元素的 run 和纯文本 run
    text_runs = []
    non_text_runs = []
    
    for run in runs:
        if _has_non_text_elements(run):
            non_text_runs.append(run)
        else:
            text_runs.append(run)
    
    # 只处理纯文本 run
    for run in text_runs:
        orig_len = len(run.text or "")
        if not remaining:
            # 如果没有剩余文本，清空这个 run 的文本（但保留样式）
            run.text = ""
            continue
        if orig_len > 0:
            run.text = remaining[:orig_len]
            remaining = remaining[orig_len:]
        else:
            run.text = ""
    
    # 如果还有剩余文本，添加到最后一个文本 run 或创建新 run
    if remaining:
        if text_runs:
            # 使用最后一个文本 run 的样式
            base = text_runs[-1]
            if base.text:
                base.text += remaining
            else:
                base.text = remaining
        else:
            # 如果没有文本 run，使用最后一个 run 的样式或创建新 run
            base = runs[-1] if runs else paragraph.add_run()
            new_run = paragraph.add_run(remaining)
            if runs:
                new_run.style = base.style
                new_run.bold = base.bold
                new_run.italic = base.italic
                new_run.underline = base.underline
                if base.font.size:
                    new_run.font.size = base.font.size
                if base.font.color.rgb:
                    new_run.font.color.rgb = base.font.color.rgb
                if base.font.name:
                    new_run.font.name = base.font.name
    
    # 确保没有 None 文本
    for run in runs:
        if run.text is None:
            run.text = ""


def _paragraph_text(paragraph: Paragraph) -> str:
    return "".join(run.text or "" for run in paragraph.runs)


def _replace_bracket_placeholders(text: str, item: Any) -> str:
    if isinstance(item, dict):
        for k, v in item.items():
            text = text.replace(f"[{k}]", "" if v is None else str(v))
    else:
        text = re.sub(r"\[text\]", "" if item is None else str(item), text)
    return text


def process_paragraph_loops(paragraphs: List[Paragraph], data: Dict[str, Any]) -> None:
    """
    Handle non-table loops:
    {{#data.list}}
    [field] ...
    If marker paragraph has no [ ], use the next paragraph with [ ] as template.
    """
    loop_pat = re.compile(r"\{\{#([^}]+)\}\}")
    bracket_pat = re.compile(r"\[[^\]]+\]")
    idx = 0
    while idx < len(paragraphs):
        para = paragraphs[idx]
        full_text = _paragraph_text(para)
        m = loop_pat.search(full_text)
        if not m:
            idx += 1
            continue
        field_path = m.group(1).strip()
        items = get_nested_value(data, field_path)
        parent = para._element.getparent()

        # choose template: marker line if it contains [ ], else next line with [ ]
        template_el = para._element
        template_idx = idx
        if not bracket_pat.search(full_text):
            look = idx + 1
            while look < len(paragraphs):
                cand_text = _paragraph_text(paragraphs[look])
                if bracket_pat.search(cand_text):
                    template_el = paragraphs[look]._element
                    template_idx = look
                    break
                if loop_pat.search(cand_text):
                    break
                look += 1

        # remove marker paragraph
        parent.remove(para._element)
        paragraphs.pop(idx)

        # if template is different and still present, remove it too (after marker removal, index shifts)
        if template_idx != idx and template_idx < len(paragraphs) + 1:
            parent.remove(template_el)
            paragraphs.pop(idx)

        if not isinstance(items, list) or len(items) == 0:
            continue

        new_paras: List[Paragraph] = []
        insert_pos = idx
        for item in items:
            new_el = deepcopy(template_el)
            parent.insert(insert_pos, new_el)
            new_para = Paragraph(new_el, para._parent)
            new_text = loop_pat.sub("", _paragraph_text(new_para))
            new_text = _replace_bracket_placeholders(new_text, item)
            _rewrite_paragraph_text(new_para, new_text)
            new_paras.append(new_para)
            insert_pos += 1

        paragraphs[idx:idx] = new_paras
        idx += len(new_paras)


def process_paragraph_blocks(paragraphs: list[Paragraph], data: Dict[str, Any]) -> None:
    """
    Handle block tags that may span multiple paragraphs:
    {{?cond}}
    ...
    {{/}}
    If condition false, clear text in range; if true, remove only the tags.
    """
    start_pat = re.compile(r"\{\{\?([^}]+)\}\}")
    end_pat = re.compile(r"\{\{/\}\}")

    i = 0
    while i < len(paragraphs):
        text = _paragraph_text(paragraphs[i])
        start_match = start_pat.search(text)
        if not start_match:
            i += 1
            continue

        cond = start_match.group(1).strip()
        depth = 1
        j = i + 1
        end_idx = None
        while j < len(paragraphs):
            t = _paragraph_text(paragraphs[j])
            if start_pat.search(t):
                depth += 1
            if end_pat.search(t):
                depth -= 1
                if depth == 0:
                    end_idx = j
                    break
            j += 1

        if end_idx is None:
            # no matching end; skip
            i += 1
            continue

        if evaluate_condition(cond, data):
            # condition true: remove tags; if tag-only paragraphs, delete them
            new_start = start_pat.sub("", text)
            new_end = end_pat.sub("", _paragraph_text(paragraphs[end_idx]))

            to_delete = []
            if new_start.strip() == "":
                # 只有在不包含非文本元素时才删除段落
                if not _paragraph_has_non_text_elements(paragraphs[i]):
                    to_delete.append(i)
                else:
                    # 如果包含非文本元素，只移除标记文本，保留段落
                    _rewrite_paragraph_text(paragraphs[i], new_start)
            else:
                _rewrite_paragraph_text(paragraphs[i], new_start)

            if new_end.strip() == "":
                # 只有在不包含非文本元素时才删除段落
                if not _paragraph_has_non_text_elements(paragraphs[end_idx]):
                    to_delete.append(end_idx)
                else:
                    # 如果包含非文本元素，只移除标记文本，保留段落
                    _rewrite_paragraph_text(paragraphs[end_idx], new_end)
            elif end_idx not in to_delete:
                _rewrite_paragraph_text(paragraphs[end_idx], new_end)

            # delete paragraphs marked (from end to start to keep indices valid)
            for idx_del in sorted(to_delete, reverse=True):
                p_el = paragraphs[idx_del]._element
                p_el.getparent().remove(p_el)
                paragraphs.pop(idx_del)

            # adjust end_idx if paragraphs were removed
            i = max(i, 0)
        else:

            # condition false: remove entire block paragraphs
            for k in range(end_idx, i - 1, -1):
                
                p_el = paragraphs[k]._element
                p_el.getparent().remove(p_el)
                paragraphs.pop(k)
            # i remains the same position (now next paragraph)
        # continue from current index
        i = max(i, 0)


def render_text(text: str, data: Dict[str, Any]) -> str:
    """Process blocks then replace {{path}} placeholders."""
    text = process_block(text, data)
    
    def repl(match: re.Match):
        path = match.group(1).strip()
        val = get_nested_value(data, path)
        return "" if val is None else str(val)

    return PLACEHOLDER_PATTERN.sub(repl, text)


def process_paragraph(paragraph: Paragraph, data: Dict[str, Any]) -> None:
    """Render placeholders in a paragraph while preserving run styles."""
    full_text = "".join(run.text for run in paragraph.runs)
    full_text = format_bracket_with_item('nomal',full_text, None, data)

    rendered = render_text(full_text, data)

    _rewrite_paragraph_text(paragraph, rendered)

