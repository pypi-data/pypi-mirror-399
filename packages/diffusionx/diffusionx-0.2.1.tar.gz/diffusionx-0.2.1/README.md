# DiffusionX

English | [简体中文](README-zh.md)

![PyPI](https://img.shields.io/pypi/v/diffusionx)
![PyPI - License](https://img.shields.io/pypi/l/diffusionx)

> [!NOTE]
> Development is in progress. 
>
> The Python binding of the same-named Rust crate [diffusionx](https://crates.io/crates/diffusionx), a multi-threaded Rust crate for random number generation and stochastic process simulation, via [PyO3](https://github.com/PyO3/pyo3). 

## Usage

### Random Number Generation

High-performance parallel random number generation using `diffusionx.random`.

```python
from diffusionx import random

# Generate standard normal random numbers (10 samples)
x = random.randn(10)

# Generate uniform random numbers (3x3 matrix) in [0, 1)
u = random.uniform((3, 3), low=0.0, high=1.0)

# Generate alpha-stable random numbers (alpha=1.5, beta=0.5)
s = random.stable_rand(alpha=1.5, beta=0.5, size=1000)
```

### Stochastic Process Simulation

Simulate various stochastic processes and calculate functionals using `diffusionx.simulation`.

```python
from diffusionx.simulation import Bm, FBm, Levy

# --- Brownian Motion ---
bm = Bm(start_position=0.0, diffusion_coefficient=1.0)
# Simulate trajectory
times, positions = bm.simulate(duration=10.0, time_step=0.01)
# Calculate First Passage Time (FPT) for domain (-1, 1)
fpt = bm.fpt(domain=(-1, 1))

# --- Fractional Brownian Motion ---
fbm = FBm(hurst_exponent=0.7)
# Calculate Time-Averaged Mean Squared Displacement (TAMSD)
tamsd = fbm.tamsd(duration=10.0, delta=1.0)

# --- Alpha-Stable Lévy Process ---
levy = Levy(alpha=1.5)
# Calculate Occupation Time in domain (-1, 1)
occ_time = levy.occupation_time(domain=(-1, 1), duration=10.0)
```

## Features

### Random Number Generation (`diffusionx.random`)

- **Gaussian**: `randn`
- **Uniform**: `uniform`
- **Exponential**: `randexp`
- **Poisson**: `poisson`
- **$\alpha$-Stable**: `stable_rand`, `skew_stable_rand`
- **Bernoulli**: `bool_rand`

### Stochastic Processes (`diffusionx.simulation`)

**Diffusions & Lévy Processes**
- Brownian Motion (`Bm`)
- Geometric Brownian Motion (`GeometricBm`)
- Fractional Brownian Motion (`FBm`)
- Lévy Process (`Levy`, `AsymmetricLevy`)
- Cauchy Process (`Cauchy`, `AsymmetricCauchy`)
- Gamma Process (`Gamma`)
- Ornstein-Uhlenbeck Process (`OU`)

**Subordinators**
- Stable Subordinator (`Subordinator`)
- Inverse Stable Subordinator (`InvSubordinator`)

**Langevin Dynamics**
- Langevin Equation (`Langevin`)
- Generalized Langevin Equation (`GeneralizedLangevin`)
- Subordinated Langevin Equation (`SubordinatedLangevin`)

**Brownian Functionals**
- Brownian Bridge (`BrownianBridge`)
- Brownian Excursion (`BrownianExcursion`)
- Brownian Meander (`BrownianMeander`)

**Others**
- Continuous Time Random Walk (`CTRW`)
- Poisson Process (`Poisson`)
- Lévy Walk (`LevyWalk`)

### Functionals

Support for calculating various functionals across most processes:
- **FPT**: First Passage Time (and moments)
- **Occupation Time**: Time spent in a domain (and moments)
- **MSD/TAMSD**: Mean Squared Displacement metrics

## Benchmark

Performance benchmark tests compare the Rust, C++, Julia, and Python implementations, which can be found [here](https://github.com/tangxiangong/diffusionx-benches).

## License

This project is dual-licensed under:

* [MIT License](https://opensource.org/licenses/MIT)
* [Apache License Version 2.0](https://www.apache.org/licenses/LICENSE-2.0)

You can choose to use either license. 

### Contribution

Unless you explicitly state otherwise, any contribution intentionally submitted
for inclusion in the work by you, as defined in the Apache-2.0 license, shall be dual licensed as above, without any
additional terms or conditions.
