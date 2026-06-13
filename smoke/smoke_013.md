# smoke_013 count argument

Command:

```text
uv run python smoke/smoke_013.py
```

Output:

```text
Skeleton simplex counts
tier | dim 0 | dim 1 | dim 2 | dim 3 | dim 4
-----+-------+-------+-------+-------+------
   0 |     4 |     6 |     8 |    10 |    12

Tier-0 H-lift counts
            metric | dim 0 | dim 1 | dim 2 | dim 3 | dim 4
-------------------+-------+-------+-------+-------+------
positive addresses |     4 |     2 |     0 |     0 |     0
     total H-lifts |     4 |     2 |     0 |     0 |     0
```

No error found.

The graph is two disconnected directed edges:

```text
a -> b
c -> d
```

No simplex can mix the two components, because there are no cross-component
edges. Valid supports are:

```text
{a}, {b}, {c}, {d}, {a,b}, {c,d}
```

For dimension `d`:

- 4 totally degenerate simplices;
- `d` nonconstant degeneracies over `a -> b`;
- `d` nonconstant degeneracies over `c -> d`.

So the count is:

```text
4 + 2d
```

For dimensions `0..4`, this is:

```text
4, 6, 8, 10, 12
```
