
import time
import csv
from statistics import mean

RUNS = 20

TEST_CASES = [

    {
        "name": "S4-E",
        "difficulty": "Easy",
        "board": [
            [1, 0, 3, 4],
            [0, 4, 1, 0],
            [2, 1, 0, 3],
            [4, 0, 2, 1]
        ],
        "block_rows": 2,
        "block_cols": 2
    },

    {
        "name": "S4-M",
        "difficulty": "Medium",
        "board": [
            [0, 1, 0, 0],
            [4, 0, 0, 2],
            [1, 0, 0, 0],
            [0, 0, 4, 0]
        ],
        "block_rows": 2,
        "block_cols": 2
    },

    {
        "name": "S4-H",
        "difficulty": "Hard",
        "board": [
            [0, 0, 0, 4],
            [0, 1, 0, 0],
            [0, 0, 2, 0],
            [3, 0, 0, 0]
        ],
        "block_rows": 2,
        "block_cols": 2
    },

    {
        "name": "S6-E",
        "difficulty": "Easy",
        "board": [
            [0, 2, 3, 4, 0, 6],
            [4, 0, 6, 0, 2, 0],
            [2, 3, 0, 5, 6, 0],
            [0, 6, 4, 0, 3, 1],
            [0, 1, 0, 6, 0, 5],
            [6, 0, 5, 3, 1, 0]
        ],
        "block_rows": 2,
        "block_cols": 3
    },

    {
        "name": "S6-M",
        "difficulty": "Medium",
        "board": [
            [1, 0, 0, 0, 0, 6],
            [0, 0, 6, 0, 2, 0],
            [0, 3, 0, 5, 0, 0],
            [0, 0, 4, 0, 3, 0],
            [0, 1, 0, 6, 0, 0],
            [6, 0, 0, 0, 0, 2]
        ],
        "block_rows": 2,
        "block_cols": 3
    },

    {
        "name": "S6-H",
        "difficulty": "Hard",
        "board": [
            [0, 0, 0, 4, 0, 0],
            [0, 5, 0, 0, 0, 3],
            [2, 0, 0, 0, 6, 0],
            [0, 6, 0, 0, 0, 1],
            [3, 0, 0, 0, 4, 0],
            [0, 0, 5, 0, 0, 0]
        ],
        "block_rows": 2,
        "block_cols": 3
    }

]

def is_valid(board, row, col, value, block_rows, block_cols):

    n = len(board)

    for c in range(n):
        if board[row][c] == value:
            return False

    for r in range(n):
        if board[r][col] == value:
            return False

    start_row = (row // block_rows) * block_rows
    start_col = (col // block_cols) * block_cols

    for r in range(start_row, start_row + block_rows):
        for c in range(start_col, start_col + block_cols):
            if board[r][c] == value:
                return False

    return True


def get_candidates(board, row, col, block_rows, block_cols):

    n = len(board)
    candidates = []

    for value in range(1, n + 1):

        if is_valid(
            board, row, col, value,
            block_rows, block_cols
        ):
            candidates.append(value)

    return candidates


def validate_input(board, block_rows, block_cols, name):

    n = len(board)

    if n == 0:
        raise ValueError(f"{name}: Board is empty.")

    if any(len(row) != n for row in board):
        raise ValueError(f"{name}: Board must be N x N.")

    if block_rows * block_cols != n:
        raise ValueError(f"{name}: Invalid sub-grid size.")

    if n % block_rows != 0 or n % block_cols != 0:
        raise ValueError(f"{name}: Invalid block dimensions.")

    for row in board:
        for value in row:
            if not isinstance(value, int) or not (0 <= value <= n):
                raise ValueError(f"{name}: Invalid cell value.")

    for r in range(n):
        for c in range(n):

            value = board[r][c]

            if value != 0:
                board[r][c] = 0

                valid = is_valid(
                    board, r, c, value,
                    block_rows, block_cols
                )

                board[r][c] = value

                if not valid:
                    raise ValueError(
                        f"{name}: Conflicting clues at ({r}, {c})."
                    )


def validate_solution(solution, original, block_rows, block_cols):

    n = len(solution)
    expected = set(range(1, n + 1))

    if any(0 in row for row in solution):
        return False

    for r in range(n):
        for c in range(n):
            if original[r][c] != 0:
                if solution[r][c] != original[r][c]:
                    return False

    for row in solution:
        if set(row) != expected:
            return False

    for c in range(n):
        column = {solution[r][c] for r in range(n)}

        if column != expected:
            return False

    for start_r in range(0, n, block_rows):
        for start_c in range(0, n, block_cols):

            values = set()

            for r in range(start_r, start_r + block_rows):
                for c in range(start_c, start_c + block_cols):
                    values.add(solution[r][c])

            if values != expected:
                return False

    return True


def dfs_backtracking(board, block_rows, block_cols, stats):

    n = len(board)

    empty_cell = None

    for r in range(n):
        for c in range(n):

            if board[r][c] == 0:
                empty_cell = (r, c)
                break

        if empty_cell is not None:
            break

    if empty_cell is None:
        return True

    stats["expanded_nodes"] += 1

    row, col = empty_cell

    for value in range(1, n + 1):

        if is_valid(
            board, row, col, value,
            block_rows, block_cols
        ):

            board[row][col] = value

            if dfs_backtracking(
                board, block_rows, block_cols, stats
            ):
                return True

            board[row][col] = 0
            stats["backtracks"] += 1

    return False


def dfs_mrv(board, block_rows, block_cols, stats):

    n = len(board)

    if all(value != 0 for row in board for value in row):
        return True

    stats["expanded_nodes"] += 1

    best_cell = None
    best_candidates = None

    for r in range(n):
        for c in range(n):

            if board[r][c] == 0:

                candidates = get_candidates(
                    board, r, c,
                    block_rows, block_cols
                )

                if len(candidates) == 0:
                    return False

                if (
                    best_cell is None
                    or len(candidates) < len(best_candidates)
                ):
                    best_cell = (r, c)
                    best_candidates = candidates

    row, col = best_cell

    for value in best_candidates:

        board[row][col] = value

        if dfs_mrv(
            board, block_rows, block_cols, stats
        ):
            return True

        board[row][col] = 0
        stats["backtracks"] += 1

    return False


def benchmark(solver, test_case):

    times = []
    expanded_nodes = []
    backtracks = []

    original = test_case["board"]
    block_rows = test_case["block_rows"]
    block_cols = test_case["block_cols"]

    last_solution = None
    all_runs_valid = True

    for _ in range(RUNS):

        board = [row[:] for row in original]

        stats = {
            "expanded_nodes": 0,
            "backtracks": 0
        }

        start = time.perf_counter()

        solved = solver(
            board, block_rows, block_cols, stats
        )

        end = time.perf_counter()

        elapsed = (end - start) * 1000

        valid = solved and validate_solution(
            board, original, block_rows, block_cols
        )

        if not valid:
            all_runs_valid = False

        if solved:
            last_solution = board

        times.append(elapsed)
        expanded_nodes.append(stats["expanded_nodes"])
        backtracks.append(stats["backtracks"])

    return {
        "solved": all_runs_valid,
        "avg_time": mean(times),
        "expanded_nodes": round(mean(expanded_nodes)),
        "backtracks": round(mean(backtracks)),
        "solution": last_solution
    }


def main():

    algorithms = [
        ("DFS Backtracking", dfs_backtracking),
        ("DFS + MRV", dfs_mrv)
    ]

    results = []

    print("\n========== SUDOKU EXPERIMENT ==========")
    print("Number of runs per test case:", RUNS)

    for test in TEST_CASES:

        name = test["name"]
        difficulty = test["difficulty"]
        board = test["board"]

        if not board:
            raise ValueError(
                f"{name}: Please enter your Sudoku board first."
            )

        validate_input(
            board,
            test["block_rows"],
            test["block_cols"],
            name
        )

        n = len(board)

        print(f"\nTest Case: {name} ({n}x{n})")

        for algorithm_name, solver in algorithms:

            result = benchmark(solver, test)

            row = {
                "Test Case": name,
                "Difficulty": difficulty,
                "Board Size": f"{n}x{n}",
                "Algorithm": algorithm_name,
                "Runs": RUNS,
                "Valid Solution": result["solved"],
                "Avg Time (ms)": round(result["avg_time"], 6),
                "Expanded Nodes": result["expanded_nodes"],
                "Backtracks": result["backtracks"]
            }

            results.append(row)

            print(
                f"{algorithm_name:20} | "
                f"Time: {result['avg_time']:.6f} ms | "
                f"Nodes: {result['expanded_nodes']} | "
                f"Backtracks: {result['backtracks']} | "
                f"Valid: {result['solved']}"
            )

    fieldnames = [
        "Test Case",
        "Difficulty",
        "Board Size",
        "Algorithm",
        "Runs",
        "Valid Solution",
        "Avg Time (ms)",
        "Expanded Nodes",
        "Backtracks"
    ]

    with open(
        "sudoku_results.csv",
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(results)

    print("\n======================================")
    print("Experiment completed!")
    print("Results saved to: sudoku_results.csv")


if __name__ == "__main__":
    main()

print("\n===== EMPTY CELLS =====")

for test in TEST_CASES:
    board = test["board"]

    empty_cells = sum(
        cell == 0
        for row in board
        for cell in row
    )

    print(test["name"], ":", empty_cells)
