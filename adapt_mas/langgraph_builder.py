# /adapt_mas_project/adapt_mas/langgraph_builder.py

from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Tuple, Any


class AdaptMasState(TypedDict):
    """定义工作流的状态"""
    round_number: int
    task_prompt: str
    agents: List[Any]  # 智能体实例列表
    contributions: List[Dict]  # 智能体的贡献: [{'agent_id': id, 'content': '...'}, ...]
    reviews: List[Tuple[int, int, float]]  # 同伴评审: [(reviewer, reviewee, score), ...]
    trust_manager: Any  # TrustManager 实例
    analysis_results: Dict  # 存储分析结果，如合谋团伙
    final_output: str  # 最终的聚合决策


# --- 定义工作流节点 ---

def contribution_node(state: AdaptMasState):
    """1. 智能体贡献节点"""
    contributions = []
    task_prompt = state["task_prompt"]
    current_round = state["round_number"]
    for agent in state["agents"]:
        # 在真实应用中，这里会调用LLM
        content = agent.act(task_prompt, current_round)
        contributions.append({'agent_id': agent.id, 'content': content, 'round': current_round})

    print(f"--- Round {current_round}: Contribution Node Finished ---")
    return {"contributions": contributions}


def peer_review_node(state: AdaptMasState):
    """2. 同伴评审节点"""
    reviews = []
    contributions = state["contributions"]
    agents = state["agents"]
    for reviewer in agents:
        for contribution in contributions:
            # 智能体不评价自己
            if reviewer.id != contribution['agent_id']:
                score = reviewer.review(contribution, agents)
                reviews.append((reviewer.id, contribution['agent_id'], score))

    print("--- Peer Review Node Finished ---")
    return {"reviews": reviews}


def analysis_node(state: AdaptMasState):
    """3. ADAPT-MAS核心分析节点"""
    from .graph_analyzer import GraphAnalyzer
    from .verifier import DecentralizedVerifier

    reviews = state["reviews"]
    trust_manager = state["trust_manager"]
    contributions = state["contributions"]

    # 初始化分析工具
    graph_analyzer = GraphAnalyzer()
    verifier = DecentralizedVerifier()

    # a) 社交图谱分析
    graph = graph_analyzer.build_graph(reviews)
    colluding_groups = graph_analyzer.detect_collusion(graph)

    # b) 对检测到的合谋团伙进行惩罚
    if colluding_groups:
        from config import COLLECTIVE_PENALTY_FACTOR
        print(f"Detected Colluding Groups: {colluding_groups}")
        for group in colluding_groups:
            trust_manager.penalize_group(group, "general_task", COLLECTIVE_PENALTY_FACTOR)

    # c) 去中心化验证并更新信任
    for contribution in contributions:
        agent_id = contribution['agent_id']
        # 计算CIS作为新证据
        cis = verifier.calculate_cis(agent_id, reviews, trust_manager, "general_task")
        # 更新信任分数
        trust_manager.update_trust(agent_id, "general_task", cis)

    print("--- Analysis Node Finished ---")
    return {
        "trust_manager": trust_manager,
        "analysis_results": {"colluding_groups": colluding_groups}
    }


def aggregation_node(state: AdaptMasState):
    """4. 加权聚合决策节点"""
    trust_manager = state["trust_manager"]
    contributions = state["contributions"]

    weighted_contributions = []
    for contrib in contributions:
        agent_id = contrib['agent_id']
        trust_score = trust_manager.get_trust_score(agent_id, "general_task")
        # 只考虑信任度 > 0 的贡献
        if trust_score > 0:
            weighted_contributions.append((contrib['content'], trust_score))

    # 按信任度排序，取最高分的贡献作为最终输出 (简化聚合逻辑)
    if not weighted_contributions:
        final_output = "No consensus reached due to low trust."
    else:
        # 在真实应用中，这里会用加权内容生成最终报告
        sorted_contributions = sorted(weighted_contributions, key=lambda x: x[1], reverse=True)
        final_output = sorted_contributions[0][0]

    print("--- Aggregation Node Finished ---")
    print(f"Final Decision: {final_output}\n")
    return {"final_output": final_output}


def build_graph():
    """构建LangGraph工作流"""
    workflow = StateGraph(AdaptMasState)

    workflow.add_node("contribution", contribution_node)
    workflow.add_node("peer_review", peer_review_node)
    workflow.add_node("analysis", analysis_node)
    workflow.add_node("aggregation", aggregation_node)

    workflow.set_entry_point("contribution")
    workflow.add_edge("contribution", "peer_review")
    workflow.add_edge("peer_review", "analysis")
    workflow.add_edge("analysis", "aggregation")
    workflow.add_edge("aggregation", END)

    return workflow.compile()