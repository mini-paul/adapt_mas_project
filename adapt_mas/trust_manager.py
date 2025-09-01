# /adapt_mas_project/adapt_mas/trust_manager.py

from collections import defaultdict
from typing import List

class TrustManager:
    """实现动态信任模型"""
    def __init__(self, agent_ids: List[int], learning_rate: float):
        self.alpha = learning_rate
        # 结构: {agent_id: {context: trust_score}}
        self.trust_scores = {agent_id: defaultdict(lambda: 0.5) for agent_id in agent_ids}

    def update_trust(self, agent_id: int, context: str, new_evidence: float):
        """
        根据公式 TSi,c,t = (1 - α) * TSi,c,t-1 + α * NewEvidencet 更新信任分
        new_evidence 范围应在 [-1, 1]
        """
        current_ts = self.trust_scores[agent_id][context]
        new_evidence_clipped = max(-1.0, min(1.0, new_evidence)) # 确保范围
        new_ts = (1 - self.alpha) * current_ts + self.alpha * new_evidence_clipped
        self.trust_scores[agent_id][context] = new_ts

    def get_trust_score(self, agent_id: int, context: str) -> float:
        return self.trust_scores[agent_id][context]

    def penalize_group(self, agent_ids: List[int], context: str, factor: float):
        """对一个团体进行集体性的信任惩罚"""
        for agent_id in agent_ids:
            if agent_id in self.trust_scores:
                current_score = self.get_trust_score(agent_id, context)
                self.trust_scores[agent_id][context] = current_score * factor

    def get_all_scores(self):
        return self.trust_scores