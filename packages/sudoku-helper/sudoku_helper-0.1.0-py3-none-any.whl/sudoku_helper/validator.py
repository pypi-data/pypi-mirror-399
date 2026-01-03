from ._grid import row, col, box, empties, candidates, copy


def is_valid(grid):
    """Check if the Sudoku grid is valid (no duplicates)"""
    def no_duplicates(values):
        nums = [v for v in values if v is not None]
        return len(nums) == len(set(nums))

    for i in range(9):
        if not no_duplicates(row(grid, i)):
            return False
        if not no_duplicates(col(grid, i)):
            return False

    for r in range(0, 9, 3):
        for c in range(0, 9, 3):
            if not no_duplicates(box(grid, r, c)):
                return False

    return True


def has_one_solution(grid):
    """Check if the Sudoku grid has exactly one solution"""
    count = 0

    def backtrack(g):
        nonlocal count

        if count > 1:
            return

        empty = empties(g)
        if not empty:
            count += 1
            return

        # pick first empty cell
        r, c = empty[0]

        for v in candidates(g, r, c):
            g[r][c] = v
            if is_valid(g):
                backtrack(g)
            g[r][c] = None

    backtrack(copy(grid))
    return count == 1
