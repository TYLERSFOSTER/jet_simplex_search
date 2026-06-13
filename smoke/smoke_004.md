# smoke_004 count argument

Command:

```text
uv run python smoke/smoke_004.py
```

Output:

```text
Skeleton simplex counts
tier | dim 0 | dim 1 | dim 2 | dim 3 | dim 4
-----+-------+-------+-------+-------+------
   0 |     2 |     2 |     2 |     2 |     2

Tier-0 H-lift counts
            metric | dim 0 | dim 1 | dim 2 | dim 3 | dim 4
-------------------+-------+-------+-------+-------+------
positive addresses |     2 |     0 |     0 |     0 |     0
     total H-lifts |     2 |     0 |     0 |     0 |     0
```

No error found.

The graph has two isolated vertices, `a` and `b`. Normalization adds exactly
one formal identity at each vertex, but there is no edge between the two
vertices.

For any dimension `d`, the only valid simplices are the totally degenerate
ones:

```text
(a, a, ..., a)
(b, b, ..., b)
```

Mixed words such as `(a, b)` or `(a, a, b)` would require a nonidentity edge
between `a` and `b`, which does not exist. Therefore every dimension has
exactly two simplices.
