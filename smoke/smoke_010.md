# smoke_010 count argument

Command:

```text
uv run python smoke/smoke_010.py
```

Output:

```text
tier | dim 0 | dim 1 | dim 2 | dim 3 | dim 4
-----+-------+-------+-------+-------+------
   0 |     3 |     5 |     7 |     9 |    11
```

No error found.

The graph is an in-fork:

```text
a -> c
b -> c
```

There is no edge between `a` and `b`. Therefore no simplex can use all three
vertices, because any 2-simplex involving `a`, `b`, and `c` would require a
directed face between `a` and `b`.

Valid supports are only:

```text
{a}, {b}, {c}, {a,c}, {b,c}
```

For dimension `d`, this gives:

```text
3 + 2d
```

The `3` counts the totally degenerate simplices, and each of the two edges
contributes `d` nonconstant degeneracies. For dimensions `0..4`, this is:

```text
3, 5, 7, 9, 11
```
