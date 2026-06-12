# smoke_011 count argument

Command:

```text
uv run python smoke/smoke_011.py
```

Output:

```text
tier | dim 0 | dim 1 | dim 2 | dim 3 | dim 4
-----+-------+-------+-------+-------+------
   0 |     4 |     8 |    12 |    16 |    20
```

No error found.

The graph is an open diamond:

```text
a -> b -> d
a -> c -> d
```

There is no edge `a -> d`, and there is no edge between `b` and `c`.

So even though there are length-2 paths from `a` to `d`, those paths do not
create 2-simplices. For example, `(a, b, d)` is invalid because the face
`a -> d` is missing.

Valid supports are only the four singleton supports and the four edge supports:

```text
{a}, {b}, {c}, {d}
{a,b}, {a,c}, {b,d}, {c,d}
```

For dimension `d`, the count is:

```text
4 + 4d
```

For dimensions `0..4`, this is:

```text
4, 8, 12, 16, 20
```
