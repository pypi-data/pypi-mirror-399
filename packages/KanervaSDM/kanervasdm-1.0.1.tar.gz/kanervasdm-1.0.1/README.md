# KanervaSDM

A high-performance C++ implementation of Sparse Distributed Memory (SDM) with Python bindings, based on Pentti Kanerva's 1992 technical report.

## Overview

Sparse Distributed Memory is a cognitive model that stores information in a distributed manner across many locations. This implementation provides:

- Fast C++ core with Python bindings via pybind11.
- Hamming distance-based activation for memory retrieval.
- Support for arbitrary address and memory dimensions.
- Reproducible results with seeded random initialization.

## Installation

### From Source

```bash
git clone https://github.com/made-by-simon/KanervaSDM.git
cd KanervaSDM
pip install .
```

### Development Installation

```bash
pip install -e ".[dev]"
```

### Requirements

- Python >= 3.7.
- C++11 compatible compiler.
- pybind11 >= 2.6.0.

## Quick Start

```python
import kanerva_sdm

# Initialize SDM with 100-dimensional addresses and memories
sdm = kanerva_sdm.KanervaSDM(
    address_dimension=100,
    memory_dimension=100,
    num_locations=1000,
    hamming_threshold=37,
    random_seed=42
)

# Write a memory to an address
address = [0, 1] * 50  # Binary address vector
memory = [1, 0] * 50   # Binary memory vector
sdm.write(address, memory)

# Read memory back
recalled = sdm.read(address)
print(f"Recalled memory: {recalled}")

# Check memory count
print(f"Stored memories: {sdm.memory_count}")
```

## API Reference

### KanervaSDM

Main class for Sparse Distributed Memory operations.

#### Initialization

```python
KanervaSDM(
    address_dimension: int,
    memory_dimension: int,
    num_locations: int,
    hamming_threshold: int,
    random_seed: int = 42
)
```

**Parameters:**
- `address_dimension`: Length of address vectors (N).
- `memory_dimension`: Length of memory vectors (U).
- `num_locations`: Number of hard locations (M).
- `hamming_threshold`: Hamming distance threshold for activation (H).
- `random_seed`: Seed for reproducible random generation.

**Raises:**
- `ValueError`: If any dimension or threshold is non-positive.

#### Methods

**write(address, memory)**

Store a memory at the given address.

```python
sdm.write([0, 1, 0, 1], [1, 1, 0, 0])
```

**Parameters:**
- `address`: Binary list of length `address_dimension`.
- `memory`: Binary list of length `memory_dimension`.

**Raises:**
- `ValueError`: If vectors have incorrect size or contain non-binary values.

---

**read(address)**

Retrieve memory from the given address.

```python
recalled = sdm.read([0, 1, 0, 1])
```

**Parameters:**
- `address`: Binary list of length `address_dimension`.

**Returns:**
- Binary list of length `memory_dimension`.
- Returns all zeros if no locations are activated.

**Raises:**
- `ValueError`: If address has incorrect size or contains non-binary values.

---

**erase_memory()**

Reset all memory counters to zero while preserving hard locations.

```python
sdm.erase_memory()
```

#### Properties

- `address_dimension`: Length of address vectors.
- `memory_dimension`: Length of memory vectors.
- `num_locations`: Number of hard locations.
- `hamming_threshold`: Activation threshold.
- `memory_count`: Number of stored memories.

## How It Works

### Core Concepts

1. **Hard Locations (A)**: Random binary vectors that serve as reference points in the address space.
2. **Memory Matrix (C)**: Counters that accumulate memory values at each location.
3. **Activation**: Locations within Hamming distance H of the query address are activated.
4. **Polar Encoding**: Binary values {0,1} are converted to {-1,+1} for storage.

### Write Operation

1. Find all hard locations within Hamming distance H of the target address.
2. Convert memory vector from binary to polar form.
3. Add polar values to the memory counters at activated locations.

### Read Operation

1. Find all hard locations within Hamming distance H of the target address.
2. Sum memory counters across activated locations.
3. Threshold summation to produce binary output (>= 0 → 1, < 0 → 0).

## Examples

### Basic Usage

```python
import kanerva_sdm

# Create SDM instance
sdm = kanerva_sdm.KanervaSDM(
    address_dimension=100,
    memory_dimension=100,
    num_locations=1000,
    hamming_threshold=37
)

# Store multiple memories
patterns = [
    ([0]*100, [1]*100),
    ([1]*100, [0]*100),
    ([0,1]*50, [1,0]*50)
]

for addr, mem in patterns:
    sdm.write(addr, mem)

print(f"Total memories stored: {sdm.memory_count}")

# Retrieve a memory
recalled = sdm.read([0]*100)
print(f"Recalled: {recalled[:10]}...")  # First 10 elements
```

### Testing Recall Accuracy

```python
import kanerva_sdm

sdm = kanerva_sdm.KanervaSDM(100, 100, 1000, 37, random_seed=42)

# Store a pattern
original_address = [0, 1] * 50
original_memory = [1, 0] * 50
sdm.write(original_address, original_memory)

# Test recall
recalled = sdm.read(original_address)
accuracy = sum(r == m for r, m in zip(recalled, original_memory)) / len(original_memory)
print(f"Recall accuracy: {accuracy * 100:.1f}%")
```

### Experimenting with Parameters

```python
import kanerva_sdm

# Test different thresholds
for threshold in [30, 35, 40, 45]:
    sdm = kanerva_sdm.KanervaSDM(100, 100, 1000, threshold)
    sdm.write([0]*100, [1]*100)
    recalled = sdm.read([0]*100)
    accuracy = sum(recalled) / len(recalled)
    print(f"Threshold {threshold}: {accuracy * 100:.1f}% ones recalled")
```

## Testing

Run the test suite using pytest:

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test
pytest tests/test_kanerva_sdm.py::TestKanervaSDM::test_write_and_read
```

## Performance Considerations

- C++ implementation provides significant speedup over pure Python.
- Memory operations are O(M × N) where M is `num_locations` and N is `address_dimension`.
- Larger Hamming thresholds activate more locations, increasing computation.
- Optimal threshold is typically around 40-45% of `address_dimension`.

## Project Structure

```
kanerva-sdm/
│
├── include/
│   └── kanerva_sdm/
│       └── kanerva_sdm.h          # C++ header
│
├── src/
│   └── kanerva_sdm/
│       ├── __init__.py            # Python package init
│       └── bindings.cpp           # pybind11 bindings
│
├── tests/
│   └── kanerva_sdm/
│       ├── __init__.py
│       └── test_kanerva_sdm.py    # Unit tests
│
├── .gitignore
├── LICENSE
├── MANIFEST.in
├── pyproject.toml
├── README.md
└── setup.py
```

## Reference

This implementation is based on:

> Pentti Kanerva (1992). "Sparse Distributed Memory and Related Models."

## License

MIT License. See [LICENSE](LICENSE) for details.

## Author

Simon Wong (smw2@ualberta.ca)

## Contributing

Contributions are welcome. Please:

1. Fork the repository.
2. Create a feature branch.
3. Add tests for new functionality.
4. Ensure all tests pass.
5. Submit a pull request.

## Issues

Report bugs and request features at [GitHub Issues](https://github.com/made-by-simon/KanervaSDM/issues).