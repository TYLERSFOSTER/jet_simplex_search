# smoke_012 count argument

Command:

```text
uv run python smoke/smoke_012.py
```

Output:

```text
Skeleton simplex counts
tier | dim 0 | dim 1 | dim 2 | dim 3 | dim 4
-----+-------+-------+-------+-------+------
   0 |     4 |     9 |    16 |    25 |    36

Tier-0 H-lift counts
            metric | dim 0 | dim 1 | dim 2 | dim 3 | dim 4
-------------------+-------+-------+-------+-------+------
positive addresses |     4 |     5 |     2 |     0 |     0
     total H-lifts |     4 |     5 |     2 |     0 |     0
```

No error found.

The graph is a closed diamond:

```text
a -> b -> d
a -> c -> d
a -> d
```

There is still no edge between `b` and `c`. Therefore the only 3-vertex
nondegenerate supports are:

```text
{a,b,d}
{a,c,d}
```

There is no 4-vertex support because `{a,b,c,d}` would require a face between
`b` and `c`.

For dimension `d`, count by support size:

- singleton supports: `4`;
- edge supports: `5d`, because there are 5 nonidentity edges and each edge
  contributes `d` nonconstant degeneracies;
- triangle supports: `2 * binomial(d, 2)`, because each of the two triangles
  contributes the number of positive 3-part compositions of `d + 1`.

So:

```text
4 + 5d + 2 * binomial(d, 2)
= 4 + 5d + d(d - 1)
= (d + 2)^2
```

For dimensions `0..4`, this gives:

```text
4, 9, 16, 25, 36
```
