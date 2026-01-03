import json
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def middle_ellipsis(s: str, max_len: int, ellipsis: str = "…") -> str:
    if len(s) <= max_len:
        return s
    if max_len <= len(ellipsis):
        # Not enough room for content, just return ellipsis or truncated ellipsis
        return ellipsis[:max_len]

    # How many chars from start and end
    keep = max_len - len(ellipsis)
    front = keep // 2
    back = keep - front
    return s[:front] + ellipsis + s[-back:]

#
# prettyprint helper for long JSON
#
def middle_ellipsis_in_json(obj, max_len=40):
    """

    example usage
    pretty = json.dumps(middle_ellipsis_in_json(data, max_len=40), indent=2, ensure_ascii=False)
    print(pretty)
    """
    if isinstance(obj, str):
        return middle_ellipsis(obj, max_len)
    if isinstance(obj, list):
        return [middle_ellipsis_in_json(x, max_len) for x in obj]
    if isinstance(obj, dict):
        return {k: middle_ellipsis_in_json(v, max_len) for k, v in obj.items()}
    return obj
