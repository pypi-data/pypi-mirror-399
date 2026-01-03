Grid = list[list[int | None]]

SIZE = 9
BOX = 3
DIGITS = set(range(1, 10))


def row(grid, r):
    return grid[r]


def col(grid, c):
    return [grid[r][c] for r in range(9)]


def box(grid, r, c):
    br = (r // 3) * 3
    bc = (c // 3) * 3
    return [
        grid[rr][cc]
        for rr in range(br, br + 3)
        for cc in range(bc, bc + 3)
    ]


def empties(grid):
    return [(r, c) for r in range(9) for c in range(9) if grid[r][c] is None]


def candidates(grid, r, c):
    if grid[r][c] is not None:
        return set()

    used = set(row(grid, r)) | set(col(grid, c)) | set(box(grid, r, c))
    return DIGITS - used


def copy(grid):
    return [row[:] for row in grid]
