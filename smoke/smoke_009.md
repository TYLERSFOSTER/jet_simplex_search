# smoke_009 count argument

Command:

```text
uv run python smoke/smoke_009.py
```

Output:

```text
tier | dim 0 | dim 1 | dim 2 | dim 3 | dim 4
-----+-------+-------+-------+-------+------
   0 |     3 |     5 |     7 |     9 |    11
```

No error found.

The graph is an out-fork:

```text
a -> b
a -> c
```

There is no edge between `b` and `c`. Therefore a simplex cannot use both
targets `b` and `c`, because the directed flag condition would need a face
edge between them.

Valid supports are only:

```text
{a}, {b}, {c}, {a,b}, {a,c}
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
