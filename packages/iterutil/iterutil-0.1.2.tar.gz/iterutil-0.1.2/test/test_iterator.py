from iterutil import Iterator
from unittest import TestCase


class TestIterator(TestCase):
    def setUp(self):
        self.inner = [1, 2, 3, 4, 5, 6, 7]
        self.iterator = Iterator(self.inner)

    def test_passthrough(self):
        assert self.inner is self.iterator.inner
        for a, b in zip(self.inner, self.iterator):
            self.assertTrue(a == b)

    def test_filter(self):
        filtered = self.iterator.filter(lambda x: bool(x % 2))
        for a in filtered:
            self.assertTrue(a % 2 == 1)

    def test_map(self):
        mapped = self.iterator.map(lambda x: x * 2)
        for a, b in zip(self.iterator, mapped):
            self.assertTrue(b == a * 2)

    def test_for_each(self):
        collection = []
        self.iterator.for_each(lambda x: collection.append(x))
        self.assertEqual(collection, self.inner)

    def test_try_for_each(self):
        collection = []

        def fn(v: int):
            if v % 2:
                raise Exception()
            else:
                collection.append(v)

        self.iterator.try_for_each(fn=fn)
        self.assertEqual(collection, [2, 4, 6])

    def test_filter_map(self):
        target = [2, 6, 10, 14]
        product = list(self.iterator.filter_map(lambda x: x * 2 if x % 2 else None))
        self.assertEqual(target, product)

    def test_collect(self):
        collected: list = self.iterator.filter(lambda x: bool(x % 2)).collect(list)
        self.assertEqual(collected, [1, 3, 5, 7])

    def test_filterfalse(self):
        # keep evens (i.e., filter out odds)
        product = list(self.iterator.filterfalse(lambda x: bool(x % 2)))
        self.assertEqual(product, [2, 4, 6])

    def test_chain(self):
        product = list(Iterator([1, 2]).chain([3, 4], [5]))
        self.assertEqual(product, [1, 2, 3, 4, 5])

    def test_enumerate(self):
        product = list(Iterator(["a", "b", "c"]).enumerate())
        self.assertEqual(product, [(0, "a"), (1, "b"), (2, "c")])

    def test_zip(self):
        product = list(Iterator([1, 2, 3]).zip(["a", "b"]))
        self.assertEqual(product, [(1, "a"), (2, "b")])

    def test_flatten(self):
        product = list(Iterator([[1, 2], [], [3], [4, 5]]).flatten())
        self.assertEqual(product, [1, 2, 3, 4, 5])

    def test_fold_sum(self):
        total = self.iterator.fold(lambda acc, x: acc + x, 0)
        self.assertEqual(total, sum(self.inner))

    def test_fold_empty_returns_init(self):
        total = Iterator([]).fold(lambda acc, x: acc + x, 123)
        self.assertEqual(total, 123)

    def test_slice_getitem(self):
        product = list(self.iterator[1:6:2])
        self.assertEqual(product, [2, 4, 6])

    def test_slice_getitem_rejects_int_index(self):
        with self.assertRaises(TypeError):
            _ = self.iterator[0]