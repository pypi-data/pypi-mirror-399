"""Advanced search parser for Django Admin."""

import re


def parse_advanced_search(text, allowed_fields):
    """Parse search terms using advanced syntax.
    
    Args:
        text (str): The search text to parse
        allowed_fields (list): List of field names that are allowed to be searched
        
    Returns:
        dict: A dictionary containing:
            - has_advanced (bool): Whether advanced search syntax was detected
            - filters (dict): Mapping of field names to (lookup, value) tuples
            - plain_text (str): Any remaining text that wasn't parsed as advanced search
    """
    allowed_fields = set(allowed_fields)
    if not allowed_fields:
        return {'has_advanced': False, 'filters': {}, 'plain_text': text}

    # 正则表达式匹配 field:modifier"value" 或 field:modifier value
    # Groups: 1=field, 2=modifier(==|=|!), 4=quoted_value, 5=unquoted_value
    pattern = r'(\S+?):((?:==|[=!])?)("([^"]*)"|(\S+))'
    filters = {}
    plain_parts = []
    last_end = 0

    for match in re.finditer(pattern, text):
        field = match.group(1)
        modifier = match.group(2) or ''
        quoted_val = match.group(4)
        unquoted_val = match.group(5)
        raw_value = quoted_val or unquoted_val
        start, end = match.span()

        # 只处理允许的字段
        if field not in allowed_fields:
            plain_parts.append(match.group(0))
            continue

        # 根据修饰符确定查找类型
        match modifier:
            case '==':
                lookup, value = 'exact', raw_value
            case '=':
                lookup, value = 'iexact', raw_value
            case '!':
                # 处理带*的值
                if raw_value.startswith('*') and raw_value.endswith('*'):
                    lookup, value = 'contains', raw_value[1:-1]
                elif raw_value.startswith('*'):
                    lookup, value = 'endswith', raw_value[1:]
                elif raw_value.endswith('*'):
                    lookup, value = 'startswith', raw_value[:-1]
                else:
                    lookup, value = 'contains', raw_value
            case _:
                # 处理带*的值
                if raw_value.startswith('*') and raw_value.endswith('*'):
                    lookup, value = 'icontains', raw_value[1:-1]
                elif raw_value.startswith('*'):
                    lookup, value = 'iendswith', raw_value[1:]
                elif raw_value.endswith('*'):
                    lookup, value = 'istartswith', raw_value[:-1]
                else:
                    lookup, value = 'icontains', raw_value

        filters[field] = (lookup, value)
        # 添加匹配之前的普通文本
        plain_parts.append(text[last_end:start].strip())
        last_end = end

    # 添加最后剩余的普通文本
    plain_parts.append(text[last_end:].strip())
    plain_text = ' '.join(p for p in plain_parts if p).strip()

    return {
        'has_advanced': bool(filters),
        'filters': filters,
        'plain_text': plain_text,
    }