"""
Common utilities: nested value lookup and condition evaluation.
"""
import re
import ast
import copy
from typing import Any, Dict


def get_nested_value(data: Dict[str, Any], path: str) -> Any:
    """Get nested value from dict/list using dot path."""
    if not path:
        return None
    copy_data = copy.deepcopy(data)
    # dot_data = DotDict(data)
    keys = path.split('.')
    if not keys:
        return copy_data[keys]
    for i in range(len(keys)):
        copy_data = copy_data.get(keys[i])

    # value = dot_data.get_path(path)
    # keys = path.split(".")
    # value: Any = data
    # for key in keys:
    #     if isinstance(value, dict):
    #         value = value.get(key)
    #     elif isinstance(value, list) and key.isdigit():
    #         idx = int(key)
    #         value = value[idx] if idx < len(value) else None
    #     else:
    #         return None
    #     if value is None:
    #         return None
    return copy_data


def _value_len(val: Any) -> int:
    if hasattr(val, "__len__"):
        try:
            return len(val)  # type: ignore[arg-type]
        except Exception:
            return 0
    return 0

def safe_eval(expr, variables=None):
    if variables is None:
        variables = {}
    
    # 检查AST是否包含危险节点（如函数调用、属性访问）
    tree = ast.parse(expr, mode='eval')
    for node in ast.walk(tree):
        if isinstance(node, (ast.Call, ast.Attribute)):
            raise ValueError("Unsafe expression")
    
    # 编译并执行
    code = compile(tree, '<string>', 'eval')
    return eval(code, {'__builtins__': {}}, variables)

def evaluate_condition(condition: str, data: Dict[str, Any]) -> bool:
    """
    Evaluate simple condition expressions used in templates.

    Supported:
    - == null / != null
    - == '' / != ''
    - size() > 0
    - && / ||
    - truthy check of a field
    """
    condition = condition.strip()
    if not condition:
        return False

    # Logical AND / OR
    # if "&&" in condition:
    #     return all(evaluate_condition(part, data) for part in condition.split("&&"))
    # if "||" in condition:
    #     return any(evaluate_condition(part, data) for part in condition.split("||"))

    # size() > 0
    size_match = re.match(r"(.+)\.size(.*?)$", condition)
    eq_match = re.match(r"(.+)\s*==\s*(.*?)$", condition)
    not_in_match = re.match(r"(.+)\s* not in \s*(.*?)$", condition)
    if size_match:
        field = size_match.group(1).strip()
        field2 = size_match.group(2).strip()
        val = get_nested_value(data, field)
        return safe_eval(f"{_value_len(val)}{field2}") 
    elif eq_match:
        field = eq_match.group(1).strip()
        field2 = eq_match.group(2).strip()
        val = get_nested_value(data, field)
        return safe_eval(f"{val}=={field2}") 
    elif not_in_match:
        field = not_in_match.group(1).strip()
        field2 = not_in_match.group(2).strip()
        val = get_nested_value(data, field)
        return safe_eval(f"{val} not in {field2}") 
    # == '' / != ''
    # empty_eq = re.match(r"(.+)==\s*['\"]\s*['\"]", condition)
    # if empty_eq:
    #     field = empty_eq.group(1).strip()
    #     val = get_nested_value(data, field)
    #     return val == "" or val is None

    # empty_neq = re.match(r"(.+)!=\s*['\"]\s*['\"]", condition)
    # if empty_neq:
    #     field = empty_neq.group(1).strip()
    #     val = get_nested_value(data, field)
    #     return val not in ("", None)

    # # == null / != null
    # null_eq = re.match(r"(.+)==\s*null", condition, re.IGNORECASE)
    # if null_eq:
    #     field = null_eq.group(1).strip()
    #     val = get_nested_value(data, field)
    #     return val is None

    # null_neq = re.match(r"(.+)!=( )?null", condition, re.IGNORECASE)
    # if null_neq:
    #     field = null_neq.group(1).strip()
    #     val = get_nested_value(data, field)
    #     return val is not None

    # Direct truthy check
    val = get_nested_value(data, condition)
    return bool(val)


def process_block(text: str, data: Dict[str, Any]) -> str:
    """
    Process conditional blocks {{?condition}}...{{/}}.
    Removes blocks when condition is False; strips tags when True.
    """
    start_pat = r"\{\{\?([^}]+)\}\}"
    end_pat = r"\{\{/\}\}"

    def find_blocks(s: str):
        starts = list(re.finditer(start_pat, s))
        ends = list(re.finditer(end_pat, s))
        return starts, ends

    result = text
    while True:
        starts, ends = find_blocks(result)
        if not starts or not ends:
            break
        # pair first start with nearest end after it (no deep nesting handling)
        start = starts[0]
        end_candidates = [e for e in ends if e.start() > start.end()]
        if not end_candidates:
            break
        end = end_candidates[0]
        inner = result[start.end(): end.start()]
        cond = start.group(1).strip()
        if evaluate_condition(cond, data):
            # keep inner, drop tags
            replacement = inner
        else:
            replacement = ""
        result = result[: start.start()] + replacement + result[end.end():]
    return result

