# smoke_006 count argument

Command:

```text
uv run python smoke/smoke_006.py
```

Output:

```text
Skeleton simplex counts
tier | dim 0 | dim 1 | dim 2 | dim 3 | dim 4
-----+-------+-------+-------+-------+------
   0 |     3 |     5 |     7 |     9 |    11

Tier-0 H-lift counts
            metric | dim 0 | dim 1 | dim 2 | dim 3 | dim 4
-------------------+-------+-------+-------+-------+------
positive addresses |     3 |     2 |     0 |     0 |     0
     total H-lifts |     3 |     2 |     0 |     0 |     0
```

No error found.

The graph is the path:

```text
a -> b -> c
```

There is no edge `a -> c`. That missing face is decisive: a word using all
three vertices, such as `(a, b, c)`, is not a 2-simplex because the directed
flag condition requires the face edge `a -> c`.

So valid supports are only:

```text
{a}, {b}, {c}, {a,b}, {b,c}
```

For dimension `d`:

- 3 totally degenerate simplices, one at each vertex;
- `d` nonconstant degeneracies over `a -> b`;
- `d` nonconstant degeneracies over `b -> c`.

Thus:

```text
3 + 2d
```

For dimensions `0..4`, this is:

```text
3, 5, 7, 9, 11
```
