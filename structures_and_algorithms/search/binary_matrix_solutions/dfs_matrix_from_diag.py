#!/usr/bin/python3

"""Calculates which matrices correspond to given diagonal, use like so: <this file> 3 1 1 1 2 2"""
""" Constraints:
    Each row and column has a set sum
    We know that every solution can be represented as upper-triangular, so we only need to focus on 1's in half the area
        The upper triangular form also demands a diagonal of 1's - no need to "guess" those.
        Middle of diagonal is representative of last row sum, and first colum sum, i.e. you have 2 '1's there.

    Example: given this diag: [3 1 1 1 2 2]
    We get the single solution:
        1 1 1
        0 1 0
        0 0 1

    Meaning the whole laplacian matrix would look like so:
         3  0  0 -1 -1 -1
         0  1  0  0 -1  0
         0  0  1  0  0 -1
        -1  0  0  1  0  0
        -1 -1  0  0  2  0
        -1  0 -1  0  0  2

"""

import numpy as np

def find_next_available_by_constraints(row_constraints, col_constraints, from_row, past_col, is_upper_diag=True):
    constraint_length = len(row_constraints)
    for i in range(from_row, constraint_length):  # look for valid row
        if row_constraints[i] > 0:  # row is fine
            starting_col = past_col+1 if i == from_row else i+1 if is_upper_diag else 0
            for j in range(starting_col, constraint_length):  # look for valid col
                if col_constraints[j] > 0:
                    return i, j
    return None, None

def coords_to_complete_matrix(coords, mat_size, is_upper_diag=True):
    """converts a collection of coordinates to a 2D int matrix of 0s and 1s"""
    solution_mat = np.eye(mat_size, dtype=int) if is_upper_diag else np.zeros((mat_size, mat_size), dtype=int)
    for coord in coords:  # reconstruct the solution
        solution_mat[coord[0]][coord[1]] = 1
    return solution_mat

def solve(diag, is_limited_to_ut=True):
    """ For each placement, try placing '1' and eliminate options through updated sum-amount
        After finishing an attempt, backtrack by making the last-set '1' into '0' and continue on... It's DFS.

        How: every time, we "pick" the next viable coord. At every dead-end we cancel the last pick but still only scan
        after its location. This means we can't repeat previous paths - we always scan for new solutions past a
        cancelled past pick."""

    solutions_found = []  # list of matrices

    updated_diag = (np.array(diag) - 1).tolist() if is_limited_to_ut else diag  # subtract 1 from all sums if we start with diagonal of 1s
    row_sum_remaining = updated_diag[:len(updated_diag) // 2]
    col_sum_remaining = updated_diag[len(updated_diag) // 2:]

    path_taken = []

    def next_and_mark(row_from, col_exceed):
        i, j = find_next_available_by_constraints(row_sum_remaining, col_sum_remaining, row_from, col_exceed, is_limited_to_ut)
        if i is not None and j is not None:  # valid: mark and lower appropriate sums by 1
            path_taken.append((i, j))  # mark choice
            row_sum_remaining[i] -= 1
            col_sum_remaining[j] -= 1
        return i, j

    row, col = next_and_mark(0, -1)  # find first viable coord
    while path_taken :
        if row is None or col is None:  # if reached the end
            if np.any(row_sum_remaining) or np.any(col_sum_remaining):  # didn't fulfill all constraints (some are non-0); this combination is no good.
                pass
            else:
                solutions_found.append(path_taken.copy())  # add to solutions (without last one, it's defective)

            # "try without" - cancel last coord and continue looking
            row, col = path_taken.pop()
            row_sum_remaining[row] += 1
            col_sum_remaining[col] += 1

        # find next
        row, col = next_and_mark(row, col)


    print(f"All {'upper-triangular ' if is_limited_to_ut else ''}solutions ({len(solutions_found)} total) for {diag}")
    mat_size = len(diag) // 2
    for solution in solutions_found:
        print(f"{coords_to_complete_matrix(solution, mat_size)}\n")

    return solutions_found


if __name__ == "__main__":
    import sys
    if not len(sys.argv) >= 2:
        print("You need to provide diagonal as array. Like so: <this file> 3 1 1 1 2 2")
        exit(1)
    else:
        print('Starting recovery-theorem calculations.')
        int_list = [int(arg.replace(',', '')) for arg in sys.argv[1:]]
        solve(int_list)
    print('Finished recovery-theorem calculations.')




import unittest

class TestAlgorithms(unittest.TestCase):

    def test_find_next(self):
        coord = find_next_available_by_constraints([2,0,0], [0,1,1], 0, -1)
        self.assertEqual(coord, (0,1))
        coord = find_next_available_by_constraints([2,0,0], [0,1,1], 0, 1)
        self.assertEqual(coord, (0,2))
        coord = find_next_available_by_constraints([2,0,0], [0,1,1], 0, 2)
        self.assertEqual(coord, (None, None))

    def test_results_picking_on_input(self):
        def str_to_intmat(mat_str):
            return np.array([list(map(int, row.split())) for row in mat_str.strip().split('\n')], dtype=int)

        find_me = str_to_intmat("""
            1 1 1 1 0 0 0 0 0
            0 1 0 0 0 0 0 0 0
            0 0 1 1 0 0 0 0 0
            0 0 0 1 0 0 0 0 0
            0 0 0 0 1 1 1 0 0
            0 0 0 0 0 1 1 0 0
            0 0 0 0 0 0 1 0 0
            0 0 0 0 0 0 0 1 1
            0 0 0 0 0 0 0 0 1
            """)

        def any_match(matrix):
            diag = np.concatenate((np.sum(matrix, axis=1), np.sum(matrix, axis=0)))
            matrix_np = np.array(matrix)
            for solution in solve(diag):
                reconstructed_matrix = coords_to_complete_matrix(solution, len(matrix))
                if np.array_equal(matrix_np, reconstructed_matrix):
                    return True
            return False

        self.assertTrue(any_match(find_me))

    def test_result_count(self):
        """NOTE: the promise for the expected final count is in a different algorithm's output; it's no guarantee!!"""
        def asrt_count(arr, count, ut_only=True):
            self.assertEqual(len(solve(arr, ut_only)), count)

        asrt_count([3, 1, 1, 1, 2, 2], 1)
        asrt_count([1, 2, 2, 2, 1, 1, 1, 1, 2, 3], 2)
        asrt_count([1, 2, 2, 2, 1, 1, 1, 1, 2, 3], 258, ut_only=False)
        asrt_count([1, 3, 1, 2, 2, 1, 1, 1, 1, 2, 2, 3], 2)
        asrt_count([1, 3, 3, 2, 1, 1, 1, 1, 1, 3, 2, 3], 3)
        asrt_count([1, 3, 4, 4, 2, 2, 1, 1, 1, 1, 2, 2, 4, 4], 0)
        asrt_count([1, 3, 3, 3, 2, 2, 1, 1, 1, 1, 2, 2, 3, 3], 0)
        asrt_count([4, 1, 2, 1, 3, 2, 1, 2, 1, 1, 2, 2, 3, 1, 2, 3, 1, 2], 1)
        asrt_count([4, 3, 3, 3, 2, 1, 1, 2, 2, 2, 4, 5], 10)

