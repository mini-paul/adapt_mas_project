# /experiments/run_experiment.py

import random
import pandas as pd
from typing import List

# 导入配置和模块
import config
from adapt_mas.agent import BaseAgent, HonestAgent, SleeperAgent, ColludingAgent, CamouflageAgent
from adapt_mas.trust_manager import TrustManager
from adapt_mas.langgraph_builder import build_graph, AdaptMasState


def setup_agents() -> List[BaseAgent]:
    """根据配置初始化智能体"""
    agents = []
    num_malicious = int(config.NUM_AGENTS * config.MALICIOUS_RATIO)
    agent_ids = list(range(config.NUM_AGENTS))
    malicious_ids = random.sample(agent_ids, num_malicious)

    colluding_group = malicious_ids if 'colluding' in config.ATTACK_TYPE else []

    for i in range(config.NUM_AGENTS):
        if i in malicious_ids:
            if config.ATTACK_TYPE == 'sleeper':
                agents.append(SleeperAgent(i, latent_period=config.SLEEPER_LATENT_PERIOD))
            elif config.ATTACK_TYPE == 'colluding':
                agents.append(ColludingAgent(i, colluding_group=colluding_group))
            elif config.ATTACK_TYPE == 'camouflage':
                agents.append(CamouflageAgent(i))
        else:
            agents.append(HonestAgent(i))
    print(f"Agents setup complete. Malicious IDs: {malicious_ids}")
    return agents


def run_simulation():
    """运行单次完整的模拟实验"""
    # 1. 初始化
    agents = setup_agents()
    trust_manager = TrustManager(
        agent_ids=[agent.id for agent in agents],
        learning_rate=config.TRUST_LEARNING_RATE
    )
    adapt_mas_app = build_graph()

    log_data = []

    # 2. 运行 N 轮
    for round_num in range(1, config.NUM_ROUNDS + 1):
        # (简化) 每轮都用同一个任务
        task = "investment"  # 'code' or 'investment'

        initial_state: AdaptMasState = {
            "round_number": round_num,
            "task_prompt": f"This is round {round_num}. Please perform the task.",
            "agents": agents,
            "trust_manager": trust_manager,
            "contributions": [],
            "reviews": [],
            "analysis_results": {},
            "final_output": ""
        }

        # 运行ADAPT-MAS工作流
        final_state = adapt_mas_app.invoke(initial_state)

        # 3. 记录日志
        trust_scores = final_state['trust_manager'].get_all_scores()
        for agent in agents:
            log_entry = {
                "round": round_num,
                "agent_id": agent.id,
                "is_malicious": agent.is_malicious,
                "malicious_type": agent.malicious_type,
                "trust_score": trust_scores[agent.id]["general_task"],
                "detected_colluding": agent.id in [item for sublist in
                                                   final_state['analysis_results']['colluding_groups'] for item in
                                                   sublist]
            }
            log_data.append(log_entry)

    # 4. 保存日志文件
    log_df = pd.DataFrame(log_data)
    log_filename = f"experiment_log_{config.ATTACK_TYPE}_{config.MALICIOUS_RATIO}.csv"
    log_df.to_csv(log_filename, index=False)
    print(f"\nSimulation finished. Log saved to {log_filename}")


if __name__ == "__main__":
    run_simulation()