import json
from datetime import datetime
from pathlib import Path


def dump_json(data, prefix: str = "debug") -> Path:
    """
    将数据以 JSON 格式保存到 debug 目录
    
    Args:
        data: 要保存的数据，可以是 dict 或带有 to_map() 方法的 SDK 响应对象
        prefix: 文件名前缀，默认为 "debug"
    
    Returns:
        保存的文件路径
    """
    debug_dir = Path("debug")
    debug_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = debug_dir / f"{prefix}_{timestamp}.json"

    # 如果是 SDK 响应对象，调用 to_map() 转换
    if hasattr(data, "to_map"):
        data = data.to_map()

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"调试数据已保存到: {output_file}")
    return output_file
