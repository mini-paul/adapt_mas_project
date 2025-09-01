# /adapt_mas_project/README.md

# ADAPT-MAS 框架实现

本项目是研究论文《基于动态信任与社交图谱分析之自适应多智能体安全防御框架研究》的核心代码实现。

## 项目结构

- **/adapt_mas**: 框架核心逻辑。
- **/experiments**: 实验运行脚本。
- **/analysis**: 结果分析Jupyter Notebook。
- **/utils**: 通用工具，如API客户端。
- **config.py**: 所有实验参数的配置文件。

## 如何运行

1.  **安装依赖**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **配置API密钥**:
    打开 `config.py` 文件，将 `DEEPSEEK_API_KEY` 的值修改为您自己的DeepSeek API密钥。

3.  **配置实验参数**:
    在 `config.py` 中，您可以调整智能体数量、恶意智能体比例、攻击类型、卧底潜伏期等参数。

4.  **运行实验**:
    ```bash
    python experiments/run_experiment.py
    ```
    实验结束后，将在项目根目录下生成一个 `.csv` 日志文件，例如 `experiment_log_colluding_0.3.csv`。

5.  **分析结果**:
    启动Jupyter Lab:
    ```bash
    jupyter lab
    ```
    然后打开 `analysis/plot_results.ipynb`，修改其中的日志文件名，运行代码单元格即可生成您论文第四章中描述的信任分数演化图等分析结果。
