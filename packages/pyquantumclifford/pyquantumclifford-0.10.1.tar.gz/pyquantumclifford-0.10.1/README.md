# pyquantumclifford

Thin Python wrapper for [`QuantumClifford.jl`](https://qc.quantumsavory.org/stable/) and [`QuantumClifford.ECC`](https://qc.quantumsavory.org/stable/ECC_API/) using the JuliaPy stack.
Supports extremely fast Stabilizer state simulations, weakly non-Clifford dynamics, and generation of many modern quantum error correcting codes.

## Instalation

```
pip install pyquantumclifford
```

or

```
uv add pyquantumclifford
```

On first `import` the Julia runtime will be downloaded and QuantumClifford.jl will be compiled (optimized for your hardware). This is a slow process, might take around 5 minutes.

Optional: Having [`juliaup`](https://github.com/JuliaLang/juliaup) installed in your system (and available in your PATH) makes managing Julia versions much simpler behind the scenes. Consider manually installing `juliaup` before installing `pyquantumclifford`. The install command is `curl -fsSL https://install.julialang.org | sh` for a selfcontained install in `~/.julia` that you can delete at any time.

## Usage

```python
import numpy as np
from pyquantumclifford import QuantumClifford, ECC

# Optional, for calling arbitrary Julia code
from juliacall import Main as jl

# Simple ECC code
code = ECC.Shor9()

# Access parity checks and matrices
ECC.parity_checks(ECC.Shor9())
ECC.parity_matrix(ECC.Shor9())
np.array(ECC.parity_matrix(ECC.Shor9()))
```

## Notes

- Windows is not supported due to the Oscar computer algebra system being unavailable on it. Use WSL on Windows.
- `juliacall` provides access to Julia modules from Python.
