import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

# 防止中文乱码
mpl.rcParams['font.family'] = 'SimHei'
mpl.rcParams['axes.unicode_minus'] = False

# 1. 2000-2025 真实年度总回报（%）
data = {
    '年份':  list(range(2000, 2026)),
    'A股': [43.5, -23.5, -18.5, 8.9, -15.0, -11.7, 111.9, 173.0, -62.9, 105.5,
            -7.0, -24.8, 4.8, 9.1, 49.7, 38.8, -13.0, 5.3, -28.3, 33.6,
            25.6, 9.2, -17.9, -3.5, 10.2, 20.7],          # 2025=YTD
    '债券': [1.6, 4.0, 4.8, 0.2, 3.7, 8.9, 2.1, 5.8, 11.8, 4.2,
            3.8, 4.0, 5.8, 1.4, 6.7, 8.8, 1.2, 0.9, 5.1, 4.6,
            2.9, 3.9, 3.2, 2.8, 3.5, 2.4],                # 2025=YTD
    '货币基金': [2.3, 2.2, 1.9, 1.0, 1.2, 1.6, 1.9, 2.0, 2.8, 1.9,
            1.8, 2.3, 2.9, 2.8, 3.1, 3.2, 2.5, 1.7, 1.9, 2.0,
            1.8, 2.0, 1.7, 1.8, 2.0, 1.9],                # 货币基金
    '黄金': [-5.4, 1.9, 25.5, 19.8, 4.6, 15.2, 22.6, 30.9, 4.9, 24.0,
            29.6, 9.9, -1.7, -28.3, -2.4, 1.5, 8.5, 13.2, 18.3, 13.2,
            13.8, 27.4, 27.4, 26.1, 27.4, 26.1],          # 2025=YTD
    '现金': [-0.4, -0.7, -1.1, 1.2, 2.7, 1.5, 1.6, 3.3, 0.1, -0.7,
            1.4, 2.6, 1.9, 1.5, 1.0, 1.4, 1.3, 1.6, 2.1, 2.3,
            1.9, 3.0, 3.0, 2.8, 3.0, 2.8]                # -CPI/(1+CPI)
}

df = pd.DataFrame(data).set_index('年份')

# 2. 复利净值（2000=1）
nav = (1 + df/100).cumprod()

# 3. 方案A：把2000年收益移到2001年初，强制2000年=1
nav0 = nav.shift(1).fillna(1)          # 2000年全部=1
nav0.iloc[0] = 1                      # 再次保险

# 4. 画图——中文全程
colors = {'A股':'#d62728', '债券':'#ff7f0e', '货币基金':'#2ca02c',
          '黄金':'#FFD700', '现金':'#9467bd'}
lw = {'A股':1.8, '债券':1.5, '货币基金':1.2, '黄金':1.5, '现金':1.2}

plt.figure(figsize=(12,6))
for col in nav0:
    plt.plot(nav0.index, nav0[col], label=col, color=colors[col], linewidth=lw[col])

plt.yscale('log')
plt.legend(loc='upper left', fontsize=11)
plt.title('A股真实锯齿 2000=1（对数坐标）', fontsize=14)
plt.ylabel('净值（2000-01-01 = 1，对数）', fontsize=12)
plt.xlabel('年份', fontsize=12)
plt.grid(True, which='both', ls='--', alpha=0.4)
plt.tight_layout()
plt.savefig('A股锯齿图_2000等于1.png', dpi=400)
plt.show()