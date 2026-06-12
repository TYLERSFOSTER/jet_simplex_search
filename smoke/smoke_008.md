# smoke_008 count argument

Command:

```text
uv run python smoke/smoke_008.py
```

Output:

```text
tier | dim 0 | dim 1 | dim 2 | dim 3 | dim 4
-----+-------+-------+-------+-------+------
   0 |     4 |    10 |    20 |    35 |    56
```

No error found.

The graph is the complete directed flag graph on the total order:

```text
a <= b <= c <= d
```

It contains every edge from an earlier vertex to a later vertex, plus formal
identities after normalization. Therefore a dimension `d` simplex is exactly a
nondecreasing word of length `d + 1` in four symbols.

The stars-and-bars count is:

```text
binomial((d + 1) + 4 - 1, 4 - 1) = binomial(d + 4, 3)
```

For dimensions `0..4`, this gives:

```text
4, 10, 20, 35, 56
```
