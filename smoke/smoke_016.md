# smoke_016 count argument

Command:

```text
uv run python smoke/smoke_016.py
```

Output:

```text
Skeleton simplex counts
tier | dim 0 | dim 1 | dim 2 | dim 3 | dim 4
-----+-------+-------+-------+-------+------
   0 |     3 |     6 |    10 |    15 |    21
   1 |     2 |     3 |     4 |     5 |     6

Tier-0 H-lift counts
            metric | dim 0 | dim 1 | dim 2 | dim 3 | dim 4
-------------------+-------+-------+-------+-------+------
positive addresses |     3 |     3 |     1 |     0 |     0
     total H-lifts |     3 |     3 |     1 |     0 |     0
```

No error found.

At tier `0`, the graph is the transitive triangle:

```text
a -> b
a -> c
b -> c
```

So the tier `0` counts are the same as `smoke_007`: dimension `d` simplices
are nondecreasing words of length `d + 1` over three symbols. The count is:

```text
binomial(d + 3, 2)
```

For dimensions `0..4`, this gives:

```text
3, 6, 10, 15, 21
```

The edge `a -> b` is labeled `collapse`, so the `LabelBlockSchema` contracts
`a` and `b` into one downstairs cell. Tier `1` therefore has two vertices:

```text
X = {a,b}
c
```

and one nonidentity edge:

```text
X -> c
```

Thus tier `1` has the same counts as the one-edge graph. For dimension `d`,
the count is:

```text
2 + d
```

For dimensions `0..4`, this gives:

```text
2, 3, 4, 5, 6
```

This is also the intended quotient-tower behavior: the upstairs nondegenerate
edge `a -> b` lives over a downstairs identity at `X`, while the whole upstairs
triangle lives over downstairs degenerate simplex addresses.
