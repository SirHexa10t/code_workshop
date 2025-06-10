#!/usr/bin/python3


class HistoryArray:
    """Fast-access and item-history-preserving array"""

    def __init__(self, initial_items):
        self.array = tuple([item,] for item in initial_items)
        self.cached_array = None  # Cache for get_array result
        self.is_cache_outdated = True  # Flag to check if cache needs updating

    def push(self, index, value):
        """Push a value to the list at the given index and mark cache as outdated."""
        if index < 0 or index >= len(self.array):
            raise IndexError("Index out of range")
        self.array[index].append(value)
        self.is_cache_outdated = True  # Mark that cache needs update

    def pop(self, index):
        """Pop a value from the list at the given index and mark cache as outdated."""
        if index < 0 or index >= len(self.array):
            raise IndexError("Index out of range")
        if len(self.array[index]) == 1:
            raise ValueError(f"Cannot pop the only remaining item at index {index}")
        self.array[index].pop()
        self.is_cache_outdated = True  # Mark that cache needs update

    def get_array(self):
        """Return the last item from each list in the array, using cache if possible."""
        if self.is_cache_outdated:
            self.cached_array = [lst[-1] for lst in self.array]
            self.is_cache_outdated = False
        return self.cached_array

    def __getitem__(self, index):
        """Overloaded list brackets ("[]")! Retrieve the last item from the list at the given index using indexing syntax."""
        if index < 0 or index >= len(self.array):
            raise IndexError("Index out of range")
        return self.array[index][-1]  # Return the last item from the list at the index




import unittest

class TestHistoryArray(unittest.TestCase):

    def setUp(self):
        self.instance = HistoryArray([10, 20, 30])


    def test_array_initial(self):
        self.assertEqual(self.instance.get_array(), [10, 20, 30])
        self.assertEqual(self.instance.get_array(), [10, 20, 30])  # once more to be sure
        self.instance.push(0, 15)


    def test_push_pop(self):
        """Test pushing new values."""
        self.instance.push(0, 15)
        self.assertEqual(self.instance.get_array(), [15, 20, 30])
        self.assertEqual(self.instance.get_array(), [15, 20, 30])  # once more to be sure
        self.instance.push(0, 100)
        self.assertEqual(self.instance.get_array(), [100, 20, 30])
        # test double-pop
        self.instance.pop(0)
        self.instance.pop(0)
        self.assertEqual(self.instance.get_array(), [10, 20, 30])
        self.assertEqual(self.instance.get_array(), [10, 20, 30])  # once more to be sure

    def test_get(self):
        self.assertEqual(self.instance[0], 10)
        self.instance.push(2, 100)
        self.assertEqual(self.instance[2], 100)


    # errors

    def test_pop_last_remaining_item(self):
        """Test that popping the last remaining item raises an error."""
        with self.assertRaises(ValueError):
            self.instance.pop(0)  # Attempt to pop the only remaining item in index 0

    def test_index_out_of_range(self):
        """Test that an IndexError is raised for out-of-range indices."""
        with self.assertRaises(IndexError):
            self.instance.push(3, 40)  # Index out of range
        with self.assertRaises(IndexError):
            self.instance.pop(3)  # Index out of range

    def test_negative_index(self):
        """Test that a negative index raises an IndexError."""
        with self.assertRaises(IndexError):
            self.instance.push(-1, 5)
        with self.assertRaises(IndexError):
            self.instance.pop(-1)