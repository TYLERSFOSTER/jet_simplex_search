# Cubical Out/In And Seam Matching Discussion

## Status

Discussion scaffold for the cubical completion/search mode.

This document records the current working idea so the Project Owner can walk
through it, correct notation, and decide which version should become the
blueprint.

It is not an implementation plan.

## Starting Point

The cubical mode should treat an `n`-cube in a graph as an arrangement of
vertices and directed edges that can serve as the `1`-skeleton of an `n`-cube.

Equivalently, an `n`-cube has a Boolean-lattice address:

```text
P({1, ..., n})
```

or, in bitmask notation:

```text
{0,1}^n
```

A cube based at a vertex `s` sends the initial subset/bitmask to `s`:

```text
emptyset |-> s
```

and has directed graph edges along cover relations:

```text
I -> I union {j}
```

or:

```text
epsilon -> epsilon + e_j
```

where the second expression means flipping one coordinate from `0` to `1`.

## Graded Cubes

For each vertex `s`, define:

```text
Cube^k(s) = { k-cubes whose initial vertex is s }
```

The first levels are:

```text
Cube^0(s) = { s }
Cube^1(s) = directed edges with initial vertex s
Cube^2(s) = directed square 1-skeletons with initial vertex s
Cube^3(s) = directed cube 1-skeletons with initial vertex s
```

This mirrors the simplex-side grading:

```text
Out^m(s) = { m-simplices with initial vertex s }
```

but the extension structure is not linear. A simplex extends by appending one
new target vertex. A cube extends by completing a Boolean-lattice pattern.

## The Lower-Poset Matching Problem

Suppose all cubes through dimension `k` have already been found.

To construct a `(k+1)`-cube based at `s`, one needs a compatible lower shell of
`k`-cubes.

The lower shell is not an arbitrary collection of `k+1` elements of
`Cube^k(s)`. It is a specific Boolean-poset arrangement: the `k+1` lower
hyperfaces through the initial vertex must agree on all shared
`(k-1)`-faces.

Naively, this asks for:

```text
choose k+1 cubes from Cube^k(s)
check all overlaps
```

Even if the overlap check itself is only:

```text
binomial(k+1, 2)
```

pair checks, the hard part is finding candidate collections without doing a
large combinatorial join over all of `Cube^k(s)`.

So the design goal is:

```text
make lower-poset compatibility a lookup problem
```

not:

```text
make lower-poset compatibility a raw matching problem
```

## Coface Out Sets

The first proposed cubical analogue of the simplex `Out` cache is a coface
frontier.

For each `(k-1)`-cube:

```text
kappa in Cube^{k-1}(s)
```

define:

```text
Out(kappa) = { kappa' in Cube^k(?) : kappa is a face of kappa' }
```

In words:

```text
Out(kappa)
```

is the set of one-dimension-higher cubes that contain `kappa` as a face.

This is not an outgoing-vertex frontier. It is an incidence frontier:

```text
lower cube -> higher cofaces
```

The base vertex of the coface may or may not be the same `s`, depending on
which face of the higher cube `kappa` occupies. Therefore, the fully general
index should be over cube records themselves, not only over `Cube^k(s)`.

## Fast Lower-Shell Checks

With coface `Out` sets, a shared face becomes the index for compatibility.

If two `k`-cubes `C_i` and `C_j` are supposed to intersect in a particular
`(k-1)`-cube `kappa_ij`, then the compatibility check becomes:

```text
C_i in Out(kappa_ij)
C_j in Out(kappa_ij)
```

or:

```text
{C_i, C_j} subset Out(kappa_ij)
```

So a lower shell can be validated by membership checks in precomputed coface
frontiers.

This is the key proposed pruning move:

```text
lower-poset matching becomes finite incidence lookup
```

rather than direct comparison of vertex tables or edge tables.

## Example: Squares

A `2`-cube based at `s` is a square:

```text
s  ->  a
|      |
v      v
b  ->  c
```

The lower data through `s` consists of two `1`-cubes:

```text
s -> a
s -> b
```

The terminal vertex `c` must be reachable from both `a` and `b`:

```text
a -> c
b -> c
```

In the simplest graph-recognition version, candidate terminals lie in:

```text
Out_vertex(a) cap Out_vertex(b)
```

But once squares are recorded, each initial edge also has a coface frontier:

```text
Out(edge s -> a) = squares containing that edge
Out(edge s -> b) = squares containing that edge
```

These coface frontiers are what later dimensions use.

## Example: Cubes From Squares

A `3`-cube based at `s` has three lower square faces through `s`.

Call them, informally:

```text
AB-square
AC-square
BC-square
```

They must agree pairwise on their shared initial edges:

```text
AB and AC share A-edge
AB and BC share B-edge
AC and BC share C-edge
```

Instead of recomputing those edge overlaps from the square records, use:

```text
AB in Out(A-edge)
AC in Out(A-edge)

AB in Out(B-edge)
BC in Out(B-edge)

AC in Out(C-edge)
BC in Out(C-edge)
```

The lower-shell check becomes a small pattern of membership checks.

Then the opposite terminal corner is found by finishing the upper side. In a
pure graph-recognition version, this again resembles an intersection of
outgoing targets from the codimension-one top vertices of the lower shell.

## The Dual In Sets

The conversation then introduced a dual structure.

If:

```text
Out(kappa)
```

records higher cubes in which `kappa` appears as a lower/source-side face, then
there should also be:

```text
In(kappa)
```

recording higher cubes in which `kappa` appears as an upper/target-side face.

This is only a first notation. A full cubical implementation may need
coordinate-aware incidence:

```text
Cofaces(kappa, axis, side)
```

where:

```text
side = 0  means the face at coordinate axis fixed to 0
side = 1  means the face at coordinate axis fixed to 1
```

In discussion shorthand:

```text
Out = lower/source-side cofaces
In  = upper/target-side cofaces
```

## Finishing On The Other Side

The "finish on the other side" idea is that a higher cube can be assembled by
matching lower and upper cubical pieces along seams.

For a square, one can think of:

```text
bottom edge
top edge
left seam edge
right seam edge
```

For a cube, one can think of:

```text
lower/source square
upper/target square
side square seams connecting them
```

More generally, a `(k+1)`-cube has two opposite `k`-faces in each coordinate
direction:

```text
axis i fixed to 0
axis i fixed to 1
```

The design intuition is:

```text
cubes are assembled by matching compatible In/Out incidence data along seams
```

rather than by free enumeration of all vertices of the Boolean lattice.

## Seam Records

This suggests introducing seam or incidence records.

A minimal incidence record might store:

```text
face_cube_id
coface_cube_id
axis
side
```

where:

```text
side = 0 or 1
```

If coordinate axes are not yet stable or canonical, the record might instead
store:

```text
face_cube_id
coface_cube_id
face_address
overlap_signature
```

The point is not yet the exact schema. The point is to avoid recomputing:

```text
is this lower cube a face of that higher cube?
```

and to make the search use already-recorded incidence.

## Possible Data Structures

### Cube Record

A cubical record may need:

```text
id
dimension
initial_vertex
vertices_by_mask
edge_witnesses_by_cover
axis_order_or_direction_labels
faces_by_address
lower_face_ids
upper_face_ids
projection_data
degeneracy_data
```

Open question:

```text
Should axis order be part of identity, or should cubes be canonicalized modulo
coordinate permutation?
```

### Incidence Record

An incidence or seam record may need:

```text
id
face_cube_id
coface_cube_id
coface_dimension
axis_or_face_address
side
shared_vertices_signature
shared_edges_signature
```

This record is the "mark in the sand" that a face relation has already been
witnessed.

### Coface Indexes

Useful indexes may include:

```text
out_cofaces[face_cube_id]
in_cofaces[face_cube_id]
cofaces_by_face_address[(face_cube_id, axis, side)]
cofaces_by_base_dimension[(base_vertex, dimension)]
```

If the design keeps `Cube^k(s)` as the primary public notation, the internal
indexes can still be keyed by cube id.

## Relationship To Young-Tableaux/Partition Tricks

The possible connection to the `state_collapser` Young-tableaux trick is that
cube construction has many compatible coordinate-growth orders.

Products such as:

```text
(Delta^1)^n
```

have simplicial shadows indexed by monotone chains through the Boolean lattice.
Those chains correspond to orders of coordinate advancement.

Possible uses:

- keep a canonical coordinate order to avoid duplicate incidence records;
- store chain/tableaux shadows as auxiliary readouts;
- use tableaux-style indexing to organize partial Boolean-lattice assignments;
- triangulate cubical records only as a compatibility view, not as the primary
  cubical identity.

Current caution:

```text
Do not erase the cubical address too early.
```

The cubical object is not merely a simplex. The simplicial structure of
`(Delta^1)^n` is useful, but the package should not accidentally require
primitive graph edges for every simplicial diagonal if the intended cubical
object only requires interval-direction edges.

## Tower And Fiber Principle

The same high-level speed-up principle from simplex search should remain.

Do not:

```text
generate arbitrary upstairs cubical diagrams and filter by projection
```

Instead:

```text
search upstairs only inside fibers indexed by valid downstairs cubical
objects, faces, seams, or shells
```

For a downstairs square, upstairs search should be constrained by the fibers of
that square's corners and edges.

For a downstairs cube, upstairs search should be constrained by the fibers of
that cube's faces and seams.

The precise fiber key may differ from the simplex mode:

```text
simplex mode:
    known downstairs simplex + final edge

cubical mode:
    known downstairs cube/shell + face/seam incidence
```

## Recognition Versus Completion

This document has mostly described graph-recognition language:

```text
find cubical arrangements already present in the directed graph
```

The mode may later support formal completion:

```text
add commutativity cells or fillers when a boundary exists
```

That is a separate semantic decision.

Before implementation, decide whether the first cubical mode is:

- recognition-only;
- completion/filler-adding;
- or recognition first, completion later.

## Current Working Picture

The current best shorthand is:

```text
Cube^k(s):
    k-cubes with initial vertex s

Out(kappa):
    higher cubes containing kappa as a lower/source-side face

In(kappa):
    higher cubes containing kappa as an upper/target-side face

Seam/incidence records:
    cached witnesses that one cube is a specified face of another

Higher cube search:
    structured joins over In/Out/seam incidence, followed by any remaining
    graph frontier intersections needed to finish the opposite side
```

This is the cubical analogue of the simplex cached-frontier idea, adapted to
Boolean-lattice boundaries instead of chain boundaries.

## Open Questions For Project Owner

1. Should cubes be ordered by coordinate directions, or identified up to
   coordinate permutation?
2. Does a `k`-cube in this first mode require only the `1`-skeleton edges, or
   also require lower cubical faces as explicit records?
3. Should `Out(kappa)` mean all cofaces, or only cofaces where `kappa` is a
   lower/source-side face?
4. Should `In(kappa)` be primitive, or computed by filtering incidence records?
5. What exactly is a seam: a shared face, a pair of matched faces, or an
   incidence record between a face and coface?
6. Is the first cubical mode recognition-only?
7. How should degenerate cubical directions be represented?
8. What is the downstairs object that indexes upstairs search: a full cube, a
   lower shell, a seam, or all of these at different stages?
