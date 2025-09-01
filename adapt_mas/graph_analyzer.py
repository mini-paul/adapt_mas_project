# /adapt_mas_project/adapt_mas/graph_analyzer.py

import networkx as nx
from community import community_louvain
from collections import defaultdict
from typing import List, Dict, Tuple


class GraphAnalyzer:
    """实现社交图谱分析，检测合谋团体"""

    def __init__(self, suspicion_threshold: float = 0.7):
        self.suspicion_threshold = suspicion_threshold

    def build_graph(self, interactions: List[Tuple[int, int, float]]):
        """
        构建有向加权图
        interactions: a list of (reviewer_id, reviewee_id, score)
        """
        G = nx.DiGraph()
        for u, v, w in interactions:
            G.add_edge(u, v, weight=w)
        return G

    def detect_collusion(self, G: nx.DiGraph) -> List[List[int]]:
        """
        使用Louvain算法检测社群并计算可疑度
        返回一个列表，每个元素是一个被识别为合谋的团伙
        """
        if G.number_of_nodes() == 0:
            return []

        # Louvain算法需要无向图
        partition = community_louvain.best_partition(G.to_undirected())
        communities = defaultdict(list)
        for agent_id, community_id in partition.items():
            communities[community_id].append(agent_id)

        colluding_groups = []
        for community_id, members in communities.items():
            if len(members) > 1:  # 只考虑2人及以上的团体
                suspicion_score = self._calculate_suspicion_score(G, members)
                if suspicion_score > self.suspicion_threshold:
                    colluding_groups.append(members)

        return colluding_groups

    def _calculate_suspicion_score(self, G: nx.DiGraph, members: List[int]) -> float:
        """
        根据内部凝聚度、外部隔离度、评价偏差度计算社群可疑分
        """
        internal_edges = 0
        internal_weight = 0.0
        external_edges = 0
        external_weight = 0.0

        internal_eval_scores = []
        external_eval_scores = []

        for u in members:
            if u not in G: continue
            for v, data in G[u].items():
                weight = data.get('weight', 0.0)
                if v in members:
                    internal_edges += 1
                    internal_weight += weight
                    internal_eval_scores.append(weight)
                else:
                    external_edges += 1
                    external_weight += weight
                    external_eval_scores.append(weight)

        # 1. 内部凝聚度 (简化为平均内部评价)
        avg_internal_cohesion = (internal_weight / internal_edges) if internal_edges > 0 else 0

        # 2. 外部隔离度 (简化为内外部边数比)
        total_edges = internal_edges + external_edges
        external_isolation_ratio = (internal_edges / total_edges) if total_edges > 0 else 1.0

        # 3. 评价偏差度
        avg_external_eval = (sum(external_eval_scores) / len(external_eval_scores)) if external_eval_scores else 0
        eval_bias = avg_internal_cohesion - avg_external_eval

        # 组合成最终可疑分 (这是一个简化的加权，可以根据实验调优)
        # 内部评价越高、越孤立、内外评价差异越大，则越可疑
        suspicion_score = (
                0.5 * external_isolation_ratio +
                0.3 * (avg_internal_cohesion / 1.0) +  # 假设最高分为1.0
                0.2 * (eval_bias / 2.0)  # 假设最大偏差为2.0 (1 - (-1))
        )
        return max(0.0, min(1.0, suspicion_score))