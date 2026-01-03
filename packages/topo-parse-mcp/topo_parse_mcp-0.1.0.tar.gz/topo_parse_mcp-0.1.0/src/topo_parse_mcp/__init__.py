"""
- 本文件将原有的 topo_parse_tool 改写为 MCP server 的形式，使用 FastMCP 并通过 @mcp.tool() 暴露工具。
"""
import sys
from pathlib import Path

# 项目根目录加入 sys.path
current_dir = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(current_dir))

from typing import Dict, Any, Optional, List
import os
import networkx as nx

from utils.json_tools import JsonOperations
from utils.log_output import log_output
from utils.topo_graph import TopoGraph
from utils.globals import GLOBAL_STATE

# MCP server 导入
from mcp.server.fastmcp import FastMCP

# 创建 MCP server 实例，名字可按需调整
mcp = FastMCP("TopoParse")


# 拓扑解析
class TopologyParser:
    """
    从 JSON 拓扑文件构建 TopoGraph（基于 networkx.MultiDiGraph），
    并对外提供拓扑文本视图与 Flex-Algo 视图访问接口。
    """

    def __init__(self) -> None:
        # 使用 TopoGraph 管理底层 networkx 图
        self.topo = TopoGraph()

    def build_graph_from_json(self, json_path: str) -> None:
        """
        从 JSON 文件构建内部拓扑图结构。
        """
        if not os.path.exists(json_path):
            log_output.error("build_graph_from_json: 文件不存在: %s", json_path)
            raise FileNotFoundError(json_path)

        json_ops = JsonOperations(json_path)
        topo_json = json_ops.load_json()
        log_output.debug("build_graph_from_json: 已加载 JSON 文件: %s", json_path)

        topo_info = topo_json.get("topo info", {})
        nodes = topo_info.get("nodes", [])
        links = topo_info.get("links", [])

        # 从 nodes 中提取 flex_algo 定义（相同 ID 保留 priority 更高的）
        flex_algo_map = {}
        for node in nodes:
            for algo in node.get("flex_algos", []):
                algo_id = algo["flex_algo"]
                if (
                    algo_id not in flex_algo_map
                    or algo["priority"] > flex_algo_map[algo_id]["priority"]
                ):
                    flex_algo_map[algo_id] = algo
        flex_algos = list(flex_algo_map.values())

        # 重新初始化 TopoGraph
        self.topo = TopoGraph()

        # 添加节点
        for n in nodes:
            try:
                self.topo.add_node(n)
            except Exception:
                log_output.warning("build_graph_from_json: 添加节点出错：%s", n)

        # 添加链路
        for l in links:
            try:
                self.topo.add_link(l)
            except Exception:
                log_output.warning("build_graph_from_json: 添加链路出错：%s", l)

        # 添加 Flex-Algo 信息
        try:
            self.topo.add_flex_algos(flex_algos)
        except Exception:
            log_output.warning("build_graph_from_json: 保存 flex_algos 数据出错")

        log_output.debug(
            "build_graph_from_json: 构建完成 nodes=%d edges=%d",
            self.topo.get_graph().number_of_nodes(),
            self.topo.get_graph().number_of_edges(),
        )

    # 访问 / 导出 接口
    def get_graph(self) -> nx.MultiDiGraph:
        # 返回内部 networkx 图对象
        return self.topo.get_graph()

    def get_topo_prompt(self, flex_algo: Optional[int] = None) -> str:

        # 参数 flex_algo：可选，若提供则返回 Flex-Algo 的子拓扑视角，否则提供完整拓扑
        return self.topo.generate_topo_prompt(flex_algo=flex_algo)

    def get_flex_algo_prompt(self, flex_algo: Optional[int] = None) -> str:

        # 返回 Flex-Algo 定义文本。若传入 flex_algo（整数），只返回对应的定义；否则返回全部定义。
        return self.topo.get_graph_flex_algo_prompt(flex_algo=flex_algo)

    def get_nodes(self) -> List[Dict[str, Any]]:
        # 返回节点列表（每项包含 system_id 与属性）
        return self.topo.get_nodes()

    def get_links(self) -> List[Dict[str, Any]]:
        # 返回链路列表（每条有向边为一条记录）
        return self.topo.get_links()

    def get_flex_algos(self) -> List[Dict[str, Any]]:
        # 返回解析到的 flex_algos 列表，若无返回空列表"""
        return self.topo.get_flex_algos()


# MCP Tool 暴露
@mcp.tool()
def topo_parse_mcp_tool(flex_algo_id: Optional[int] = None) -> str:
    """
    描述:
        解析当前网络拓扑 JSON 文件，可选指定 Flex-Algo ID 以获取对应的算法拓扑。
        构建网络拓扑结构，并以文本形式返回拓扑信息与 Flex-Algo 定义。
        - 当 flex_algo_id 为 None 时：
            返回完整拓扑视图 + 全量 Flex-Algo 定义。
        - 当 flex_algo_id 为指定整数时：
            返回该 Flex-Algo 的算法定义 + 对应的子拓扑视角。

    参数:
        flex_algo_id (Optional[int], 默认 None)
            Flex-Algo 算法的唯一编号（非负整数）。
            - None：返回全量网络拓扑与默认（ID=0）算法定义。
            - 整数：返回该 Flex-Algo 编号对应的算法定义及适用拓扑。
            - 若编号不存在，可能返回空或默认信息。

    返回:
        str:
            文本内容，当工具成功调用时，以“topo_parse_mcp_tool工具调用成功，结果是：”为起始，并按顺序拼接以下信息：
            1. Flex-Algo 算法定义（包括 id、MetricType、CalcType 等核心字段）
            2. 拓扑信息（节点、链路关系及属性，匹配指定算法的范围）
    """
    log_output.info("llm begins to call tool: topo_parse_mcp_tool")
    log_output.info("flex_algo_id: %s", flex_algo_id)

    topo_parser = TopologyParser()
    topo_parser.build_graph_from_json(json_path=GLOBAL_STATE.topo_path)
    flex_algo_prompt_text = topo_parser.get_flex_algo_prompt(flex_algo=flex_algo_id)
    topo_prompt_text = topo_parser.get_topo_prompt(flex_algo=flex_algo_id)

    result = (
        "topo_parse_mcp_tool工具调用成功，结果是：\n"
        f"{flex_algo_prompt_text}\n"
        f"{topo_prompt_text}"
    )

    log_output.info("llm finished call tool: topo_parse_mcp_tool")
    return result


def main() -> None:
    mcp.run(transport="stdio")
