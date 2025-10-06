
---

## 1. 风险测度速查表

| 名称 | 定义 | 公式 | 量子加速点 |
| ---- | ---- | ---- | ---------- |
| **VaR<sub>α</sub>** | α-分位损失 | inf{z : P(L≤z)≥1-α} | 用QAE估分位更快 |
| **CVaR<sub>α</sub>** | 尾部平均损失 | E[L \| L≥VaR<sub>α</sub>] | 用QAE估期望，误差∝1/N |
| **经典蒙特卡洛** | 样本均值 | L̂ = 1/J Σ L<sub>j</sub> | 误差∝1/√J |
| **QAE** | 量子振幅估计 | α̂ = QPE(Grover<sup>⊗k</sup>) | 误差∝1/N<sub>shots</sub> |

---

## 2. CVaR最小化LP（Rockafellar & Uryasev）

**变量**  
w ∈ ℝ<sup>n</sup> : 资产权重  θ ∈ ℝ : VaR代理变量  z ∈ ℝ<sup>J</sup> : 辅助损失缺口

**目标**  
min θ + 1/((1-α)J) Σ z<sub>j</sub>

**约束**  
z<sub>j</sub> ≥ −w<sup>T</sup>r<sub>j</sub> − θ  z<sub>j</sub> ≥ 0  Σ w<sub>i</sub> = 1  w ≥ 0

> 一次线性规划同时给出 **最优权重 w*** 与 **VaR(θ*)**。

---

## 3. 量子QAE线路伪代码（Qiskit风格）

```python
from qiskit_finance.circuit import EuropeanCallExpectedValue
from qiskit.algorithms import AmplitudeEstimation

# 1. 把“损失>θ”事件编码成量子线路
objective = EuropeanCallExpectedValue(
    num_state_qubits=log2(J),
    strike_price=θ,
    spot_price=spot,
    volatility=σ,
    interest_rate=r
)

# 2. 选择QAE版本（IQAE最省资源）
ae = IterativeAmplitudeEstimation(
    epsilon_target=0.01,  # 1%误差
    alpha=0.05,           # 95%置信
    quantum_instance=qcs_backend
)

result = ae.estimate(objective)
expectation = result.estimation        # E[(L-θ)^+]
```

> ** shots 数≈1k** 即可达到 **经典100k路径**方差水平。

---

## 4. 4-资产验证流程（免费额度可跑）

1. **挑资产**：SPY、QQQ、TLT、GLD  
2. **经典基准**：用10年历史日收益→100万次路径→LP解得w₀、CVaR₀  
3. **量子侧**：  
   - 用相同协方差矩阵生成 **1k条量子场景**（QAE估期望）  
   - 解同一LP得w₁、CVaR₁  
4. **判定**：  
   - |w₁−w₀|<1e-3 ✅  
   - Var(CVaR₁) / Var(CVaR₀) < 0.25 ✅  
5. **扩规模**：36-Q可推至12资产；100-Q Lyra再推20+资产

---

## 5. 性能红线（当前Rigetti硬件）

| 芯片 | 可用Q | 门深度 | 总保真度 | 建议资产数 |
| ---- | ----- | ------ | -------- | ---------- |
| Ankaa-2 | 8-Q | ≤60 | ≥75% | 4-5 |
| Ankaa-3 | 36-Q | ≤80 | ≥70% | 8-12 |
| Lyra(2025) | 100-Q | ≤120 | ≥65% | 20+ |

> **线路深度≈2×资产数×QAOA层数**；先跑p=1，保真度>70%再上p=2。

---

## 6. 免费资源与下一步

- **RGTI QCS Free Tier**：1万 shots/月 + 无限QVM  
- **学术加码**：.edu邮箱再领5万 shots（6个月）  
- **本地调试**：`qvm -S` 永远免费，先验证深度  
- **下一步**：  
  1. 把 **CVaR-LP** 封装成函数 → 支持 **QAE期望输入**  
  2. 跑 **12资产×p=1** → 记录 **方差降低倍数K**  
  3. 等 **100-Q Lyra** → 扩 **20资产×p=2** → 对比 **经典1000万路径**

---

复制完直接存成 `QuantumRisk.md`，随时打开就能接着填代码、补数据。祝早日跑出第一条 **量子优势风险曲线**！