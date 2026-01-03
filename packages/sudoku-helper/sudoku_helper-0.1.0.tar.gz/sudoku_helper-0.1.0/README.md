
# Sudoku Helper

A Python library for solving and validating Sudoku puzzles programmatically.


## Features

- Solve standard 9x9 Sudoku puzzles step-by-step
- Validate Sudoku grids
- Check for unique solutions
- Easy to use as a Python library


## Installation

### From PyPI (recommended)

```bash
pip install sudoku-helper
```

### Development install (from source)

```bash
git clone https://github.com/yourusername/sudoku-helper.git
cd sudoku-helper
pip install -r requirements.txt
```

## Usage

Import the library and use its functions in your Python code:

```python
from sudoku_helper.validator import is_valid, has_one_solution
from sudoku_helper.solver import next_step

# Example 9x9 Sudoku grid (None for empty cells)
grid = [
	[5, 3, None, None, 7, None, None, None, None],
	[6, None, None, 1, 9, 5, None, None, None],
	[None, 9, 8, None, None, None, None, 6, None],
	[8, None, None, None, 6, None, None, None, 3],
	[4, None, None, 8, None, 3, None, None, 1],
	[7, None, None, None, 2, None, None, None, 6],
	[None, 6, None, None, None, None, 2, 8, None],
	[None, None, None, 4, 1, 9, None, None, 5],
	[None, None, None, None, 8, None, None, 7, 9],
]

# Validate the grid
print(is_valid(grid))

# Check for unique solution
print(has_one_solution(grid))

# Get the next logical solving step
step = next_step(grid)
if step:
	print(f"Cells: {step.cells}")
	print(f"Technique: {step.technique}")
	print(f"Explanation: {step.explanation}")
else:
	print("No further logical steps found.")
```


## Contributing

Pull requests are welcome. Please ensure your code passes all tests and Snyk scans.
