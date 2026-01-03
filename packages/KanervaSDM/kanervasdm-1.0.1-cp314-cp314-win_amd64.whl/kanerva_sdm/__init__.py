"""
Kanerva Sparse Distributed Memory (SDM)

A high-performance C++ implementation of Sparse Distributed Memory (SDM)
with Python bindings, based on Pentti Kanerva's 1992 technical report.

Example
-------
>>> import kanerva_sdm
>>> sdm = kanerva_sdm.KanervaSDM(
...     address_dimension=100,
...     memory_dimension=100,
...     num_locations=1000,
...     activation_threshold=37
... )
>>> address = [0, 1] * 50
>>> memory = [1, 0] * 50
>>> sdm.write(address, memory)
>>> recalled = sdm.read(address)

Reference
---------
Pentti Kanerva (1992) "Sparse Distributed Memory and Related Models".

(c) 2026 Simon Wong.
"""

from ._kanerva_sdm import KanervaSDM, __version__

__all__ = ["KanervaSDM", "__version__"]