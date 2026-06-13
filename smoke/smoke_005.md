# smoke_005 count argument

Command:

```text
uv run python smoke/smoke_005.py
```

Output:

```text
Skeleton simplex counts
tier | dim 0 | dim 1 | dim 2 | dim 3 | dim 4
-----+-------+-------+-------+-------+------
   0 |     2 |     3 |     4 |     5 |     6

Tier-0 H-lift counts
            metric | dim 0 | dim 1 | dim 2 | dim 3 | dim 4
-------------------+-------+-------+-------+-------+------
positive addresses |     2 |     1 |     0 |     0 |     0
     total H-lifts |     2 |     1 |     0 |     0 |     0
```

No error found.

The graph is one directed edge:

```text
a -> b
```

with formal identities added at `a` and `b`.

For dimension `d`, there are two totally degenerate simplices:

```text
a repeated d + 1 times
b repeated d + 1 times
```

There are also `d` nonconstant degeneracies over the edge `a -> b`. These are
the words:

```text
a^r b^(d + 1 - r), for 1 <= r <= d
```

So the count is:

```text
2 + d
```

For dimensions `0..4`, this is:

```text
2, 3, 4, 5, 6
```
