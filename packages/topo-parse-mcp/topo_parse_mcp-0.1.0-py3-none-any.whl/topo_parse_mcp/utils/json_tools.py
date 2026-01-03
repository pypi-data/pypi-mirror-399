import json
from typing import Union, Dict, List
from utils.log_output import log_output

class JsonOperations:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def load_json(self) -> Union[Dict, List, None]:
        """读取 JSON 文件并返回其内容"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            log_output.error(f"File: {self.file_path} not found.")
            return None
        except json.JSONDecodeError:
            log_output.error("Error decoding JSON.")
            return None

    def save_json(self, data: Union[Dict, List]) -> bool:
        """将数据保存为 JSON 文件"""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            log_output.error(f"Error saving JSON: {e}")
            return False

    def update_json(self, key: str, value: Union[str, int, float, bool, dict, list]) -> bool:
        """更新 JSON 文件中的某个字段"""
        data = self.load_json()
        if data is None:
            return False

        data[key] = value
        return self.save_json(data)

    def delete_key(self, key: str) -> bool:
        """删除 JSON 文件中的某个字段"""
        data = self.load_json()
        if data is None or key not in data:
            return False

        del data[key]
        return self.save_json(data)

    def add_entry(self, key: str, value: Union[str, int, float, bool, dict, list]) -> bool:
        """向 JSON 文件中添加一个新的键值对"""
        data = self.load_json()
        if data is None:
            return False

        data[key] = value
        return self.save_json(data)

    def dumps(obj, **kwargs) -> str:
        """包装标准 json.dumps，方便统一导出（保持与标准 json 一致）。"""
        return json.dumps(obj, **kwargs)


if __name__ == "__main__":
    # 使用示例：
    json_file = 'data.json'
    json_ops = JsonOperations(json_file)

    # 加载数据
    data = json_ops.load_json()
    if data is not None:
        log_output.info("Loaded JSON:", data)

    # 保存数据
    new_data = {'name': 'John', 'age': 30}
    json_ops.save_json(new_data)

    # 更新数据
    json_ops.update_json('age', 31)

    # 删除字段
    json_ops.delete_key('name')

    # 添加新条目
    json_ops.add_entry('city', 'New York')
