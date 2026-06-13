# Malik Work Progeny In Jet Simplex Search

## 0. Purpose

This document records, for the present `jet_simplex_search` investigation, the
lineage from Abdullah Naeem Malik's work into the package now being built.

The goal is not to summarize all of Malik's thesis. The goal is narrower:
explain which ideas in this repository are descendants of Malik's thesis,
portfolio code, and research program; which ideas are only adjacent; and which
engineering choices in this package are new refinements made for release.

Primary source assessed:

- Abdullah Naeem Malik, *Simplicial methods in graph machine learning*,
  PhD thesis, 2024. Local PDF assessed at
  `/Users/foster/Downloads/mythesis.pdf`.

Related Malik portfolio sources assessed:

- [Find all 2-simplices](https://abdullahnaeemmalik.github.io/portfolio/Find%20all%202-simplices/)
- [Simplicial Finder](https://abdullahnaeemmalik.github.io/portfolio/simplicial_finder/)
- [Finding Simplicial Sets within a graph by using successive quotients](https://abdullahnaeemmalik.github.io/portfolio/Finding%20Simplicial%20Sets%20within%20a%20graph%20by%20using%20successive%20quotients/)
- [Left Kan Extension](https://abdullahnaeemmalik.github.io/portfolio/Left%20Kan%20Extension/)
- [Constructing a Simplicial Set](https://abdullahnaeemmalik.github.io/portfolio/maximal_simplicial_set/)
- [Finding simplices with adjacency matrices](https://abdullahnaeemmalik.github.io/portfolio/simplices-via-adj/)
- [CinchNET](https://abdullahnaeemmalik.github.io/portfolio/bnsnn/)
- [PseudoTop Vertex Neural Network](https://abdullahnaeemmalik.github.io/portfolio/ptvnn/)
- [Publications](https://abdullahnaeemmalik.github.io/publications/)
- [Talks](https://abdullahnaeemmalik.github.io/talks/)
- [CV](https://abdullahnaeemmalik.github.io/cv/)

Related package work in the same broader ecosystem:

- [`HGraphML`](https://github.com/TYLERSFOSTER/HGraphML), a separate package
  beginning the quotient-tower-backed graph message-passing component.

Working claim:

`jet_simplex_search` is a small, release-oriented descendant of Malik's graph
to simplicial-set program. It is especially descended from four strands:

1. treating directed graphs as 1-dimensional presentations of simplicial data;
2. identifying standard simplices in directed graphs by adjacency/frontier
   constraints;
3. using quotient towers to make simplex search happen over smaller graphs and
   then lift results through fibers;
4. preserving degenerate simplices as first-class dimension-preserving records.

The present package does not attempt to implement the whole thesis. It is not a
GNN package, not CinchNET, not PTVNN, and not a full Kan-extension engine. It is
a focused search package: given graph data, a dimension bound, and optionally a
static quotient tower from `state_collapser`, it enumerates and lifts simplices
with traceable witnesses. The first package-level beginning of the
message-passing component lives instead in
[`HGraphML`](https://github.com/TYLERSFOSTER/HGraphML), which uses
`state_collapser` quotient towers to run graph message passing on coarse tiers
and lift messages back to fine graph data.

## 1. Executive Lineage

Malik's thesis asks how directed graphs can be treated as the visible
1-skeleton of richer simplicial-set structure. The thesis develops several
ways of passing from graph data to higher-order relations:

- Kan-extension viewpoints on graphs as 1-truncated simplicial data;
- direct algorithms for finding standard simplices in directed graphs;
- adjacency-matrix and Boolean-matrix acceleration for low dimensions;
- inductive algorithms that build higher simplices from lower simplices;
- hierarchical quotient search, where a large graph is compressed, simplices are
  found downstairs, and candidate lifts are checked upstairs;
- neural architectures that consume the resulting higher-order structures.

`jet_simplex_search` sits in the middle of that program. It takes the simplex
search and quotient-lift parts seriously enough to turn them into a small
package with:

- explicit graph normalization;
- formal identity edges for degenerate simplices;
- direct sparse enumeration at a bottom tier;
- static quotient towers realized through `state_collapser`;
- fiber-addressed lifting from downstairs simplices to upstairs simplices;
- H-to-G skeletonization and H-lift accounting for loop/parallel-edge input;
- JSON/JSONL artifacts and tests aimed at public release.

The most important conceptual inheritance is this:

Malik's hierarchical search does not merely compress a graph as a heuristic
preprocessing step. It changes where search occurs. Higher-dimensional
candidates upstairs should be considered only when there is a dimension-matched
simplex downstairs. The present repo sharpens that into a package invariant:

Search at tier `r` is indexed by simplex records already present at tier
`r + 1`. The downstairs simplex is not an after-the-fact validation check. It is
the address of the upstairs search.

That is the core speed-up idea now embodied in the package.

## 2. Source Corpus

### 2.1 Thesis Structure

The thesis metadata identifies:

- author: Abdullah Naeem Malik;
- title: *Simplicial methods in graph machine learning*;
- date: 2024;
- length: 121 PDF pages.

The table of contents is directly relevant to this repository in the following
sections:

- Chapter 2, "Simplicial Sets and Graphs", beginning around thesis PDF page 24;
- Chapter 4, "Algorithms for Identifying Standard Simplices in Graphs",
  beginning around thesis PDF page 51;
- Chapter 6, "Hierarchial Simplicial Search", beginning around thesis PDF
  page 83;
- Chapter 7, "Message Propagation Along Simplices", beginning around thesis PDF
  page 95;
- Chapter 8, "Conclusions and Future work", beginning around thesis PDF
  page 109.

The repository is most directly descended from Chapters 2, 4, and 6.
Chapter 7 is downstream motivation. Chapter 8 confirms that hierarchical search
and neural use of simplicial data are part of one research trajectory, but the
present package implements only the search side.

### 2.2 Portfolio Structure

Malik's portfolio contains a public development trail that matches the thesis.
The most important project for this repo is the quotient-tower project:

- "Finding Simplicial Sets within a graph by using successive quotients".

The next most important sources are:

- "Find all 2-simplices";
- "Finding simplices with adjacency matrices";
- "Left Kan Extension";
- "Constructing a Simplicial Set".

The neural-network projects, especially PTVNN and CinchNET, are not direct code
ancestors of the package. They are downstream uses for the kind of higher-order
structure this package is meant to expose.

## 3. Lineage Table

| Malik idea | Thesis or portfolio locus | Present repo realization | Difference in this package |
| --- | --- | --- | --- |
| Directed graph as 1-dimensional simplicial data | Thesis Chapter 2 | `GraphInput`, normalization, direct simplex records | The package is operational and sparse-search oriented, not a category-theory framework |
| Degenerate loops as formal identity structure | Thesis Chapter 2; Left Kan portfolio code | formal identity edges in the simplex engine; degenerate records preserved | The input graph is kept conceptually separate from formal degeneracy identities |
| Standard simplex in a graph | Thesis Chapters 2 and 4 | ordered vertex tuples with face-edge witnesses | The package stores traceable records rather than only accepting/rejecting tuples |
| Right-Kan-like completion by finding all possible standard simplices | Thesis Chapters 2 and 4 | direct enumeration at the bottom tier | This is bounded by user-supplied `k` and implemented as finite search |
| Left-Kan-like degenerate completion | Thesis Chapter 2; Left Kan portfolio | formal identities generate degenerate simplices | Full Kan machinery is future work |
| Inductive construction from lower simplices | Thesis Chapter 4, inductive connecting algorithms | cached frontier recurrence and dimension-by-dimension enumeration | The repo includes degenerates and ordered records as first-class outputs |
| Adjacency-matrix simplex search | Thesis Chapter 4; adjacency portfolio | conceptual ancestor for frontier intersections | The package does not use matrix powers as its main kernel |
| Quotient hierarchy | Thesis Chapter 6; successive quotients portfolio | `state_collapser` tower adapter and clean tower realization | The repo makes the tower static and separates realization from lifting |
| Lift simplices through quotient fibers | Thesis Chapter 6 | `lift.py`, `clean_tower.py`, projection ids | The repo enforces dimension-matched downstairs indexing |
| Degenerate downstairs simplex with nondegenerate upstairs lift | Thesis Chapter 6, Proposition 5 and algorithm discussion | projection-preserving lift records and tests | The package treats this as central, not an edge case |
| SQL/database storage of quotient hierarchy | successive quotients portfolio; thesis Chapter 6 experiments | artifacts and in-memory package records | The package avoids SQL for the initial library release |
| Simplex verification | Thesis Chapter 6, Algorithm 13 | face-edge witnesses and witness consistency tests | The repo aims for auditable records, not just counts |
| HNSW analogy for coarse-to-fine search | thesis Chapter 6; quotient portfolio | static bottom-up lift through tower tiers | The package does not implement dynamic nearest-neighbor search |
| PTVNN | thesis Chapter 5; PTVNN portfolio | not implemented | Downstream consumer direction only |
| CinchNET / adjacency graph of a simplicial set | thesis Chapter 7; CinchNET portfolio | not implemented in this repo, but the beginning of the graph message-passing branch is in [`HGraphML`](https://github.com/TYLERSFOSTER/HGraphML) | This package is preprocessing/search infrastructure; HGraphML is the separate message-passing bridge |
| Collapse-ratio diagnostics and edge-length concerns | thesis Chapter 6 experiments and portfolio notes | partial diagnostics and smoke scripts | More performance diagnostics remain release-prep work |

## 3.1 Thesis Chapter Assessment For This Investigation

This section records how each relevant thesis chapter should be read for the
present repo. It deliberately ignores parts of the thesis that are not part of
the package lineage.

### 3.1.1 Abstract And Introduction

The abstract frames the thesis around data structures that identify higher
relationships in binary relational data. For this repo, that means:

- graph edges are binary observations;
- higher simplices are higher-order relational structure latent in those edges;
- algorithms must expose those higher structures before downstream learning can
  use them.

The introduction's contribution list matters because it places simplex
identification and graph neural networks in one program, but not in one
implementation layer. The current package belongs to the identification layer.
It prepares the higher-order structure. It does not train neural networks.

Assessment for `jet_simplex_search`:

- direct ancestor: algorithms to identify higher-order relations;
- adjacent motivation: graph machine learning;
- not in scope: neural architecture training.

### 3.1.2 Chapter 2: Simplicial Sets And Graphs

Chapter 2 is the conceptual root. It says a directed graph can be treated as
low-dimensional simplicial data, and then extended by simplicial operations.

Repo descendants:

- `GraphInput` is the package-level input shape for graph data;
- formal identity edges are the operational version of degenerate 1-simplices;
- simplex degree is arity minus one;
- degenerate higher simplices are valid outputs, not noise;
- bounded search to degree `k` is a finite operational slice of a completion
  process.

Important distinction:

The thesis can speak globally about Kan extensions and simplicial sets. The
package has to answer a finite API question:

```text
given graph H and integer k, which simplex records through degree k are emitted?
```

The package therefore turns the chapter's concepts into executable invariants:

- every simplex record has a degree;
- every simplex record has an ordered vertex address;
- every nonzero simplex record has edge witnesses for its faces;
- degenerate records keep their repeated vertex addresses.

### 3.1.3 Chapter 4: Algorithms For Identifying Standard Simplices

Chapter 4 is the direct-search root. It contains the clearest ancestor of the
bottom-tier enumeration code.

Repo descendants:

- sparse outgoing-frontier intersections;
- inductive construction from degree `m` to degree `m + 1`;
- special importance of 2-simplex search as the first nontrivial case;
- tests and smoke scripts focused on small dimensions.

The package changes the implementation kernel. Instead of making adjacency
matrix powers the central data structure, it uses:

```text
frontier(prefix) intersection adjacency(last vertex)
```

This keeps the same mathematical constraint while making the implementation
more appropriate for sparse graphs.

Important distinction:

Some thesis algorithms are described without degenerates. The repo cannot make
that simplification because quotient projection can turn an upstairs
nondegenerate simplex into a downstairs degenerate simplex.

### 3.1.4 Chapter 6: Hierarchial Simplicial Search

Chapter 6 is the tower-search root. It is the strongest direct ancestor of the
present package.

Repo descendants:

- quotient towers;
- search on a compressed bottom tier;
- lift through preimages/fibers;
- degenerate downstairs images of nondegenerate upstairs simplices;
- verification of lifted candidates;
- diagnostics around tier size and lift behavior.

The key repo refinement is that the tower is static and search is
fiber-addressed. A downstairs simplex record is not merely used to validate an
upstairs candidate after broad enumeration. It determines where the upstairs
search is allowed to happen.

This turns the chapter's hierarchical intuition into the package invariant:

```text
no downstairs simplex record, no upstairs lift search over that address
```

### 3.1.5 Chapter 7: Message Propagation Along Simplices

Chapter 7 is downstream. It introduces the idea of building graph structures
from simplicial sets so neural networks can propagate along simplex-related
maps.

Repo descendants:

- artifact design should preserve enough structure for future adjacency-graph
  consumers;
- face and degeneracy information should stay explicit rather than disappearing
  into counts;
- the beginning of the broader message-passing component is not in this repo
  but in [`HGraphML`](https://github.com/TYLERSFOSTER/HGraphML), where the
  first package surfaces run graph message passing over `state_collapser`
  quotient towers and lift coarse messages back along edge fibers.

Not implemented in `jet_simplex_search`:

- CinchNET;
- neural message passing;
- simplex adjacency graph export as a first-class API.

Implemented elsewhere in first form:

- `HGraphML` has the first quotient-tower-backed graph message-passing bridge:
  graph data, edge-aligned message models, coarse-tier message computation, and
  learned or rule-based lifts back to fine-edge messages.

### 3.1.6 Chapter 8: Conclusions And Future Work

The conclusion confirms the three algorithmic branches relevant here:

- inductive search;
- adjacency-matrix search;
- hierarchical quotient search.

It also frames hierarchical quotient search as a way to reduce the cost of
finding higher simplices by using smaller graphs and lifting back upward.

Repo descendants:

- the package chooses the hierarchical branch as its most important release
  differentiator;
- direct search remains as the bottom-tier kernel;
- quotient-lift search is packaged as a reusable library API.

Future directions inherited from the conclusion:

- better Kan replacement modes;
- richer categorical settings;
- downstream neural models;
- parallel and local processing.

## 4. Conceptual Foundation: Graphs As Simplicial Presentations

Chapter 2 of the thesis supplies the conceptual foundation for the present
repo. The thesis treats a directed graph as a functor out of a truncated simplex
category: vertices are level 0 data, arrows are level 1 data, and higher
simplices are absent until some completion process supplies them.

The package inherits that exact stance. A directed graph is not merely an object
whose cliques are being counted. It is a visible 1-skeleton from which one can
ask for higher standard simplex data.

The thesis distinguishes several completions or views:

- the graph itself as low-dimensional data;
- a left-Kan-style completion that freely supplies degenerate higher simplices;
- a right-Kan-style completion that supplies every higher simplex forced by
  compatible boundary data;
- iterative attachment operations such as `conn_k(G)`, which add higher
  simplices along detected boundaries.

The present repo implements a bounded, finite, search-oriented slice of this
picture. Given a dimension bound `k`, it enumerates standard simplices up to
dimension `k`. Degenerate simplices are included by allowing formal identity
steps. Nondegenerate higher simplices are included when the relevant directed
face constraints hold.

The repo therefore makes the thesis foundation executable in this narrower
sense:

- vertices become 0-simplex records;
- graph edges and formal identities become 1-simplex records;
- higher simplex records are generated inductively;
- every generated simplex carries enough address and witness data to explain why
  it exists.

## 5. Degeneracy Lineage

Degeneracy is one of the most important places where the package is directly
descended from Malik's work but makes a sharper implementation decision.

In the thesis, degenerate simplices arise naturally when a graph is viewed
simplicially. A vertex has an identity edge. A string such as:

```text
s -> s -> s -> t
```

is not just the edge `s -> t`. It is a higher-dimensional degenerate simplex
address. This matters especially under quotient maps, because a nondegenerate
upstairs simplex can project to a degenerate downstairs simplex after several
distinct upstairs vertices collapse to one downstairs vertex.

The package preserves this principle in two ways.

First, formal identities are part of the simplex engine. The package does not
need to rely on user-supplied loops to discover degenerate simplices. It can
normalize graph input and still admit the identity option at every vertex when
building simplices.

Second, a degenerate simplex is not collapsed to its nondegenerate spine in the
record system. The address has dimension. For example:

```text
(s, s, t)
```

is a 2-simplex address even if its nondegenerate support resembles an edge.

That decision is not cosmetic. It is necessary for quotient lifting. If an
upstairs triangle projects to `(S, S, T)`, then a search engine that reduces
`(S, S, T)` to `(S, T)` has lost the dimension-preserving address over which the
upstairs simplex should be lifted.

This is exactly the kind of issue Malik's quotient-hierarchy discussion exposes.
The package turns it into an implementation invariant:

Degenerate simplices are first-class simplex records. Their frontiers may be
set-theoretically redundant, but their addresses are not redundant.

## 6. Direct Search Lineage

Chapter 4 of the thesis develops algorithms for identifying standard simplices
in graphs. The portfolio project "Find all 2-simplices" gives an early
computational instance of the same concern.

The adjacency-matrix approach for 2-simplices is:

- use the adjacency matrix `A`;
- compute path information such as `A^2`;
- compare two-step paths with direct edges;
- use intersections of in-neighbors and out-neighbors to identify compatible
  triangular data;
- use Boolean variants to avoid unnecessary arithmetic growth.

For higher `k`, the thesis considers inductive and matrix-powered approaches.
These show two durable ideas:

1. a higher simplex can be built from a lower simplex plus one more compatible
   vertex;
2. the compatibility check is an intersection problem over outgoing adjacency
   sets.

The present package keeps those ideas but changes the kernel. It does not make
matrix powers the main implementation strategy. Instead, it uses sparse
frontiers.

For a simplex:

```text
sigma = (s0, ..., sm)
```

the possible next targets are:

```text
Out(sigma) = Out(s0) intersection ... intersection Out(sm)
```

The user and Codex refined this further during the design discussion:

```text
Out(sigma) = Out(partial_m(sigma)) intersection Out(tgt(sigma))
```

where:

```text
partial_m(sigma) = (s0, ..., s_{m-1})
tgt(sigma)       = sm
```

This makes `Out(sigma)` an inductive payload carried by the simplex record. A
new simplex can compute its frontier from the cached frontier of its prefix and
the outgoing set of its last vertex. That is the sparse, package-level
descendant of Malik's adjacency/intersection algorithms.

The degree-bucket version is:

```text
Out^0(s) = {s}
Out^1(s) = {id_s} union Out(s)
Out^(m+1)(s) = union over sigma in Out^m(s) of extensions of sigma
```

Interpreted operationally, each `Out(sigma)` is a set of one-step extensions, or
a target frontier from which one-step extensions are constructed.

This is the direct-search core of the present package.

## 7. What The Package Changes From The Direct Algorithms

The thesis direct algorithms are research prototypes and mathematical
algorithms. The package changes them in several release-oriented ways.

### 7.1 Sparse frontiers instead of matrix powers

The package favors adjacency sets and cached intersections. That better matches
the intended input regime: sparse directed graphs.

The matrix approach is still an ancestor. It explains why common-neighbor and
path/direct-edge intersections are the right primitives. But the package's
actual engine is closer to:

```text
for each valid simplex sigma:
    for each target in cached_frontier(sigma):
        emit sigma extended by target
```

### 7.2 Records instead of bare tuples

The package needs more than counts. A simplex record carries:

- dimension;
- vertices;
- projection information when it is lifted;
- face-edge witnesses;
- degeneracy information or identity-edge participation;
- frontier or extension information.

This record orientation is important for release because users need artifacts
that can be checked and inspected.

### 7.3 Degenerates included by default

Some thesis algorithms explicitly ignore degenerate simplices for simplicity.
The package cannot do that because quotient lifting depends on degenerate
downstairs addresses.

The package therefore includes degenerates up to the requested dimension bound.
Since the bound is finite, the degenerate closure remains finite.

## 8. Quotient Tower Lineage

The strongest direct ancestor of `jet_simplex_search` is Malik's hierarchical
simplex search in thesis Chapter 6 and the portfolio project "Finding
Simplicial Sets within a graph by using successive quotients".

The thesis observes that direct search can explode because there are many
possible edge orderings and many possible higher simplex boundaries. The
hierarchical strategy compresses the graph by identifying vertices, searches a
smaller graph, and then lifts results through quotient fibers.

The portfolio code and thesis algorithms contain several pieces that map
directly into the present package:

- choose edges or vertex relations to collapse;
- build successive quotient graphs;
- remember preimages and equivalence classes;
- find simplices on a smaller quotient graph;
- lift each quotient simplex to candidate upstairs simplices;
- verify the required upstairs edge data;
- repeat through the hierarchy.

The package keeps this structure but gives it a more static and typed shape.

Current package structure:

- `clean_tower.py` realizes a clean quotient tower from `state_collapser`;
- `search.py` performs bottom-tier direct enumeration;
- `lift.py` lifts through the tower using downstairs simplex records;
- `skeleton.py` handles H-to-G skeletonization for loop/parallel-edge input;
- `h_lift.py` computes compressed H-lift counts;
- `artifacts.py` writes auditable search artifacts.

The crucial difference is that the package treats the tower as static. The
tower is built first. Search does not dynamically rewrite the tower while
enumeration is happening.

The package pipeline is:

1. normalize input graph data;
2. realize or accept a static quotient tower;
3. choose the bottommost nondegenerate tier;
4. enumerate all simplices up to `k` at that bottom tier;
5. lift dimension-by-dimension through each higher tier, indexed by the
   downstairs simplex records.

This is the thesis hierarchy made into a deterministic package pipeline.

## 9. Fiber-Addressed Search

The central speed-up in the present package is not merely "check a quotient".
It is fiber-addressed generation.

Suppose a downstairs `(m+1)`-simplex is:

```text
tau = (c0, ..., cm, c_{m+1})
```

Its prefix is:

```text
partial(tau) = (c0, ..., cm)
```

and its last downstairs edge is:

```text
alpha : cm -> c_{m+1}
```

At the tier above, the package does not enumerate every possible extension of
every upstairs `m`-simplex and then ask whether it happens to project to `tau`.
Instead it searches only inside the fiber over `tau`.

Operationally:

```text
for each upstairs m-simplex sigma over partial(tau):
    consider only upstairs edges beta over alpha
    require source(beta) = tgt(sigma)
    require target(beta) in Out(sigma)
    emit sigma extended by target(beta)
```

That is the decisive package-level refinement of Malik's quotient lifting.

The downstairs simplex is the index of the search. The last edge of the
downstairs simplex determines which upstairs edge fiber is relevant. The
upstairs frontier determines which of those fiber targets actually extend the
simplex.

This avoids searching for upstairs higher-dimensional structure in places where
there is no downstairs simplex of the same dimension.

This also answers the important boundary case:

If downstairs has only a boundary-like pattern and no 2-simplex record, then
the package should not search for an upstairs 2-simplex over that missing
downstairs interior. The lifting code should have no downstairs 2-simplex key
to index. Therefore no corresponding upstairs 2-simplex search occurs.

That is the small-object style behavior currently intended. It is different
from a Kan-filling version, where missing horns or boundaries might become
prompts to add fillers.

## 10. Degenerate Downstairs, Nondegenerate Upstairs

One of the most important thesis-to-package inheritances is the fact that
quotient maps can send nondegenerate upstairs simplices to degenerate downstairs
simplices.

Example:

```text
upstairs:   a -> b -> c -> d
projection: a,b,c map to S; d maps to T
downstairs: S -> S -> S -> T
```

The downstairs simplex is degenerate. The upstairs simplex may be nondegenerate.
The lifting system must preserve the full downstairs address:

```text
(S, S, S, T)
```

and not reduce it to:

```text
(S, T)
```

This is why the repo includes degenerate simplices as ordinary simplex records.
They are not noise. They are the correct quotient addresses for possible
nondegenerate lifts.

This point appears in the thesis hierarchical search discussion, especially
around the proposition that projection through a quotient can create degenerate
simplices downstairs. It also appears in the portfolio quotient code, where
preimages and degenerate quotient behavior are part of the lifting story.

The present package makes this a central correctness rule:

Dimension is preserved across lifting. Degeneracy is allowed in the projection.

## 11. H-To-G Skeletonization As A Package Refinement

The current repository has an H-to-G skeletonization layer that is not merely a
direct copy of the thesis. It is a package-specific refinement for practical
graph input.

The thesis and portfolio code mostly discuss directed graphs and quotient
graphs at the level of vertices and arrows. The present package must also handle
input graphs with:

- loops;
- parallel edges;
- labels or payloads;
- multiple edge witnesses between the same endpoints;
- compressed skeletons used for search.

The package therefore distinguishes:

- `H`, the original graph-like input, possibly with loops and parallel edges;
- `G`, a cleaned or skeletonized graph used for simplex search;
- fibers from `H` data over `G` edges and vertices;
- H-lift counts or compressed lift summaries.

This is conceptually compatible with Malik's quotient-fiber program, but it is a
new engineering layer. It exists because a public package needs to explain how
results over a clean search skeleton correspond back to original input data.

The H-to-G layer is also where witness correctness becomes especially important.
If multiple H edges collapse to the same G edge, or multiple G edges sit over a
downstairs edge, the package must not merely report that some endpoints match.
It must preserve which edge witnesses make the simplex valid.

This concern motivated recent refactors and code-review revisions around:

- source-sensitive edge fibers;
- witness projection consistency;
- not mixing edge ids that share endpoints but project differently.

That level of traceability is an engineering strengthening of Malik's verifier
idea.

## 12. Relation To `state_collapser`

Malik's hierarchical search needs a source of quotient towers. The present
package delegates that role to `state_collapser`.

In the present repo, `state_collapser` is not the simplex search engine. It is
the tower-building dependency. `jet_simplex_search` uses it to obtain or realize
the static tower over which simplex search occurs.

The package then owns:

- graph normalization for search;
- direct simplex enumeration;
- degenerate identity handling;
- lift-index construction;
- witness preservation;
- search artifacts;
- H-to-G lift summaries.

This separation is important. Malik's thesis combines the conceptual
hierarchical search story with prototype graph/database machinery. The present
package splits concerns:

```text
state_collapser        builds quotient structure
jet_simplex_search     enumerates and lifts simplex structure
```

That split makes the release surface smaller and easier to test.

## 13. Artifact Lineage

The thesis quotient search and portfolio code use database-like storage to
remember quotient layers, preimages, and verification data. The current package
turns that need into simple release artifacts.

The current artifact direction is:

- machine-readable JSON summaries;
- JSONL simplex streams;
- diagnostics about tier counts and lifting;
- witness records sufficient to audit emitted simplices.

This is a practical descendant of Malik's SQL-backed quotient hierarchy, but
with a different public-library bias:

- no required database server;
- no hidden notebook state;
- deterministic package APIs;
- reproducible smoke scripts and tests.

The artifact requirement is not incidental. Since the package's claim is not
only "we counted something" but "we found these simplices by this quotient and
these witnesses", the artifact layer is part of the mathematical evidence.

### 13.1 Current Repo File Provenance

This section maps current package files to their Malik-lineage roles. It is a
snapshot of the repo during this investigation.

| Repo file | Malik-lineage role | Present responsibility |
| --- | --- | --- |
| `src/jet_simplex_search/graph.py` | graph as 1-skeleton input | defines input vertices, input edges, graph validation |
| `src/jet_simplex_search/normalize.py` | formal reflexive graph used for simplicial enumeration | turns package graph input into normalized search graphs with adjacency and edge lookup |
| `src/jet_simplex_search/frontier.py` | adjacency/common-neighbor simplex criteria | implements sparse frontier intersection and face witness lookup |
| `src/jet_simplex_search/search.py` | Chapter 4 direct and inductive simplex search | enumerates zero-simplices, extends simplex records, runs bottom-tier and tower search |
| `src/jet_simplex_search/records.py` | simplices as first-class auditable data | stores simplex addresses, witnesses, fibers, degeneracy flags, search results |
| `src/jet_simplex_search/lift.py` | Chapter 6 quotient lifting | lifts simplex records one tier using downstairs simplex fibers and last-edge fibers |
| `src/jet_simplex_search/tower_adapter.py` | abstraction boundary for quotient hierarchy | defines the tower protocol and adapter utilities |
| `src/jet_simplex_search/clean_tower.py` | static quotient tower realization | builds clean quotient tiers using `state_collapser`-compatible contraction structure |
| `src/jet_simplex_search/skeleton.py` | package-specific H-to-G refinement | collapses original loops/parallel H edges into a clean skeleton G with fibers |
| `src/jet_simplex_search/h_lift.py` | package-specific lift accounting over original H | computes compressed original-edge lift counts over tier-0 skeleton simplices |
| `src/jet_simplex_search/diagnostics.py` | thesis-style runtime/count analysis made public | packages tier and simplex counts for artifacts |
| `src/jet_simplex_search/artifacts.py` | replacement for notebook/SQL evidence trails | writes machine-readable search outputs |
| `src/jet_simplex_search/api.py` | release-facing package surface | exposes the small, bounded search API |

The most Malik-direct files are:

- `search.py`;
- `frontier.py`;
- `lift.py`;
- `clean_tower.py`;
- `tower_adapter.py`.

The most package-specific refinements are:

- `skeleton.py`;
- `h_lift.py`;
- `artifacts.py`;
- `api.py`.

### 13.2 Current Test Provenance

The test suite also reflects the Malik lineage. Some tests are ordinary package
tests, but several are specifically defending thesis-derived invariants.

| Test area | Malik-lineage invariant being protected |
| --- | --- |
| bottom-tier enumeration | direct standard simplex search through bounded degree |
| directed flag semantics | standard simplex equals all required directed faces |
| frontier tests | common-neighbor/intersection criterion is implemented sparsely |
| fiber lift tests | quotient lifting is indexed by downstairs simplex records |
| witness consistency tests | lifted records must have truthful edge witnesses |
| clean tower tests | quotient hierarchy can be realized as clean search tiers |
| H-lift tests | original H edge multiplicity is not lost behind skeleton G |
| README quickstart tests | release examples remain executable |

The most important test idea inherited from Malik's hierarchy is:

```text
if a downstairs simplex is absent, the upstairs lift search over that simplex
address must not run
```

That is the behavioral difference between the current small-object style
package and a future Kan-filling package.

### 13.3 Smoke Script Provenance

The smoke scripts are descendants of Malik's low-dimensional examples and
runtime experiments. They are deliberately small because their purpose is not to
benchmark maximum performance. Their purpose is to make the combinatorics
visible:

- how many degenerate simplices are generated;
- how identity arrows contribute;
- how low-dimensional directed flags behave;
- how counts change under simple graph shapes.

This is the package version of the thesis's early examples and notebook-driven
algorithm checks.

## 14. Portfolio Project Correspondence

### 14.1 Find all 2-simplices

The "Find all 2-simplices" portfolio project anticipates the package's
low-dimensional direct search. The notebook contains object structures for
creating and searching 2-simplices, and it uses adjacency-style data such as
out-neighbors, in-neighbors, and common tensors between squared adjacency and
adjacency.

Present repo descendant:

- direct 2-simplex enumeration;
- sparse intersection logic;
- smoke scripts for low-dimensional counts;
- extension of the same idea beyond dimension 2.

Difference:

- the package includes degenerates as first-class records;
- the package stores witnesses and projections;
- the package is not a notebook prototype.

### 14.2 Finding simplices with adjacency matrices

The adjacency-matrix portfolio project anticipates the direct search kernel. It
uses powers of adjacency and intersections to detect possible higher simplices.

Present repo descendant:

- `Out(sigma)` frontiers are the sparse analogue of common-neighbor matrix
  constraints;
- bottom-tier direct search uses dimension-by-dimension extension;
- the package can terminate naturally when no next-dimensional frontiers emit
  records.

Difference:

- the package does not use adjacency matrix powers as the main algorithm;
- it is optimized for sparse graph data and quotient lifting.

### 14.3 Simplicial Finder

The "Simplicial Finder" portfolio project is part of the same development line:
identify higher simplicial structure already present in directed graph data.

Present repo descendant:

- the package is a focused reusable implementation of this search problem;
- the search output is structured for inspection and release.

Difference:

- the package now includes static towers and H-to-G lift accounting;
- it has a clearer bounded API around `k`.

### 14.4 Successive quotients

The successive-quotients portfolio project is the most direct ancestor. It
contains:

- quotient graph construction;
- preimage tracking;
- lift verification;
- SQL storage;
- a search process inspired by hierarchical navigation;
- experiments on random graphs and transitive tournaments.

Present repo descendant:

- static quotient tower search;
- bottom-tier simplex enumeration;
- tier-by-tier lifting;
- downstairs-degenerate/upstairs-nondegenerate handling;
- fiber-indexed candidate generation;
- diagnostics and smoke scripts.

Difference:

- the package uses `state_collapser` for tower construction;
- the package avoids SQL in the core release path;
- the package makes edge witness identity explicit;
- the package treats the tower as static rather than dynamic.

### 14.5 Left Kan Extension

The Left Kan portfolio code anticipates the future Kan version of this package.
It contains machinery around degeneracy maps, level-up operations, and universal
completion.

Present repo descendant:

- formal identity arrows;
- degenerate simplex generation;
- explicit separation between degenerate completion and nondegenerate search.

Difference:

- the current package is not a full left Kan extension implementation;
- it only generates bounded finite simplex data needed for the search problem.

### 14.6 Constructing a Simplicial Set

The "Constructing a Simplicial Set" project contains functions and files around
standard simplices, degeneracy names, face names, mapping possibilities, and
degeneracy status.

Present repo descendant:

- simplex addresses;
- face-edge witnesses;
- degeneracy-aware records;
- distinction between degenerate and nondegenerate structure.

Difference:

- the package centers graph search and quotient lifting rather than abstract
  simplicial-set construction in isolation.

### 14.7 PTVNN

The PTVNN project is downstream and adjacent. It uses pseudotop or
pseudoterminal vertices as graph-theoretic proxies for higher-order structure.

Present repo relationship:

- conceptual motivation only;
- possible future consumer of simplex-search artifacts;
- not implemented in the package.

### 14.8 CinchNET And HGraphML

CinchNET and the thesis Chapter 7 adjacency-graph construction are downstream
of simplex identification. They ask how to perform message passing along
simplices after a simplicial structure has been built.

Present repo relationship:

- the package can become preprocessing infrastructure for such models;
- artifact design should remain compatible with future simplex adjacency or
  face/degeneracy graph construction;
- no neural model is implemented here.

Broader ecosystem relationship:

- the first concrete package step toward this message-passing branch is
  [`HGraphML`](https://github.com/TYLERSFOSTER/HGraphML);
- `HGraphML` is not yet CinchNET and does not consume this package's simplex
  artifacts as a complete simplicial message-passing pipeline;
- it does establish the adjacent engineering pattern: use `state_collapser`
  quotient towers, run message passing on a coarse graph, and lift messages back
  through fibers to finer graph data;
- that makes `HGraphML` the present beginning of the message-passing component,
  while `jet_simplex_search` remains the simplex-search and quotient-lift
  component.

### 14.9 Conway's Game of Life in reverse

This portfolio project does not materially anticipate the present repo.

It may show Malik's broader interest in inverse search and combinatorial
constraints, but it is not part of the direct simplex-search lineage.

### 14.10 Talks, publications, and CV

The Publications page anchors the thesis as the mature statement of the
research program.

The Talks page reinforces the chronology:

- talks on finding higher structures in graphs;
- talks on combinatorial approaches to simplicial sets;
- talks on infinite simplices;
- talks on PTVNN.

These confirm that the present package is not an isolated implementation idea.
It sits in a sustained Malik research line around higher structures in graph
data.

## 15. What The Present Repo Does Not Yet Implement

The package should not overclaim. The following Malik-derived or Malik-adjacent
ideas are not yet implemented as full package features.

### 15.1 Full Kan replacement

The present package has a small-object style search: it searches over existing
downstairs simplex records and lifts them. It does not yet implement a Kan
replacement engine that freely adds missing fillers.

In particular:

- missing downstairs horns do not trigger automatic upstairs filler search;
- missing downstairs interiors do not become search addresses;
- the current algorithm is conservative and dimension-matched.

A future Kan version should be specified separately.

### 15.2 Full cofibrant or small-object replacement formalism

The present algorithm is inspired by small-object style staged construction,
but it is implemented as bounded finite graph search and quotient lifting.

It does not yet expose a general categorical small-object replacement API.

### 15.3 Neural message passing

The package does not implement PTVNN, CinchNET, or the adjacency graph
`Adj(X)` from Chapter 7.

It may produce input suitable for those later systems.

Important repo-boundary clarification:

- `jet_simplex_search` does not implement neural message passing;
- the first package-level beginning of quotient-tower-backed graph message
  passing is in [`HGraphML`](https://github.com/TYLERSFOSTER/HGraphML);
- `HGraphML` currently works at the graph message-passing level, with coarse
  graph messages and fiber lifts, rather than at the full simplicial
  adjacency-graph/CinchNET level;
- a future integration path could use `jet_simplex_search` artifacts to provide
  simplex records and face/degeneracy structure to an HGraphML-like
  message-passing system.

### 15.4 Matrix kernels

The package does not currently provide an adjacency-matrix backend. The matrix
approach is a historical and conceptual ancestor, not the current kernel.

### 15.5 SQL-backed quotient persistence

The package does not use the SQL database strategy from the successive-quotient
prototype. It uses ordinary Python data structures and artifacts.

### 15.6 Parallel quotient processing

The thesis notes that subgraphs or quotient fibers can in principle be
processed in parallel. The present package does not yet make parallelism a core
feature.

## 16. What The Present Repo Adds

The repo is not merely a transcription of Malik's code. It adds several
engineering and conceptual refinements.

### 16.1 Static tower discipline

The tower is built first. Search happens over a fixed tower. This makes
correctness and testing much simpler.

### 16.2 Fiber-addressed lifting as an invariant

Lifting is organized by downstairs simplex ids. This strengthens the hierarchy
idea into a search invariant.

### 16.3 Source-sensitive edge fibers

The package tracks fibers by downstairs edge and upstairs source. This prevents
the search from scanning irrelevant upstairs edges and prevents witness
confusion when multiple edges share endpoints.

### 16.4 Witness consistency

The package treats edge witnesses as part of the result. Counts alone are not
enough.

### 16.5 H-to-G skeletonization

The package handles original graph data with loops and parallel edges by
separating the original H graph from the clean G skeleton used for search.

### 16.6 Release-oriented tests and smoke scripts

The repo has a growing test and smoke layer that checks:

- degenerate counts;
- missing-downstairs-interior behavior;
- witness projection consistency;
- README examples;
- release metadata.

This is an engineering descendant of the thesis experiments, but with a package
release target.

## 17. Current Package Interpretation Of Malik's Program

For this repo, Malik's program can be read as a sequence:

```text
directed graph
  -> graph as 1-truncated simplicial data
  -> bounded standard-simplex search
  -> quotient hierarchy to reduce search
  -> dimension-preserving lift through fibers
  -> simplicial artifacts for downstream learning or analysis
```

`jet_simplex_search` currently implements the middle part:

```text
graph input
  -> normalized search graph / H-to-G skeleton
  -> static quotient tower
  -> bottom-tier direct simplex enumeration
  -> fiber-addressed lifting
  -> auditable simplex records and artifacts
```

That is the package's rightful scope for an early public release.

## 18. Implications For Future Design

The Malik lineage suggests several future workstreams.

### 18.1 Kan version

A Kan version should be a separate mode, not a quiet mutation of the current
small-object search.

Small-object style current behavior:

```text
search only over existing downstairs simplices
```

Kan-style future behavior:

```text
detect horns or boundaries that demand fillers
add or search for fillers according to the Kan policy
```

This distinction must remain explicit.

### 18.2 Simplicial adjacency graph output

If the package later supports CinchNET-like consumers, it should be able to emit
an adjacency graph of simplex records with face and degeneracy maps.

This would connect directly to thesis Chapter 7. It would also form the natural
bridge to [`HGraphML`](https://github.com/TYLERSFOSTER/HGraphML), which already
begins the separate message-passing side by using `state_collapser` quotient
towers, coarse graph messages, and fiber lifts. In that future integration,
`jet_simplex_search` would supply the simplex-indexed structure, while HGraphML
or an HGraphML-descended package would supply the trainable message-passing
machinery.

### 18.3 Performance kernels

The thesis and portfolio compare direct and hierarchical search. The package
should eventually include:

- sparse path benchmarks;
- transitive tournament benchmarks;
- quotient-tower benchmarks;
- fiber-query counts;
- edge-scan counts;
- artifact-size diagnostics.

### 18.4 Better tower diagnostics

Malik's quotient work discusses collapse ratio and the effect of quotient
quality. The package should expose enough diagnostics to explain when the tower
helps and when it does not.

Useful diagnostics include:

- tier vertex counts;
- tier edge counts;
- simplex counts by tier and dimension;
- edge-fiber size distribution;
- maximum edge-fiber size;
- lift expansion ratios;
- degenerate versus nondegenerate counts.

### 18.5 Direct `state_collapser` integration maturity

The package should keep `state_collapser` as the tower dependency, but the
boundary should stay narrow. The simplex package should not inherit unnecessary
state-collapser internals.

The clean division should remain:

```text
state_collapser: quotient schemas and tower construction
jet_simplex_search: simplex enumeration, lifting, witnesses, artifacts
```

## 19. Release-Framing Consequence

The package should be described publicly as a library pre-release descended
from Malik's simplicial graph-search program.

It should not yet be advertised as:

- a complete implementation of Malik's thesis;
- a Kan replacement engine;
- a neural simplicial learning framework;
- a general categorical algebra package.

It is also worth distinguishing this repo from
[`HGraphML`](https://github.com/TYLERSFOSTER/HGraphML): HGraphML is where the
message-passing branch has begun, while this package should be framed as the
bounded simplex-search and quotient-lift branch.

Accurate release claim:

`jet_simplex_search` is a small Python package for bounded simplex search in
directed graph data, including degenerate simplices, with static quotient-tower
lifting through `state_collapser` and auditable witness artifacts.

That claim is faithful to the Malik lineage and to the current code.

## 20. Final Assessment

The ideas in this repository are not accidental. They are the package-shaped
progeny of Malik's thesis and portfolio work.

The thesis supplies the conceptual frame:

- graphs as low-dimensional simplicial presentations;
- standard simplices as higher-order graph relations;
- degeneracy as essential structure;
- quotient hierarchies as a way to make search feasible;
- simplicial data as a foundation for later machine learning.

The portfolio supplies the prototype trail:

- 2-simplex search;
- adjacency-matrix search;
- simplicial-set construction;
- left Kan completion;
- successive quotient lifting;
- neural architectures that would consume the result, with the first separate
  package-level message-passing work now represented by
  [`HGraphML`](https://github.com/TYLERSFOSTER/HGraphML).

The present repo supplies the package discipline:

- bounded API;
- static tower;
- sparse frontiers;
- degenerate records;
- fiber-addressed lifting;
- H-to-G skeletonization;
- witness-correct artifacts;
- tests and smoke examples.

The most important inherited idea is the quotient-lift search pattern. The most
important package refinement is to make the downstairs simplex the search
address rather than a validation afterthought.

That is the through-line from Malik's work to `jet_simplex_search`.
