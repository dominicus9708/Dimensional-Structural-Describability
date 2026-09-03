# Bounded refinement on formation submodels 001

## Purpose

This note anchors the structural-gravity notion of a minimal bounded realization to the existing Formation Axiom System instead of introducing an unrelated refinement calculus.

## 1. Existing formation-theoretic substrate

The Formation Axiom System already defines witness-reflecting formation embeddings and a formation-submodel preorder. A formation submodel preserves and reflects the relevant admission, describability, restriction, realization, assignment, role, and channel data on its image.

Structural gravity therefore does not need a new primitive notion of structural inclusion.

## 2. Structural-gravity boundedness predicate

Let

\[
\mathsf{Bd}(B)\in\{0,1\}
\]

be an application-specific bounded-source predicate supplied by the structural-gravity specialization. This predicate is not part of the current formation axioms and must be defined independently of measured gravity.

The predicate may use only structural-gravity-admissible source data, for example formation status, describability, closure/support conditions, internal localization information, or explicitly supplied non-gravitational constitutive data.

## 3. Bounded refinement

For two source-restricted formation realizations `B'` and `B`, define

\[
B'\preceq_{\rm bd}B
\]

when:

1. `B'` is a formation submodel of `B` through a witness-reflecting formation embedding; and
2. `Bd(B')=Bd(B)=1` under the same structural-gravity boundedness rule.

A refinement is proper when `B'` is not strictly formation-isomorphic to `B` under the inherited comparison structure.

## 4. Canonical minimal bounded realization

A bounded realization `B_min` is minimal when

\[
\mathsf{Bd}(B_{\min})=1
\]

and every bounded formation submodel `B'` of `B_min` is non-proper, i.e. it is strictly equivalent to `B_min` for the structural information retained by the specialization.

Equivalently, there is no strictly smaller bounded source-restricted formation submodel.

This definition is structural rather than metric. It does not assert that `B_min` has the smallest mass or smallest length in the universe.

## 5. Why strict-equivalence language matters

The formation-submodel relation is a preorder. Minimality should therefore not be defined merely by numerical cardinality or by assuming antisymmetry. The safe condition is:

> every bounded submodel of `B_min` carries no proper structural reduction relative to the declared specialization.

Strict formation isomorphism may be used when the complete formation descriptor is the comparison target. If structural gravity retains additional downstream property or localization data, the corresponding equivalence must be strengthened to preserve those records as well.

## 6. Dynamic stability condition

A static minimal bounded realization is not automatically dynamically persistent. The Structural Reorganization Dynamics framework treats lineage as additional data and allows branching, merging, status change, rank transition, and other reorganization events.

For a dynamically persistent minimal bounded source, structural gravity should separately require a lineage condition such as:

\[
B_{\min}(t_1)\rightsquigarrow B_{\min}(t_2)
\]

through declared component lineage over the persistence interval.

This prevents the word `bounded` from silently meaning `eternally stable`.

## 7. Consequence for minimum scale

Only after a canonical minimal bounded realization is selected may the specialization assign a characteristic measure `v_min` and define

\[
\ell_{\min}=v_{\min}^{1/d}.
\]

Thus the logical order is

\[
\boxed{
\text{formation submodel structure}
\to
\text{boundedness predicate}
\to
B_{\min}
\to
\ell_{\min},m_{\min}
}
\]

and not

\[
\text{postulated minimum spacetime length}\to B_{\min}.
\]

## 8. Audit status

- Supported by existing DSD formalism: formation embeddings, formation-submodel preorder, strict formation equivalence, and dynamic lineage as distinct additional data.
- New structural-gravity specialization data: the boundedness predicate, source-restricted model selection, and any downstream geometric localization/measure used to extract `ell_min`.
- Not yet established: existence or uniqueness of a minimal bounded realization for every source, comparability of all bounded refinements, or universality of any ratio built from `ell_min` and `m_min`.
