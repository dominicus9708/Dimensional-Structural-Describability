# Canonical minimal bounded realization 001

## Motivation

The previous bounded-scale invariance audit shows that if every bounded hierarchy is treated as a freely replaceable descriptive regrouping, the explicit microscopic scale cancels from the unique hierarchy-invariant source-to-distortion monomial. Therefore a microscopic bounded scale can enter a physical structural-gravity law only if the theory itself selects a distinguished bounded realization level rather than allowing an analyst to choose it arbitrarily.

## 1. Admissible bounded realizations

For a realized physical source `S`, let `B(S)` denote the structural-gravity specialization's family of admissible bounded realization records. A record may inherit formation data, typed property data, and any supplied localization/measure data required to evaluate boundedness and structural size.

`B(S)` is downstream of the Formation and Property Axiom Systems. The core systems do not infer physical boundedness merely from a label.

## 2. Refinement relation

Introduce a supplied refinement preorder `preceq_B` on admissible bounded realizations.

Interpret

\[
B_1 \preceq_B B_2
\]

as: `B_1` is at least as fine a bounded realization of the same source as `B_2`, with an explicit structure-preserving map from the finer bounded records into the coarser realization.

A pure descriptive refinement must preserve the declared total physical source. Actual binding, decay, contraction, expansion, or redistribution is a dynamical transition and is not identified with refinement.

## 3. Minimal bounded realization

A bounded realization `B_min` is refinement-minimal when there is no strictly finer admissible bounded realization `B'` such that

1. `B' preceq_B B_min`,
2. `B'` preserves the same physical source under the declared source-reconstruction map,
3. every newly resolved component remains formed/admitted and structurally describable,
4. every newly resolved component satisfies the structural-gravity boundedness predicate, and
5. the refinement is not merely a change of external observation resolution.

Thus `B_min` is not "the smallest measured thing". It is the finest bounded realization that remains internally legitimate under the supplied formation, describability, and boundedness rules.

## 4. Minimum scale as a derived property

Only after a localization metric or additive `d`-measure has been supplied may `B_min` receive a structural scale.

For one minimal bounded component with positive additive measure `v_min`, define

\[
\ell_{\min}:=v_{\min}^{1/d}.
\]

Therefore `ell_min` is derived from a canonical bounded realization plus a supplied metric/measure structure. It is not a universal lattice spacing imposed on space.

## 5. Uniqueness is not automatic

A source may possess multiple incomparable refinement-minimal bounded realizations. Therefore the physically relevant object should initially be the minimal family

\[
\mathfrak M_B(S)
:=
\{B\in\mathfrak B(S):B\text{ is refinement-minimal}\}.
\]

A unique `B_min` may be used only if uniqueness is proved. Otherwise one should quotient by an appropriate strict formation/property equivalence and use only quantities constant on the resulting equivalence class.

## 6. Required invariance for a physical coupling

If a candidate microscopic coupling ingredient `Q(B)` is used, require

\[
Q(B_1)=Q(B_2)
\]

for all strictly equivalent members of the selected minimal class.

If inequivalent minimal realizations yield different values, either the source has genuine structural branches or `Q` is not yet a well-defined physical observable.

## 7. Relation to describability resolution

External observation resolution `epsilon` does not define `B_min`. It only determines which parts of a pre-existing bounded realization are externally distinguishable.

Hence a valid minimum-level quantity must satisfy an external-resolution invariance condition such as

\[
Q_{\min}^{(\epsilon_1)}=Q_{\min}^{(\epsilon_2)}
\]

whenever both descriptions refer to the same underlying minimal bounded realization and differ only by external coarse-graining.

## 8. Consequence for the geometric coupling problem

There are now two logically distinct branches.

### Aggregate-invariant branch

If the bounded level is arbitrary, hierarchy invariance forces the microscopic scale to cancel and yields only aggregate quantities such as

\[
L_\Sigma^{d-2}/M.
\]

### Canonical-minimum branch

If structural-gravity rules select a refinement-minimal bounded realization, quantities such as

\[
m_{\min},\qquad \ell_{\min}
\]

are no longer arbitrary hierarchy coordinates. They may contribute to a constitutive coupling, provided the resulting expression is invariant across equivalent minimal realizations and across external resolution changes.

## Audit status

- PASS: the canonical-minimum concept avoids treating an analyst-selected bounded hierarchy as physical.
- PASS: minimum structural length is derived from bounded realization plus metric/measure, not imposed as spatial discreteness.
- OPEN: existence of a refinement-minimal bounded realization for every relevant source.
- OPEN: uniqueness or equivalence-class stability of the minimum.
- OPEN: whether a minimum-level invariant can supply the missing non-circular geometric-distortion coupling.
- REQUIRED: the boundedness predicate and refinement relation must be explicit structural-gravity specialization data; they are not consequences of the current Formation or Property Axiom cores merely from terminology.
