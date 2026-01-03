# DiffusionX

[English](README.md) | 简体中文

> [!NOTE]
> 开发正在进行中。DiffusionX 是多线程高性能 Rust 随机数/随机过程模拟库的 Python 绑定，通过 [PyO3](https://github.com/PyO3/pyo3) 实现。

## 使用示例

### 随机数生成

使用 `diffusionx.random` 进行高性能并行随机数生成。

```python
from diffusionx import random

# 生成标准正态分布随机数 (10 个样本)
x = random.randn(10)

# 生成均匀分布随机数 (3x3 矩阵)，范围 [0, 1)
u = random.uniform((3, 3), low=0.0, high=1.0)

# 生成 alpha 稳定分布随机数 (alpha=1.5, beta=0.5)
s = random.stable_rand(alpha=1.5, beta=0.5, size=1000)
```

### 随机过程模拟

使用 `diffusionx.simulation` 模拟各类随机过程并计算泛函。

```python
from diffusionx.simulation import Bm, FBm, Levy

# --- 布朗运动 (Brownian Motion) ---
bm = Bm(start_position=0.0, diffusion_coefficient=1.0)
# 模拟轨迹
times, positions = bm.simulate(duration=10.0, time_step=0.01)
# 计算首次通过时间 (FPT)，区间 (-1, 1)
fpt = bm.fpt(domain=(-1, 1))

# --- 分数布朗运动 (Fractional Brownian Motion) ---
fbm = FBm(hurst_exponent=0.7)
# 计算时间平均均方位移 (TAMSD)
tamsd = fbm.tamsd(duration=10.0, delta=1.0)

# --- Alpha 稳定 Lévy 过程 ---
levy = Levy(alpha=1.5)
# 计算区间 (-1, 1) 内的停留时间 (Occupation Time)
occ_time = levy.occupation_time(domain=(-1, 1), duration=10.0)
```

## 功能特性

### 随机数生成 (`diffusionx.random`)

- **高斯分布**: `randn`
- **均匀分布**: `uniform`
- **指数分布**: `randexp`
- **泊松分布**: `poisson`
- **$\alpha$-稳定分布**: `stable_rand`, `skew_stable_rand`
- **伯努利分布**: `bool_rand`

### 随机过程 (`diffusionx.simulation`)

**扩散与 Lévy 过程**
- 布朗运动 (`Bm`)
- 几何布朗运动 (`GeometricBm`)
- 分数布朗运动 (`FBm`)
- Lévy 过程 (`Levy`, `AsymmetricLevy`)
- 柯西过程 (`Cauchy`, `AsymmetricCauchy`)
- Gamma 过程 (`Gamma`)
- Ornstein-Uhlenbeck 过程 (`OU`)

**从属过程 (Subordinators)**
- 稳定从属过程 (`Subordinator`)
- 逆稳定从属过程 (`InvSubordinator`)

**Langevin 动力学**
- Langevin 方程 (`Langevin`)
- 广义 Langevin 方程 (`GeneralizedLangevin`)
- 从属 Langevin 方程 (`SubordinatedLangevin`)

**布朗泛函**
- 布朗桥 (`BrownianBridge`)
- 布朗主要项 (`BrownianExcursion`)
- 布朗蜿蜒 (`BrownianMeander`)

**其他**
- 连续时间随机游走 (`CTRW`)
- 泊松过程 (`Poisson`)
- Lévy 游走 (`LevyWalk`)

### 泛函计算

支持对大多数过程计算以下泛函：
- **FPT**: 首次通过时间 (First Passage Time) 及其矩
- **Occupation Time**: 停留时间及其矩
- **MSD/TAMSD**: 均方位移 / 时间平均均方位移

## Benchmark

性能基准测试对比了 Rust, C++, Julia 和 Python 的实现，详情请见 [此处](https://github.com/tangxiangong/diffusionx-benches)。

## 许可证

本项目采用双许可证模式：

* [MIT 许可证](https://opensource.org/licenses/MIT)
* [Apache 许可证 2.0 版本](https://www.apache.org/licenses/LICENSE-2.0)

您可以选择使用其中任一许可证。
