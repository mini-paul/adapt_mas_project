# /adapt_mas_project/config.py

# --- API & Model Configuration ---
# 请在这里填入您的DeepSeek API密钥
DEEPSEEK_API_KEY = "YOUR_DEEPSEEK_API_KEY"

# 为不同角色选择模型
# 建议：裁判模型使用能力最强的，智能体模型可以稍弱以节约成本
AGENT_MODEL = "deepseek-chat"
JUDGE_MODEL = "deepseek-chat" # 在真实场景中，建议使用更强的模型作为裁判

# --- Experiment Setup ---
NUM_AGENTS = 10  # 智能体总数
NUM_ROUNDS = 50  # 实验总轮数

# --- Malicious Agent Configuration ---
# 'sleeper', 'colluding', 'camouflage', or a mix e.g., ['sleeper', 'colluding']
ATTACK_TYPE = 'colluding'
MALICIOUS_RATIO = 0.3 # 恶意智能体比例

# --- Sleeper Agent Parameters ---
SLEEPER_LATENT_PERIOD = 40 # 卧底潜伏期（在第几轮后开始攻击）

# --- Colluding Group Parameters ---
# 在实验开始时会自动根据MALICIOUS_RATIO创建合谋团体

# --- ADAPT-MAS Framework Parameters ---
# 动态信任模型学习率 (alpha)
TRUST_LEARNING_RATE = 0.3

# 社交图谱分析阈值
COMMUNITY_SUSPICION_THRESHOLD = 0.7 # 社群可疑度阈值
COLLECTIVE_PENALTY_FACTOR = 0.8   # 对合谋团体的集体惩罚因子



import os
from dotenv import load_dotenv

load_dotenv()

# --- API Keys ---
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"


OLLAMA_BASE_URL = "http://10.10.206.138:11434"
# OLLAMA_BASE_URL = "http://127.0.0.1:11434"
# --- Model Configurations ---



# --- CrS Framework Settings ---
INITIAL_CRS = 0.5
LEARNING_RATE = 0.1 # 学习率 eta
MAX_ITERATIONS = 3 # 智能体内部协作的最大轮次