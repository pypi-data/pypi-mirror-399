import sys
from pathlib import Path
# 项目根目录
current_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(current_dir))
import copy
from typing import Any
import pickle
import networkx as nx
from utils.log_output import log_output

class GraphDB:
    def __init__(self):
        log_output.info("GraphDB 初始化")  
        self.graph_db = {}
        self.graph_db_old = {}
        self.old_db_path = "agent/utils/graph_db_old.pkl"
        # self.read_graph_db(self.old_db_path)

    def read_graph_db(self, file_path: str) -> None:
        """
        从文件中读取 graph_db_old 数据。
        """
        log_output.info(f"read_graph_db: 从文件 {file_path} 读取 graph_db_old 数据")
        try:
            with open(file_path, 'rb') as f:
                self.graph_db_old = pickle.load(f)
                print(self.graph_db_old)
        except FileNotFoundError:
            log_output.warning(f"read_graph_db: 文件 {file_path} 不存在")
        except Exception as e:
            log_output.error(f"read_graph_db: 读取文件 {file_path} 时发生错误: {e}")

    def write_graph_db(self, file_path: str) -> None:
        """
        将 graph_db_old 数据写入文件。
        """
        log_output.info(f"write_graph_db: 将 graph_db_old 数据写入文件 {file_path}")
        try:
            with open(file_path, 'wb') as f:
                pickle.dump(self.graph_db, f)
        except Exception as e:
            log_output.error(f"write_graph_db: 写入文件 {file_path} 时发生错误: {e}")

    def update_graph_db(self, flex_algo: str, level: str, ip_version: str, graph: nx.MultiDiGraph) -> None:
        """
        更新 graph_db 中指定 flex_algo、level 和 ip_version 对应的图。
        """
        log_output.info(f"update_graph_db: 参数类型检查 flex_algo={type(flex_algo)}, level={type(level)}, ip_version={type(ip_version)}")
        # 将键转换为字符串
        flex_algo = str(flex_algo)
        level = str(level)
        ip_version = str(ip_version)
        log_output.info(f"update_graph_db: 更新 flex_algo={flex_algo}, level={level}, ip_version={ip_version} 对应的图")
        if flex_algo not in self.graph_db:
            self.graph_db[flex_algo] = {}
        if level not in self.graph_db[flex_algo]:
            self.graph_db[flex_algo][level] = {}
        self.graph_db[flex_algo][level][ip_version] = graph
        print(graph_db)

    def update_graph_db_attr(self, flex_algo: str, level: str, ip_version: str, attr: str, value: Any) -> None:
        """
        更新 graph_db 中指定 flex_algo、level 和 ip_version 对应图的图属性。
        要先确定对应的topo的存在，然后设置nx的图属性
        """
        log_output.info(f"update_graph_db_attr: 参数类型检查 flex_algo={type(flex_algo)}, level={type(level)}, ip_version={type(ip_version)}, attr={type(attr)}")
        # 将键转换为字符串
        flex_algo = str(flex_algo)
        level = str(level)
        ip_version = str(ip_version)
        log_output.info(f"update_graph_db_attr: 更新 flex_algo={flex_algo}, level={level}, ip_version={ip_version} 对应图的属性 {attr}")
        if flex_algo not in self.graph_db or level not in self.graph_db[flex_algo] or ip_version not in self.graph_db[flex_algo][level]:
            log_output.error(f"update_graph_db_attr: flex_algo={flex_algo}, level={level}, ip_version={ip_version} 不存在对应的图")
            return
        graph = self.graph_db[flex_algo][level][ip_version]
        graph.graph[attr] = value

    def get_graph_db_attr(self, graph_db_str: str, flex_algo: str, level: str, ip_version: str, attr: str) -> Any:
        """
        获取 graph_db 中指定 flex_algo、level 和 ip_version 对应图的图属性。
        要先确定对应的topo的存在，然后获取nx的图属性
        """
        # 检查参数类型(一行代码)
        log_output.info(f"get_graph_db_attr: 参数类型检查 flex_algo={type(flex_algo)}, level={type(level)}, ip_version={type(ip_version)}, attr={type(attr)}")
        # 将键转换为字符串
        flex_algo = str(flex_algo)
        level = str(level)
        ip_version = str(ip_version)
        log_output.info(f"get_graph_db_attr: 获取 flex_algo={flex_algo}, level={level}, ip_version={ip_version}, attr={attr}, db={graph_db_str} 对应图的属性")
        # graph_db_tar 只能是 "new" 或 "old"
        if graph_db_str not in ["new", "old"]:
            log_output.error(f"get_graph_db_attr: graph_db_str={graph_db_str} 不是有效的参数，只能是 'new' 或 'old'")
            return None
        if graph_db_str == "old":
            log_output.info(f"get_graph_db_attr: 从old中获取 flex_algo={flex_algo}, level={level}, ip_version={ip_version}, attr={attr}")
            self.read_graph_db(self.old_db_path)
        # 选择对应的 graph_db
        graph_db_tar = self.graph_db if graph_db_str == "new" else self.graph_db_old

        if flex_algo not in graph_db_tar or level not in graph_db_tar[flex_algo] or ip_version not in graph_db_tar[flex_algo][level]:
            log_output.warning(f"get_graph_db_attr: flex_algo={flex_algo}, level={level}, ip_version={ip_version}, graph_db_str={graph_db_str} 不存在对应的图")
            return None
        graph = graph_db_tar[flex_algo][level][ip_version]
        return graph.graph.get(attr, None)

    def update_old_db(self):
        """
        更新 graph_db_old 中所有图的图属性，将 graph_db 中的图属性复制到 graph_db_old 中，并将 graph_db 中的图属性清空。
        """
        self.write_graph_db(self.old_db_path)
        # self.graph_db.clear()
    
    

# graph_db_old = {
#     "128":{
#            "level_1":{
#                "ipv4":"graph_1:nx.MultiDiGraph",
#                "ipv6":"graph_2:nx.MultiDiGraph"
#            },
#         "level_2": {
#             "ipv4": "graph_3:nx.MultiDiGraph",
#             "ipv6": "graph_4:nx.MultiDiGraph"
#         }
#     }
# }


# graph_db = {
#     "128":{
#            "level_1":{
#                "ipv4":"graph_1:nx.MultiDiGraph",
#                "ipv6":"graph_2:nx.MultiDiGraph"
#            },
#         "level_2": {
#             "ipv4": "graph_3:nx.MultiDiGraph",
#             "ipv6": "graph_4:nx.MultiDiGraph"
#         }
#     }
# }
graph_db = GraphDB()


if __name__ == "__main__":
    # graph_db.read_graph_db(graph_db.old_db_path)
    # print(graph_db.graph_db_old)
    print(graph_db.get_graph_db_attr("old", "128", 1, 10, "routes"))
    # 构造一个简单的拓扑图
    # G = nx.MultiDiGraph()
    # G.add_edge('A', 'B', weight=1)
    # G.add_edge('B', 'C', weight=2)
    # G.add_edge('A', 'C', weight=4)
    #
    # # 更新 graph_db 中的图
    # graph_db.update_graph_db(128, 1, 10, G)
    #
    # # 更新图属性
    # graph_db.update_graph_db_attr(128, 1, 10, "routes", "value_1")
    #
    # # 获取图属性
    # attr_value = graph_db.get_graph_db_attr("new", 128, 1, 10, "routes")
    # print(attr_value)  # 输出: value_1
    #
    # # 更新 old_db
    # graph_db.update_old_db()