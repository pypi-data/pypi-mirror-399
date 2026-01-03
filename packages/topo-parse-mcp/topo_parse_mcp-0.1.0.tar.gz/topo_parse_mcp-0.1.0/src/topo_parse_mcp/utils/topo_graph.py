"""
 - 封装 networkx.MultiDiGraph 的构建、查询与 Prompt 生成逻辑
"""
import sys
from pathlib import Path
# 项目根目录
current_dir = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(current_dir))

from typing import Dict, Any, List, Optional
import networkx as nx
from utils.log_output import log_output
from utils.graph_db import graph_db
from utils.globals import GLOBAL_STATE


class TopoGraph:
    def __init__(self):
        # 使用 MultiDiGraph 以支持有向边
        self.graph = nx.MultiDiGraph()
        log_output.debug("TopoGraph: 初始化 MultiDiGraph（实例名 graph）")

    # 向图中添加节点
    def add_node(self, node: Dict[str, Any]) -> Optional[str]:

        # 必须包含 'system_id'，其余字段作为节点属性保存（并保留原始 _raw）
        sid = node.get("system_id")
        if not sid:
            log_output.warning("add_node: 缺少 system_id，跳过节点：%s", node)
            return None

        # 复制属性并保留 _raw
        attrs = dict(node)
        attrs.pop("system_id", None)
        attrs["_raw"] = dict(node)

        if sid in self.graph.nodes:
            # 合并属性：以新值覆盖旧值
            self.graph.nodes[sid].update(attrs)
            log_output.debug("add_node: 更新已存在节点 %s, 属性数=%d", sid, len(self.graph.nodes[sid]))
        else:
            self.graph.add_node(sid, **attrs)
            log_output.debug("add_node: 添加节点 %s, 属性数=%d", sid, len(attrs))

        return sid

    # 向图中添加链路
    def add_link(self, link: Dict[str, Any]) -> Optional[tuple]:
        """
        注意：
            - 不再自动添加反向边。
            - 若需要双向链路，请在 JSON 中显式定义两条（local->remote 与 remote->local）。
        """
        # 提取端点,支持字段兼容：local_system_id/local_id 表示源，remote_system_id/remote_id 表示目的。
        u = link.get("local_system_id") or link.get("local_id")
        v = link.get("remote_system_id") or link.get("remote_id")
        if not u or not v:
            log_output.warning("add_link: 缺少 local/remote，跳过链路：%s", link)
            return None

        # 构造属性字典（移除端点字段并保留 _raw）
        attrs = dict(link)
        for f in ("local_system_id", "local_id", "remote_system_id", "remote_id"):
            attrs.pop(f, None)
        attrs["_raw"] = dict(link)

        # 若节点不存在则隐式添加
        if not self.graph.has_node(u):
            self.graph.add_node(u, _implicit=True)
            log_output.debug("add_link: 隐式添加源节点 %s", u)
        if not self.graph.has_node(v):
            self.graph.add_node(v, _implicit=True)
            log_output.debug("add_link: 隐式添加目标节点 %s", v)
        
        # 判断边的类型：真节点到伪节点、真节点到真节点（p2p）、伪节点到真节点
        if u.endswith(".00") and v.endswith(".00"):
            # 真节点到真节点（p2p）
            edge_type = "p2p"
        elif u.endswith(".00"):
            # 真节点到伪节点
            edge_type = "to_dis"
        else:
            # 伪节点到真节点
            edge_type = "from_dis"
        attrs["edge_type"] = edge_type
        # 添加单向边 u -> v
        self.graph.add_edge(u, v, **dict(attrs))
        log_output.debug("add_link: 添加边 %s -> %s attrs_keys=%s", u, v, list(attrs.keys()))

        return (u, v)

    # 将前缀列表保存为图级元数据
    def add_prefixes(self, prefixes: Optional[List[Dict[str, Any]]]) -> None:
        """将前缀列表写入 self.graph.graph['ipv6 prefixes']（始终为列表）。"""
        if prefixes is None:
            self.graph.graph["ipv6 prefixes"] = []
            log_output.debug("add_prefixes: 保存前缀 count=0")
            return  # <-- 加上 return，避免覆盖

        self.graph.graph["ipv6 prefixes"] = prefixes
        log_output.debug("add_prefixes: 保存前缀 count=%d", len(prefixes))

    def add_flex_algos(self, flex_algos: Optional[List[Dict[str, Any]]]) -> None:
        # 将 flex_algos 列表保存为图级元数据 self.graph.graph['flex_algos']。
        if flex_algos is None:
            self.graph.graph["flex_algos"] = []
            log_output.debug("add_flex_algos: 保存 flex_algos count=0")
            return

        self.graph.graph["flex_algos"] = flex_algos
        log_output.debug("add_flex_algos: 保存 flex_algos count=%d", len(flex_algos))

    # 访问 / 导出 接口
    def get_graph(self) -> nx.MultiDiGraph:
        # 返回底层 networkx 图对象引用（供外部直接使用 networkx API）
        return self.graph

    def get_nodes(self) -> List[Dict[str, Any]]:

        # 返回节点列表（每项为 dict，包含 'system_id' 与节点属性，保留 '_raw'）。
        res: List[Dict[str, Any]] = []
        for n, attrs in self.graph.nodes(data=True):
            item = {"system_id": n}
            item.update(dict(attrs))
            res.append(item)
        return res

    def get_links(self) -> List[Dict[str, Any]]:

        # 返回链路列表（每条有向边一条记录）。每个记录为 dict，包含 'src'/'dst' 与边属性（包括 _raw）。
        res: List[Dict[str, Any]] = []
        for u, v, ed in self.graph.edges(data=True):
            rec = {"src": u, "dst": v}
            rec.update(dict(ed))
            res.append(rec)
        return res

    def get_prefixes(self) -> List[Dict[str, Any]]:
        """返回保存的前缀列表（始终为列表，防止外部修改原对象）。"""
        try:
            prefixes = self.graph.graph.get("ipv6 prefixes", [])
            return list(prefixes)
        except Exception:
            log_output.exception("get_prefixes: 内部 prefixes 格式异常，返回空列表")
            return []

    def get_flex_algos(self) -> List[Dict[str, Any]]:
        """返回保存的 flex_algos 列表（始终为列表，防止外部修改原对象）。"""
        try:
            flex_algos = self.graph.graph.get("flex_algos", [])
            return list(flex_algos)
        except Exception:
            log_output.exception("get_flex_algos: 内部 flex_algos 格式异常，返回空列表")
            return []

    # 辅助：位掩码规范化与匹配函数
    # 将十六进制字符串形式存储的“掩码槽位”值（例如 "0x10000000"）转换为整数，便于后续按位运算（AND/比较）。
    def _hex_to_int(self, s: Optional[str]) -> int:
        if s is None or s == "":
            return 0
        if isinstance(s, int):
            return int(s)
        try:
            # int(..., 0) 自动识别 0x 前缀
            return int(str(s), 0)
        except Exception:
            # 回退：尝试仅解析为十六进制（去掉 0x 前缀如果存在）
            try:
                ss = str(s).strip().lower()
                if ss.startswith("0x"):
                    ss = ss[2:]
                return int(ss, 16)
            except Exception:
                try:
                    return int(str(s))
                except Exception:
                    return 0

    def _matches_exclude_any(self, edge_masks: List[int], excl_masks: List[int]) -> bool:
        """
        - 如果 FAD 的任一 exclude mask 与 edge 的任一 slot 按位 AND 非零 -> 排除。
        """
        # 若没有排除掩码，直接返回 False（不排除）
        if not excl_masks:
            return False

        # 确保输入为整数列表（兼容传入 hex/str 的情况）
        try:
            em = [x if isinstance(x, int) else self._hex_to_int(str(x)) for x in edge_masks]
        except Exception:
            em = [self._hex_to_int(str(x)) for x in edge_masks or []]

        try:
            ex = [x if isinstance(x, int) else self._hex_to_int(str(x)) for x in excl_masks]
        except Exception:
            ex = [self._hex_to_int(str(x)) for x in excl_masks or []]

        # 任意对任意交叉比较
        for e_val in em:
            for ex_val in ex:
                if (e_val & ex_val) != 0:
                    return True
        return False

    def _matches_include_any(self, edge_masks: List[int], inc_masks: List[int]) -> bool:
        """
        - 如果 inc_masks 全为0（视为未设置），返回 False（不强制包含）。
        - 只要存在 edge 的任一 slot 与 inc_masks 的任一 slot 按位 AND 非零，则通过（包含）。
        """
        # 若 inc_masks 全为 0 或为空，视为未设置 -> 返回 False (不强制包含)
        if not any(inc_masks):
            return False

        # 转为整数列表（兼容 hex/string）
        try:
            em = [x if isinstance(x, int) else self._hex_to_int(str(x)) for x in edge_masks]
        except Exception:
            em = [self._hex_to_int(str(x)) for x in edge_masks or []]

        try:
            im = [x if isinstance(x, int) else self._hex_to_int(str(x)) for x in inc_masks]
        except Exception:
            im = [self._hex_to_int(str(x)) for x in inc_masks or []]

        # 任意对任意交叉比较：只要有一对 (e & i) != 0 则匹配
        for e_val in em:
            for i_val in im:
                if (e_val & i_val) != 0:
                    return True
        return False

    def _matches_include_all(self, edge_masks: List[int], inc_masks: List[int]) -> bool:
        """
        - 若 inc_masks 全为 0（未设置），返回 True（等同于无约束）。
        - 对于每个非零的 inc_mask 元素，要求 edge 的任一 slot 与之按位 AND 非零（即每个要求项都必须在 edge 的某个槽位上被满足）。
        - 这是把“每个非零的 inc_mask slot 都必须被满足”的语义改为跨槽位检查。
        """
        if not any(inc_masks):
            return True

        # 转为整数列表（兼容 hex/string）
        try:
            em = [x if isinstance(x, int) else self._hex_to_int(str(x)) for x in edge_masks]
        except Exception:
            em = [self._hex_to_int(str(x)) for x in edge_masks or []]

        try:
            im = [x if isinstance(x, int) else self._hex_to_int(str(x)) for x in inc_masks]
        except Exception:
            im = [self._hex_to_int(str(x)) for x in inc_masks or []]

        # 对每个非零的 inc_mask，检查 edge 的任一 slot 是否满足
        for req in im:
            if req == 0:
                continue
            satisfied = False
            for e_val in em:
                if (e_val & req) != 0:
                    satisfied = True
                    break
            if not satisfied:
                return False
        return True

    # Flex-Algo 子拓扑筛选
    def get_flexalgo_subgraph(self, algo_id: int) -> nx.MultiDiGraph:
        """
        根据指定 flex-algo id 构造子拓扑（包含匹配边及其端点）。
        - 优先检查边的 'flex_algo' 字段（显式标注），若等于 algo_id 则通过。
        - 若存在 FAD（self.graph.graph['flex_algos'] 中的条目），按 Exclude/Include 掩码用位运算匹配。
        - 若未找到对应的 FAD（algo_id 未定义），则不会依据掩码做“默认包含”——
          仅允许边上显式标注 flex_algo == algo_id 的边通过（更安全的默认策略）。
        """
        fad = None
        for f in self.graph.graph.get("flex_algos", []):
            try:
                if int(f.get("flex_algo", -1)) == int(algo_id):
                    fad = f
                    break
            except Exception:
                continue
        H = nx.MultiDiGraph()
        # 复制节点属性（子图保留全部节点属性）
        for n, attrs in self.graph.nodes(data=True):
            H.add_node(n, **dict(attrs))

        # 预处理 FAD 的掩码（保存为 int 列表）
        excl_masks = []
        inc_any_masks = []
        inc_all_masks = []
        if fad:
            excl_masks = [self._hex_to_int(x) for x in (fad.get("exclude-any") or [])]
            inc_any_masks = [self._hex_to_int(x) for x in (fad.get("include-any") or [])]
            inc_all_masks = [self._hex_to_int(x) for x in (fad.get("include-all") or [])]
        def edge_matches(edata: Dict[str, Any]) -> bool:
            # 1) edge 指定 flex_algo 优先处理（显式标注优先）
            if edata.get("flex_algo") is not None:
                try:
                    return int(edata.get("flex_algo")) == int(algo_id)
                except Exception:
                    return False

            # 2) 如果没有找到 FAD（即 algo_id 未在 flex_algos 列表中定义）
            #    则不做掩码匹配（仅允许显式标注的边通过，上面已返回），直接返回 False。
            if fad is None:
                return False

            # 3) 规范化边上的 ext_admin_group（可能为 None / list / string / int）
            edge_masks_raw = edata.get("ext_admin_group") or []
            if isinstance(edge_masks_raw, (str, int)):
                edge_masks_list = [edge_masks_raw]
            elif isinstance(edge_masks_raw, list):
                edge_masks_list = edge_masks_raw
            else:
                edge_masks_list = []

            edge_masks_ints = [self._hex_to_int(x) for x in edge_masks_list]

            # Exclude-any 优先：任意 slot 按位与非零 -> 排除
            if self._matches_exclude_any(edge_masks_ints, excl_masks):
                return False

            # Include-any：若有定义且任一 slot 匹配则通过；若定义了 include_any 但未匹配 -> 排除
            if any(inc_any_masks):
                if not self._matches_include_any(edge_masks_ints, inc_any_masks):
                    return False

            # Include-all：若有定义则要求每个非零 slot 都被满足
            if any(inc_all_masks):
                if not self._matches_include_all(edge_masks_ints, inc_all_masks):
                    return False

            # 通过所有检查
            return True

        # 筛选边并加入 H
        for u, v, ed in self.graph.edges(data=True):
            try:
                # 1) 优先策略：如果边的源节点是 IS-IS DIS node，
                #    则不做任何 flex-algo 掩码匹配，直接包含到子拓扑中。
                #    这样保证以 DIS 为源(local_system_id)的链路始终进入子拓扑。
                src_node_attrs = self.graph.nodes.get(u, {}) if hasattr(self.graph, "nodes") else {}
                if src_node_attrs and src_node_attrs.get("node_type") == "IS-IS dis node":
                    H.add_edge(u, v, **dict(ed))
                    continue

                # 2) 否则按原来的掩码/显式 flex_algo 逻辑判断
                if edge_matches(ed):
                    H.add_edge(u, v, **dict(ed))
                    # # 如果是真->伪类型的边（to_dis），则把对应的伪->真边也加入
                    # if ed.get("edge_type") == "to_dis" and self.graph.has_edge(v, u):
                    #     edge_dict = self.graph.get_edge_data(v, u)
                    #     for rev_attrs in edge_dict.values():
                    #         # 确保反向边的类型是 from_dis
                    #         if rev_attrs.get("edge_type") == "from_dis":
                    #             H.add_edge(v, u, **dict(rev_attrs))
            except Exception as e:
                log_output.exception("get_flexalgo_subgraph: 评估边是否匹配时出错: %s->%s, 错误信息: %s", u, v, str(e))

        log_output.debug("get_flexalgo_subgraph: algo=%s nodes=%d edges=%d", algo_id, H.number_of_nodes(),
                         H.number_of_edges())
        return H

    # Prompt 生成（确保字段覆盖原始 JSON 中出现的所有重要字段）
    def get_graph_nodes_prompt(self, graph: Optional[nx.MultiDiGraph] = None) -> str:
        """
        生成节点清单部分。若传入 graph，则基于该 graph 输出；否则基于 self.graph。
        子拓扑时默认只列出 graph 中 degree>0 的节点（避免列出孤立的隐式节点）。
        输出格式：system_id:{sid}, node_type:{node_type}, local_te_router_id:{te_router}, topo_ids=[...]
        """
        lines: List[str] = []
        lines.append("=== node列表 ===")

        target_graph = graph if graph is not None else self.graph

        # 遍历目标图的节点
        for n, attrs in target_graph.nodes(data=True):
            # 若是子图并且希望只列出有边的节点，可通过 degree 判断
            if graph is not None:
                # 只输出 degree > 0 的节点（有连接的节点）
                if target_graph.degree(n) == 0:
                    continue

            sid = n
            node_type = attrs.get("node_type") if attrs.get("node_type") is not None else "N/A"
            te_router = attrs.get("local_te_router_id") if attrs.get("local_te_router_id") is not None else "N/A"
            topo_ids = attrs.get("topology_ids") or []

            lines.append(
                f"system_id:{sid}, node_type:{node_type}, local_te_router_id:{te_router}, topo_ids={topo_ids}"
            )

        lines.append("")
        return "\n".join(lines)

    def get_graph_links_prompt(self, graph: Optional[nx.MultiDiGraph] = None) -> str:
        """
        生成链路清单部分。若传入 graph，则基于该 graph 输出；否则基于 self.get_links()（兼容原逻辑）。
        输出格式与主拓扑一致：
        source_system_id:{src}, dest_system_id:{dst}, interface_address:{iface}, ipv6_local_address:{ipv6}, ...
        """
        lines: List[str] = []
        lines.append("=== link列表 ===")

        if graph is None:
            # 使用已有 get_links() 保持旧逻辑与兼容性
            for l in self.get_links():
                src = l.get("src")
                dst = l.get("dst")
                iface = l.get("interface_address") or l.get("InterfaceAddress") or "N/A"
                ipv4 = l.get("ipv4_local_address") or l.get("ipv4LocalAddress") or "N/A"
                ipv6 = l.get("ipv6_local_address") or l.get("ipv6LocalAddress") or "N/A"
                local_te = l.get("local_te_router_id") or "N/A"
                igp = l.get("igp_metric")
                te = l.get("te_metric")
                delay = l.get("delay")
                # mn = l.get("min_delay_us")
                # mx = l.get("max_delay_us")

                # lines.append(
                #     f"source_system_id:{src}, dest_system_id:{dst}, interface_address:{iface}, ipv6_local_address:{ipv6}, local_te_router_id:{local_te}, "
                #     f"igp_cost:{igp}, te_cost:{te}, min_delay_us:{mn}, max_delay_us:{mx}"
                # )
                lines.append(
                    f"source_system_id:{src}, dest_system_id:{dst}, ipv6_local_address:{ipv6}, local_te_router_id:{local_te}, "
                    f"igp_cost:{igp}, te_cost:{te}, delay:{delay}"
                )
        else:
            # 基于传入的子图 graph 输出（edges(data=True)）
            for u, v, ed in graph.edges(data=True):
                src = u
                dst = v
                iface = ed.get("interface_address") or ed.get("InterfaceAddress") or "N/A"
                ipv4 = ed.get("ipv4_local_address") or ed.get("ipv4LocalAddress") or "N/A"
                ipv6 = ed.get("ipv6_local_address") or ed.get("ipv6LocalAddress") or "N/A"
                local_te = ed.get("local_te_router_id") or "N/A"
                igp = ed.get("igp_metric")
                te = ed.get("te_metric")
                delay = ed.get("delay")
                # mn = ed.get("min_delay_us")
                # mx = ed.get("max_delay_us")

                # lines.append(
                #     f"source_system_id:{src}, dest_system_id:{dst}, interface_address:{iface}, ipv6_local_address:{ipv6}, local_te_router_id:{local_te}, "
                #     f"igp_metric:{igp}, te_metric:{te}, min_delay_us:{mn}, max_delay_us:{mx}"
                # )

                lines.append(
                    f"source_system_id:{src}, dest_system_id:{dst}, ipv6_local_address:{ipv6}, local_te_router_id:{local_te}, "
                    f"igp_cost:{igp}, te_cost:{te}, delay:{delay}"
                )

        lines.append("")
        return "\n".join(lines)
    
    def add_graph_attr(self, attrs: Dict[str, Any]):
        """
        添加图属性到 self.graph。
        """
        self.graph.graph.update(attrs)

    def get_graph_prefixs_prompt(self, dest_system_id: Optional[str] = None, flex_algo_id: Optional[int] = None) -> str:
        """
        如果传入 dest_system_id，则只输出那些 origin_system_id == dest_system_id 的前缀。
        如果传入 flex_algo_id，则只输出那些 prefix 的 algorithm == flex_algo_id 的前缀。
        两个过滤器同时传入时，需同时满足才会输出。
        """
        lines: List[str] = []
        lines.append("=== ipv6 prefix列表 ===")
        prefixes = self.get_prefixes()

        if not prefixes:
            lines.append("无前缀信息")
            lines.append("")
            return "\n".join(lines)

        # 过滤函数：判断 prefix 的 origin 是否与目标匹配
        def origin_matches(p: Dict[str, Any], dest: str) -> bool:
            origin = p.get("system_id") or p.get("origin_system_id")
            if origin is None:
                return False
            return str(origin) == str(dest)

        # 过滤函数：判断 prefix 的 algorithm 是否与目标 flex_algo 匹配
        def algorithm_matches(p: Dict[str, Any], algo: int) -> bool:
            # 兼容多种命名
            alg_val = p.get("algorithm")
            if alg_val is None:
                alg_val = p.get("algo")
            if alg_val is None:
                alg_val = p.get("Algorithm")
            if alg_val is None:
                return False
            try:
                return int(alg_val) == int(algo)
            except Exception:
                # 试着比较字符串形式（稳健回退）
                return str(alg_val) == str(algo)

        matched_any = False
        for p in prefixes:
            if isinstance(p, dict):
                # 如果传了 dest_system_id，但 origin 不匹配 -> 跳过
                if dest_system_id is not None and not origin_matches(p, dest_system_id):
                    continue
                # 如果传了 flex_algo_id，但 algorithm 不匹配 -> 跳过
                if flex_algo_id is not None and not algorithm_matches(p, flex_algo_id):
                    continue

                pr = p.get("prefix") or p.get("Prefix") or "<unknown>"
                sid = p.get("system_id") or p.get("origin_system_id") or None
                metric = p.get("metric", p.get("prefix_metric", None))
                tlv_type = p.get("tlv_type")
                algo_field = p.get("algorithm") or p.get("algo") or p.get("Algorithm")
                lines.append(
                    f"address:{pr}, origin_system_id:{sid}, metric:{metric}, algorithm:{algo_field}, tlv_type:{tlv_type}")
                matched_any = True
            else:
                # 非 dict 的条目，只在未指定 dest_system_id 和未指定 flex_algo_id 时输出（与原逻辑保持一致）
                if dest_system_id is None and flex_algo_id is None:
                    lines.append(f"- {p}")
                    matched_any = True

        if not matched_any:
            lines.append("无符合条件的前缀信息")

        lines.append("")
        return "\n".join(lines)

    def get_graph_flex_algo_prompt(self, flex_algo: Optional[int] = None) -> str:
        """
        生成 Flex-Algo 定义部分的 Prompt。
        - 若 flex_algo 为 None 或 0，输出全部 flex_algos（默认行为）
        - 若 flex_algo 为非零整数，只输出该 ID 对应的一条定义；
          若找不到，输出提示信息。
        """
        lines: List[str] = []
        lines.append("=== Flex-Algo 定义 ===")

        # 使用统一的 get_flex_algos 接口
        flex_algos = self.get_flex_algos()
        if not flex_algos:
            lines.append("无 Flex-Algo 定义")
            lines.append("")
            return "\n".join(lines)

        # MetricType 含义映射表
        metric_type_map = {
            0: "igp_metric",
            1: "delay",
            2: "te_metric",
        }

        # 情况1：未传参数 或 传入 0 → 输出全部定义
        if flex_algo is None or int(flex_algo) == 0:
            for f in flex_algos:
                if not isinstance(f, dict):
                    continue
                algo_id = f.get("flex_algo", "N/A")
                metric_type = f.get("metric_type", "N/A")
                calc_type = f.get("calc_type", "N/A")
                try:
                    mt_int = int(metric_type)
                    metric_type_str = metric_type_map.get(mt_int, f"未知类型({mt_int})")
                except Exception:
                    metric_type_str = str(metric_type)
                lines.append(f"flex_algo:{algo_id}, metric_type:{metric_type_str}, calc_type:{calc_type}")
            lines.append("")  # 结尾空行
            return "\n".join(lines)

        # 情况2：传入非零整数 → 只输出对应定义
        found = False
        try:
            flex_algo_int = int(flex_algo)
        except Exception:
            lines.append(f"- 参数 flex_algo={flex_algo} 无效，应为整数")
            lines.append("")
            return "\n".join(lines)

        for f in flex_algos:
            if not isinstance(f, dict):
                continue
            try:
                if int(f.get("flex_algo", -1)) == flex_algo_int:
                    found = True
                    algo_id = f.get("flex_algo", "N/A")
                    metric_type = f.get("metric_type", "N/A")
                    calc_type = f.get("calc_type", "N/A")
                    try:
                        mt_int = int(metric_type)
                        metric_type_str = metric_type_map.get(mt_int, f"未知类型({mt_int})")
                    except Exception:
                        metric_type_str = str(metric_type)
                    lines.append(f"flex_algo:{algo_id}, metric_type:{metric_type_str}, calc_type:{calc_type}")
                    break
            except Exception:
                continue

        if not found:
            lines.append(f"- 未找到 flex_algo={flex_algo} 的定义")
        lines.append("")  # 结尾空行
        return "\n".join(lines)

    def generate_topo_prompt(self, flex_algo: Optional[int] = None) -> str:
        """
        生成并返回 Prompt（字符串）。
        - 当 flex_algo is None 或 flex_algo == 0：输出原始完整拓扑（nodes + links）。
        - 当 flex_algo 为非零整数且存在对应的 FAD 定义或链路标注：输出该 flex-algo 的子拓扑（nodes + links）。
        - 当 flex_algo 为非零整数但不存在对应定义且链路也无该标注：返回子拓扑为空的提示（不输出完整拓扑）。
        """
        lines: List[str] = []
        if flex_algo is None or int(flex_algo) == 0:
            # 只输出主图（完整拓扑）
            lines.append(self.get_graph_nodes_prompt())
            lines.append(self.get_graph_links_prompt())
            # 在graph_db的对应flex_algo_id下，根据ipv4和ipv6分别存储
            print(type(flex_algo))
            graph_db.update_graph_db(flex_algo, GLOBAL_STATE.level, GLOBAL_STATE.family, self.graph)
        else:
            # 只输出子拓扑（并保证格式与主图一致）
            try:
                fa_id = int(flex_algo)
                sub = self.get_flexalgo_subgraph(fa_id)
                lines.append(f"=== Flex-Algo {fa_id} 拓扑 ===")
                # 传入子图以复用相同的格式化逻辑
                lines.append(self.get_graph_nodes_prompt(graph=sub))
                lines.append(self.get_graph_links_prompt(graph=sub))
                # 在graph_db的对应flex_algo_id下，根据ipv4和ipv6分别存储
                print(type(flex_algo))
                # flex_algo = str(flex_algo)
                graph_db.update_graph_db(flex_algo, GLOBAL_STATE.level, GLOBAL_STATE.family, sub)
            except Exception:
                log_output.exception("generate_topo_prompt: 生成 flex 子拓扑时出错: %s", flex_algo)

        return "\n".join(lines)


