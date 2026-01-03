from __future__ import annotations

import juliacall

jl = juliacall.newmodule("PyQuantumClifford")
jl.seval("using QuantumClifford")
jl.seval("using QuantumClifford.ECC")

QuantumClifford = jl.QuantumClifford
ECC = jl.QuantumClifford.ECC

__all__ = ["jl", "QuantumClifford", "ECC"]
