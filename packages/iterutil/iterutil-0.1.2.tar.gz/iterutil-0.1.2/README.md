# iterutil

Small iterator wrapper inspired by Rust’s iterator chaining.

`iterutil.it` (aka `iterutil.iterate` / `iterutil.iterator`) wraps any `Iterable[T]` and provides a fluent, lazy API for common iterator operations (filter/map/zip/etc.).

The underlying type is `iterutil.Iterator`, but the recommended public constructor is `it(...)`.

## Requirements

- Python `>= 3.13` (PEP 695 type parameter syntax).

## Install

Once published to PyPI:

```bash
pip install iterutil
```

For local development:

```bash
pip install -e .
```

## Quick start

```python
from iterutil import it

nums = it([1, 2, 3, 4, 5, 6, 7])

result = (
		nums
		.filter(lambda x: x % 2 == 1)
		.map(lambda x: x * 2)
		.collect(list)
)

assert result == [2, 6, 10, 14]
```

## API overview

All chainable methods are lazy (they return a new `Iterator[...]` wrapping an underlying iterable). Start a chain with `it(...)`.

### Transform / filter

- `filter(fn)`: keep elements where `fn(x)` is true.
- `filterfalse(fn)`: keep elements where `fn(x)` is false.
- `map(fn)`: transform elements.
- `filter_map(fn)`: Rust-style `filter_map`; `fn(x)` must return `T | None`.
	- `None` is dropped
	- any non-`None` value is kept

```python
from iterutil import it

out = it([1, 2, 3, 4]).filter_map(lambda x: x * 2 if x % 2 else None).collect(list)
assert out == [2, 6]
```

### Combining

- `chain(*others)`: concatenate iterables.
- `zip(other)`: pair elements (stops at the shortest).
- `enumerate()`: pairs with indices starting at 0.
- `flatten()`: flattens one level (only meaningful when the items are iterables).

```python
from iterutil import it

paired = it([1, 2, 3]).zip(["a", "b"]).collect(list)
assert paired == [(1, "a"), (2, "b")]

flat = it([[1, 2], [], [3]]).flatten().collect(list)
assert flat == [1, 2, 3]
```

### Terminal operations (consume the iterator)

- `collect(cls)`: materialize into a container type, e.g. `list`, `set`, `tuple`.
- `sum()`, `min()`, `max()`: delegate to Python built-ins.
- `fold(fn, initial)`: left fold; equivalent to repeatedly applying `fn(acc, item)` starting from `initial`.
- `reduce(fn, initial=None)`: like `functools.reduce`; if `initial` is omitted and the iterator is empty, it raises.

```python
from iterutil import it

total = it([1, 2, 3]).fold(lambda acc, x: acc + x, 0)
assert total == 6
```

### Side effects

- `for_each(fn)`: apply `fn(x)` to each item.
- `try_for_each(fn)`: like `for_each`, but skips items where `fn(x)` raises.

## Slicing

`Iterator` supports slice syntax using `itertools.islice` semantics:

```python
from iterutil import it

nums = it([1, 2, 3, 4, 5, 6, 7])
assert nums[1:6:2].collect(list) == [2, 4, 6]
```

## Important notes

- Iterators are generally one-pass: once consumed, they can’t be “rewound”.
- If you wrap a container (like a list), you can create a fresh `Iterator` at any time.