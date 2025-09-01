# /adapt_mas_project/adapt_mas/agent.py

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseAgent(ABC):
    """智能体基类"""

    def __init__(self, agent_id: int, role: str, is_malicious: bool = False, malicious_type: str = None):
        self.id = agent_id
        self.role = role
        self.is_malicious = is_malicious
        self.malicious_type = malicious_type
        # 特定于恶意智能体的参数
        self.params = {}

    @abstractmethod
    def act(self, task_prompt: str, current_round: int) -> str:
        """根据任务提示生成贡献"""
        pass

    @abstractmethod
    def review(self, contribution: Dict[str, Any], all_agents: List['BaseAgent']) -> float:
        """对其他智能体的贡献进行评分"""
        pass


class HonestAgent(BaseAgent):
    """忠诚智能体"""

    def __init__(self, agent_id: int, role: str = "Analyst"):
        super().__init__(agent_id, role)

    def act(self, task_prompt: str, current_round: int) -> str:
        # 忠诚智能体总是尽力完成任务
        # (在实际运行中，这里会调用LLM)
        return f"Honest contribution for round {current_round} based on prompt: {task_prompt}"

    def review(self, contribution: Dict[str, Any], all_agents: List['BaseAgent']) -> float:
        # 忠诚智能体进行公正的评价 (简化为返回一个中性高分)
        return 0.8


class SleeperAgent(BaseAgent):
    """卧底智能体"""

    def __init__(self, agent_id: int, role: str = "Analyst", latent_period: int = 20):
        super().__init__(agent_id, role, is_malicious=True, malicious_type='sleeper')
        self.params['latent_period'] = latent_period

    def act(self, task_prompt: str, current_round: int) -> str:
        if current_round <= self.params['latent_period']:
            # 潜伏期：表现得像一个忠诚智能体
            return f"High-quality contribution during latent period (round {current_round})."
        else:
            # 攻击期：提供致命的错误信息
            return "Catastrophic and misleading information after latent period."

    def review(self, contribution: Dict[str, Any], all_agents: List['BaseAgent']) -> float:
        # 评价时也遵循潜伏策略
        current_round = contribution.get('round', 999)  # 假设贡献中包含轮次信息
        if current_round <= self.params['latent_period']:
            return 0.8
        else:
            # 攻击时可能会给出随机或恶意的评价
            return -0.5


class ColludingAgent(BaseAgent):
    """合谋智能体"""

    def __init__(self, agent_id: int, role: str = "Analyst", colluding_group: List[int] = None):
        super().__init__(agent_id, role, is_malicious=True, malicious_type='colluding')
        self.params['colluding_group'] = colluding_group if colluding_group else []

    def act(self, task_prompt: str, current_round: int) -> str:
        # 合谋智能体可能会产出中等质量的贡献
        return f"Colluding contribution for round {current_round}."

    def review(self, contribution: Dict[str, Any], all_agents: List['BaseAgent']) -> float:
        reviewee_id = contribution['agent_id']
        if reviewee_id in self.params['colluding_group']:
            # 对团伙成员无脑好评
            return 1.0
        else:
            # 打压团伙外成员
            return -1.0


class CamouflageAgent(BaseAgent):
    """伪装智能体"""

    def __init__(self, agent_id: int, role: str = "Analyst"):
        super().__init__(agent_id, role, is_malicious=True, malicious_type='camouflage')

    def act(self, task_prompt: str, current_round: int) -> str:
        # 生成看似详尽但包含核心错误的分析
        return "This is a long, well-written analysis full of professional jargon, but it is based on a fundamentally flawed premise that will lead to a wrong conclusion."

    def review(self, contribution: Dict[str, Any], all_agents: List['BaseAgent']) -> float:
        # 伪装智能体的评价可能更具欺骗性
        return 0.6  # 给出看似合理但可能不准确的评分