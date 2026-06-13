# smoke_007 count argument

Command:

```text
uv run python smoke/smoke_007.py
```

Output:

```text
Skeleton simplex counts
tier | dim 0 | dim 1 | dim 2 | dim 3 | dim 4
-----+-------+-------+-------+-------+------
   0 |     3 |     6 |    10 |    15 |    21

Tier-0 H-lift counts
            metric | dim 0 | dim 1 | dim 2 | dim 3 | dim 4
-------------------+-------+-------+-------+-------+------
positive addresses |     3 |     3 |     1 |     0 |     0
     total H-lifts |     3 |     3 |     1 |     0 |     0
```

No error found.

The graph is the transitive directed triangle:

```text
a -> b
a -> c
b -> c
```

Together with identities, this is the total order:

```text
a <= b <= c
```

A dimension `d` simplex is exactly a nondecreasing word of length `d + 1` in
the three symbols `a`, `b`, and `c`.

The number of nondecreasing words of length `d + 1` over 3 symbols is the
stars-and-bars count:

```text
binomial((d + 1) + 3 - 1, 3 - 1) = binomial(d + 3, 2)
```

For dimensions `0..4`, this gives:

```text
3, 6, 10, 15, 21
```
