import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import random

import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
matplotlib.rcParams['axes.unicode_minus'] = False

# ============ 1. 生成模拟数据（10000条订单） ============
print("生成模拟数据...")
np.random.seed(42)
random.seed(42)

# 用户ID列表（1000个独立用户）
user_ids = list(range(1, 1001))

# 生成订单数据
data = []
start_date = datetime(2025, 1, 1)
end_date = datetime(2026, 9, 8)

for i in range(10000):
    user_id = random.choice(user_ids)
    days_offset = random.randint(0, (end_date - start_date).days)
    order_date = start_date + timedelta(days=days_offset)
    amount = round(random.uniform(50, 2000), 2)
    data.append([i+1, user_id, order_date.strftime('%Y-%m-%d'), amount])

df = pd.DataFrame(data, columns=['order_id', 'user_id', 'order_date', 'amount'])
print(f"✅ 生成 {len(df)} 条订单数据，涉及 {df['user_id'].nunique()} 个独立用户")

# ============ 2. 数据清洗 ============
print("数据清洗...")
df['order_date'] = pd.to_datetime(df['order_date'])
df = df[(df['amount'] > 0) & (df['amount'] < 5000)]
# 去重（同一订单号只保留一条）
df = df.drop_duplicates(subset=['order_id'])
print(f"✅ 清洗后剩余 {len(df)} 条订单")

# ============ 3. 计算RFM指标 ============
print("计算RFM指标...")
snapshot_date = df['order_date'].max() + timedelta(days=1)
# 按用户分组计算
rfm = df.groupby('user_id').agg({
    'order_date': lambda x: (snapshot_date - x.max()).days,  # R：最近消费时间
    'order_id': 'count',                                     # F：消费频率
    'amount': 'sum'                                          # M：消费金额
}).rename(columns={
    'order_date': 'R',
    'order_id': 'F',
    'amount': 'M'
})
print(f"✅ 计算完成，共 {len(rfm)} 个用户")

# ============ 4. RFM打分 ============
print("RFM打分...")
rfm['R_score'] = pd.qcut(rfm['R'], q=5, labels=[5, 4, 3, 2, 1]).astype(int)
rfm['F_score'] = pd.qcut(rfm['F'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5]).astype(int)
rfm['M_score'] = pd.qcut(rfm['M'], q=5, labels=[1, 2, 3, 4, 5]).astype(int)
rfm['RFM_total'] = rfm['R_score'] + rfm['F_score'] + rfm['M_score']

# ============ 5. 用户分层 ============
print("用户分层...")
def rfm_segment(row):
    r = 1 if row['R_score'] >= 4 else 0
    f = 1 if row['F_score'] >= 4 else 0
    m = 1 if row['M_score'] >= 4 else 0

    segment_map = {
        (1, 1, 1): '重要价值用户',
        (1, 1, 0): '重要发展用户',
        (1, 0, 1): '重要深耕用户',
        (0, 1, 1): '重要挽留用户',
        (1, 0, 0): '一般价值用户',
        (0, 1, 0): '一般发展用户',
        (0, 0, 1): '一般深耕用户',
        (0, 0, 0): '流失用户'
    }

    return segment_map[(r, f, m)]

rfm['用户分层'] = rfm.apply(rfm_segment, axis=1)

# ============ 6. 输出统计结果,增加分隔线============
print("\n" + "="*50)
print("📊 RFM分析结果...")
print("="*50)

# 分层统计
segment_stats = rfm['用户分层'].value_counts().reset_index()
segment_stats.columns = ['用户分层', '人数']
segment_stats['占比'] = (segment_stats['人数'] / len(rfm) * 100).round(2)
print("\n用户分层统计：")
print(segment_stats.to_string(index=False))

# 高价值用户GMV占比
high_value = rfm[rfm['用户分层'].isin(['重要价值用户', '重要发展用户'])]
high_value_gmv_ratio = (high_value['M'].sum() / rfm['M'].sum() * 100).round(2)
print(f"\n💎 高价值用户（重要价值+重要发展）贡献GMV占比：{high_value_gmv_ratio}%")

# 整体指标
print(f"\n📈 整体指标：")
print(f"   - 总用户数：{len(rfm)}")
print(f"   - 总订单数：{len(df)}")
print(f"   - 总GMV：{rfm['M'].sum():,.2f}")
print(f"   - 客单价：{df['amount'].mean():.2f}")

# ============ 7. 可视化 ============
print("\n生成可视化图表...")
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('电商用户RFM分析看板', fontsize=20, fontweight='bold')

# 图1：用户分层饼图
ax1 = axes[0, 0]
colors = ['#2ecc71', '#3498db', '#f1c40f', '#e67e22', '#e74c3c', '#95a5a6', '#9b59b6', '#1abc9c']
segment_counts = rfm['用户分层'].value_counts()
ax1.pie(segment_counts.values, labels=segment_counts.index, autopct='%1.1f%%', colors=colors[:len(segment_counts)])
ax1.set_title('用户分层占比', fontsize=14)

# 图2：RFM分数分布箱线图
ax2 = axes[0, 1]
rfm[['R_score', 'F_score', 'M_score']].boxplot(ax=ax2)
ax2.set_title('RFM各维度分数分布', fontsize=14)
ax2.set_ylabel('分数')
ax2.set_xlabel('维度')

# 图3：各分层用户GMV贡献
ax3 = axes[1, 0]
gmv_by_segment = rfm.groupby('用户分层')['M'].sum().sort_values(ascending=True)
gmv_by_segment.plot(kind='barh', ax=ax3, color='#3498db')
ax3.set_title('各分层用户GMV贡献', fontsize=14)
ax3.set_xlabel('GMV总额')
for i, v in enumerate(gmv_by_segment.values):
    ax3.text(v * 0.5, i, f'{v/10000:.1f}万', va='center', fontsize=10)

# 图4：RFM散点图（R vs F，颜色代表M）
ax4 = axes[1, 1]
scatter = ax4.scatter(rfm['R'], rfm['F'], c=rfm['M'], cmap='viridis', alpha=0.6, s=30)
ax4.set_title('RFM散点图（R-F-M）', fontsize=14)
ax4.set_xlabel('R（最近购买天数）')
ax4.set_ylabel('F（购买次数）')
plt.colorbar(scatter, ax=ax4, label='M（消费金额）')

plt.tight_layout()
plt.savefig('rfm_dashboard.png', dpi=300, bbox_inches='tight')
print("✅ 图表已保存为 rfm_dashboard.png")

# ============ 8. 输出Excel报告 ============
print("\n生成Excel报告...")
with pd.ExcelWriter('rfm_analysis_report.xlsx', engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='订单明细', index=False)
    rfm.to_excel(writer, sheet_name='RFM打分')
    segment_stats.to_excel(writer, sheet_name='分层统计', index=False)

print("✅ Excel报告已保存为 rfm_analysis_report.xlsx")

from sqlalchemy import create_engine
engine = create_engine('mysql+pymysql://root:redlight39@localhost:3306/sales_data')
rfm.to_sql('rfm_user_segment', engine, if_exists='replace', index=True)
print("✅ RFM结果已写入MySQL")
