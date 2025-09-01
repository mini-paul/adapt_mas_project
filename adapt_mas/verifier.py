# /adapt_mas_project/adapt_mas/verifier.py

from typing import Dict, List, Tuple
from .trust_manager import TrustManager


class DecentralizedVerifier:
    """实现去中心化同伴验证机制，计算CIS"""

    def calculate_cis(
            self,
            contribution_id: int,
            reviews: List[Tuple[int, int, float]],
            trust_manager: TrustManager,
            context: str
    ) -> float:
        """
        计算一个贡献的影响力分数 (CIS)
        contribution_id: The ID of the agent who made the contribution.
        reviews: A list of (reviewer_id, reviewee_id, score) tuples for this round.
        trust_manager: The trust manager instance.
        context: The current task context.
        """

        weighted_score_sum = 0.0
        trust_sum = 0.0

        # 筛选出对当前贡献的评价
        relevant_reviews = [r for r in reviews if r[1] == contribution_id]

        if not relevant_reviews:
            return 0.0  # 没有收到任何评价

        for reviewer_id, _, score in relevant_reviews:
            reviewer_trust = trust_manager.get_trust_score(reviewer_id, context)

            # 给予信任分数一个下限，避免负信任分的过度影响
            reviewer_trust = max(0.01, reviewer_trust)

            weighted_score_sum += reviewer_trust * score
            trust_sum += reviewer_trust

        if trust_sum == 0:
            return 0.0

        cis = weighted_score_sum / trust_sum
        return cis