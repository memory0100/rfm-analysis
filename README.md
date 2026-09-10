# 电商用户RFM分层与价值分析系统

## 📌 项目简介
基于Python模拟生成的10,000条电商订单数据，构建RFM用户价值分层模型，实现用户精细化分类与业务洞察。

## 🛠 技术栈
- **数据处理**：Python 3.x（Pandas / NumPy）
- **数据可视化**：Matplotlib / Seaborn
- **数据存储**：SQLAlchemy + MySQL
- **分析方法**：RFM模型

## 📊 项目成果
- 对1,000名用户进行RFM三维度评分，划分**8类用户群体**
- 重要价值用户仅占17%，但贡献**28% GMV**
- 输出**4合1可视化看板** + 完整Excel分析报告
- 分析结果写入MySQL，实现数据持久化

## 📂 文件说明
| 文件 | 说明 |
|------|------|
| `script.py` | 主程序（数据生成→清洗→RFM建模→可视化） |
| `rfm_dashboard.png` | 4合1可视化看板 |
| `rfm_analysis_report.xlsx` | Excel分析报告（3个sheet） |
| `requirements.txt` | 依赖包列表 |

## 🚀 快速开始
```bash
pip install -r requirements.txt
python script.py
