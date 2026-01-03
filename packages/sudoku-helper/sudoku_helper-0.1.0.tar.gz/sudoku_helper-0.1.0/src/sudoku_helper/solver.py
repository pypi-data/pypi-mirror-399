from ._grid import candidates
from ._types import Step
from .validator import is_valid


def next_step(grid):
    """
    Return the next logical step using supported techniques,
    or None if no logical step is available.
    """
    if not is_valid(grid):
        raise ValueError("Input grid is not a valid sudoku grid")

    techniques = [
        naked_or_hidden_single,
        naked_or_hidden_pair,
        pointing_pair,
        box_line_reduction,
    ]
    for technique in techniques:
        step = technique(grid)
        if step:
            return step
    return None


def naked_or_hidden_single(grid):
    # Rows
    for r in range(9):
        steps = _hidden_in_units([(r, c) for c in range(9)], grid, "row")
        if steps:
            return steps

    # Columns
    for c in range(9):
        steps = _hidden_in_units([(r, c) for r in range(9)], grid, "col")
        if steps:
            return steps

    # 3x3 Boxes
    for br in range(0, 9, 3):
        for bc in range(0, 9, 3):
            cells = [
                (r, c)
                for r in range(br, br + 3)
                for c in range(bc, bc + 3)
            ]
            steps = _hidden_in_units(cells, grid, "box")
            if steps:
                return steps

    return None


def _hidden_in_units(cells, grid, unit):
    locations = {d: [] for d in range(1, 10)}

    for r, c in cells:
        if grid[r][c] is None:
            for v in candidates(grid, r, c):
                locations[v].append((r, c))

    for v, spots in locations.items():
        if len(spots) == 1:
            r, c = spots[0]
            technique = (
                "Naked Single"
                if len(candidates(grid, r, c)) == 1
                else "Hidden Single"
            )
            return Step(
                cells=[(r, c)],
                value=v,
                technique=technique,
                explanation=(
                    f"{v} can only go in r{r + 1}c{c + 1} "
                    f"in this {unit}."
                ),
            )

    return None


def naked_or_hidden_pair(grid):
    """
    Find two digits that are candidates
    in exactly two cells in a row, column or box
    """
    # Check rows
    for r in range(9):
        counts = {d: [] for d in range(1, 10)}
        for c in range(9):
            if grid[r][c] is None:
                for v in candidates(grid, r, c):
                    counts[v].append(c)
        # Find pairs
        digits = [d for d, locs in counts.items() if len(locs) == 2]
        for i in range(len(digits)):
            locs1 = counts[digits[i]]
            for j in range(i + 1, len(digits)):
                locs2 = counts[digits[j]]
                if locs1 == locs2:
                    c1, c2 = locs1
                    cells = [(r, c1), (r, c2)]
                    technique = (
                        "Naked Pair"
                        if all(
                            len(candidates(grid, r, c)) == 2
                            for r, c in cells
                        )
                        else "Hidden Pair"
                    )
                    return Step(
                        cells=[(r, c1), (r, c2)],
                        value=None,
                        technique=technique,
                        explanation=(
                            f"{technique} {digits[i]},{digits[j]} in "
                            f"r{r + 1}c{c1 + 1} and r{r + 1}c{c2 + 1}.",
                        ),
                    )
    # Check columns
    for c in range(9):
        counts = {d: [] for d in range(1, 10)}
        for r in range(9):
            if grid[r][c] is None:
                for v in candidates(grid, r, c):
                    counts[v].append(r)
        digits = [d for d, locs in counts.items() if len(locs) == 2]
        for i in range(len(digits)):
            locs1 = counts[digits[i]]
            for j in range(i + 1, len(digits)):
                locs2 = counts[digits[j]]
                if locs1 == locs2:
                    r1, r2 = locs1
                    cells = [(r1, c), (r2, c)]
                    technique = (
                        "Naked Pair"
                        if all(
                            len(candidates(grid, r, c)) == 2
                            for r, c in cells
                        )
                        else "Hidden Pair"
                    )
                    return Step(
                        cells=cells,
                        value=None,
                        technique=technique,
                        explanation=(
                            f"{technique} {digits[i]},{digits[j]} in "
                            f"r{r1 + 1}c{c + 1} and r{r2 + 1}c{c + 1}.",
                        ),
                    )
    # Check boxes
    for br in range(0, 9, 3):
        for bc in range(0, 9, 3):
            counts = {d: [] for d in range(1, 10)}
            for r in range(br, br + 3):
                for c in range(bc, bc + 3):
                    if grid[r][c] is None:
                        for v in candidates(grid, r, c):
                            counts[v].append((r, c))
            digits = [d for d, locs in counts.items() if len(locs) == 2]
            for i in range(len(digits)):
                locs1 = counts[digits[i]]
                for j in range(i + 1, len(digits)):
                    locs2 = counts[digits[j]]
                    if locs1 == locs2:
                        (r1, c1), (r2, c2) = locs1
                        cells = [(r1, c1), (r2, c2)]
                        technique = (
                            "Naked Pair"
                            if all(
                                len(candidates(grid, r, c)) == 2
                                for r, c in cells
                            )
                            else "Hidden Pair"
                        )
                        return Step(
                            cells=[(r1, c1), (r2, c2)],
                            value=None,
                            technique=technique,
                            explanation=(
                                f"{technique} {digits[i]},{digits[j]} "
                                f"in r{r1 + 1}c{c1 + 1} and "
                                f"r{r2 + 1}c{c2 + 1}.",
                            ),
                        )
    return None


def pointing_pair(grid):
    """
    Find two digits that are candidates in exactly two cells
    in the same row or column within a box.
    """
    for br in range(0, 9, 3):
        for bc in range(0, 9, 3):
            for d in range(1, 10):
                positions = [
                    (r, c)
                    for r in range(br, br + 3)
                    for c in range(bc, bc + 3)
                    if grid[r][c] is None and d in candidates(grid, r, c)
                ]
                if positions:
                    rows = set(r for r, _ in positions)
                    cols = set(c for _, c in positions)
                    if len(rows) == 1:
                        row = list(rows)[0]
                        cols = [c for r, c in positions if r == row]
                        return Step(
                            cells=[(row, c) for c in cols],
                            value=None,
                            technique="Pointing pair",
                            explanation=(
                                f"{d} appears only in row {row + 1} in box "
                                f"({br // 3 + 1},{bc // 3 + 1}), "
                                f"so all other {d}'s can be removed "
                                f"from row {row + 1}."
                            ),
                        )
                    if len(cols) == 1:
                        col = list(cols)[0]
                        rows = [r for r, c in positions if c == col]
                        return Step(
                            cells=[(r, col) for r in rows],
                            value=None,
                            technique="Pointing pair",
                            explanation=(
                                f"{d} appears only in column {col + 1} in box "
                                f"({br // 3 + 1},{bc // 3 + 1}), "
                                f"so all other {d}'s can be removed from "
                                f"column {col + 1}."
                            ),
                        )
    return None


def box_line_reduction(grid):
    """
    For a given digit, if all its candidates in a row or column
    are confined to a single box,
    then that digit can be removed from other cells in that box.
    """
    for r in range(9):
        for d in range(1, 10):
            positions = [
                c
                for c in range(9)
                if grid[r][c] is None and d in candidates(grid, r, c)
            ]
            if not positions:
                continue
            boxes = set(c // 3 for c in positions)
            if len(boxes) == 1:
                box = list(boxes)[0]
                box_col_start = box * 3
                box_cols = [
                    c for c in positions
                    if box_col_start <= c < box_col_start + 3
                ]
                return Step(
                    cells=[(r, c) for c in box_cols],
                    value=None,
                    technique="Box-Line Reduction",
                    explanation=(
                        f"{d} in r{r + 1} appears only in box {box + 1}, "
                        f"so can be removed from all notes in that box.",
                    ),
                )

    for c in range(9):
        for d in range(1, 10):
            positions = [
                r
                for r in range(9)
                if grid[r][c] is None and d in candidates(grid, r, c)
            ]
            if not positions:
                continue
            boxes = set(r // 3 for r in positions)
            if len(boxes) == 1:
                box = list(boxes)[0]
                box_rows_start = box * 3
                box_rows = [
                    r for r in positions
                    if box_rows_start <= r < box_rows_start + 3
                ]
                return Step(
                    cells=[(r, c) for r in box_rows],
                    value=None,
                    technique="Box-Line Reduction",
                    explanation=(
                        f"{d} in c{c + 1} appears only in box {box + 1}, "
                        f"so can be removed from all notes in that box."
                    ),
                )
    return None
