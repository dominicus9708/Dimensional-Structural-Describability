# Hadron pre-G ratio test 001

## Purpose

This note performs a first real-data stress test of candidate minimal bounded realizations without using measured gravity, G, GM, gravitational radius, or any G-derived Planck quantity.

The test does **not** assert that the pion or proton has already been proven to be a DSD minimal bounded realization. They are used as candidate color-singlet hadrons because QCD confines quarks and gluons and no isolated color-charged quark/gluon subobject is observed as a free asymptotic particle. Mapping QCD compositeness to the DSD bounded-formation-submodel preorder remains a separate task.

## Common structural length proxy

To avoid mixing charge radius with mass/energy structure, use the slope of the total EMT A-form factor as a common proxy:

\[
\ell_A^2 = 6\,\frac{A'(0)}{A(0)}(\hbar c)^2.
\]

This is called an **A-slope structural radius** here. It is deliberately not identified with every convention called a hadron mass radius, because the proton Breit-frame energy-density radius can contain additional relativistic A, J, and D contributions.

For the preferred published fit families,

\[
A_i(t)=\frac{\alpha_i}{(1-t/\Lambda_i^2)^n},
\]

with n=1 for the pion monopole fit and n=2 for the proton dipole fit. Hence

\[
A'(0)=\sum_i \frac{n\alpha_i}{\Lambda_i^2}.
\]

The z-expansion results are retained as a model-dependence cross-check.

## Input provenance

Pion lattice-QCD inputs, Hackett et al., Phys. Rev. D 108, 114504 (2023):
- ensemble pion mass approximately 169 MeV;
- preferred monopole A-form-factor fits: Ag alpha=0.546, Lambda=1.129 GeV; Aq alpha=0.481, Lambda=1.262 GeV;
- total D(0)=-0.900(70);
- z-expansion A parameters and total D(0)=-0.860(92) are also recorded.

Proton lattice-QCD inputs, Hackett et al., Phys. Rev. Lett. 132, 251904 (2024):
- same ensemble family with a approximately 0.091 fm and fitted lattice nucleon mass am=0.4169, giving mN approximately 0.9040 GeV for the present central-value audit;
- preferred dipole A-form-factor fits: Ag alpha=0.501, Lambda=1.262 GeV; Aq alpha=0.510, Lambda=1.477 GeV;
- total D(0)=-3.87(97);
- z-expansion A parameters and total D(0)=-3.35(58) are also recorded.

## Candidate minimal-bounded status

The Particle Data Group QCD review states that neither quarks nor gluons are observed as free particles and that hadrons are color-singlet combinations of quarks, antiquarks and gluons. This makes light hadrons natural **candidate** minimal bounded realizations for the first stress test. However:

1. confinement is not itself a proof of the DSD boundedness predicate;
2. QCD constituent structure is not automatically identical to the DSD formation-submodel relation;
3. baryons and mesons may belong to different structural-gravity equivalence classes;
4. a successful ratio test cannot by itself establish minimality.

## d=3 pre-G test

For a candidate dimensionless structural factor F3, define

\[
\Lambda_3(B)=F_3(B)\frac{\ell_A}{m_B}.
\]

If pion and proton were in the same class with F3 equal, universality would require equal ell/m. This fails strongly.

### Preferred pole-family fits

Pion:

\[
\ell_A \simeq 0.4076\ \mathrm{fm},\qquad
\frac{\ell_A}{m}\simeq2.4119\ \mathrm{fm/GeV}.
\]

Proton:

\[
\ell_A \simeq0.5034\ \mathrm{fm},\qquad
\frac{\ell_A}{m}\simeq0.5569\ \mathrm{fm/GeV}.
\]

Thus

\[
\frac{(\ell/m)_\pi}{(\ell/m)_p}\simeq4.331.
\]

Equal F3 therefore fails. Universality would require

\[
\frac{F_{3,\pi}}{F_{3,p}}\simeq0.2309.
\]

## D-term structural-factor candidate

The EMT D-term is dimensionless and is associated with the internal mechanical structure/internal-force information of hadrons. It is therefore a physically motivated, non-gravitational candidate for a bounded-structure factor. The word "gravitational" in "gravitational form factor" does not mean that a real gravitational measurement or G is used; these quantities are matrix elements of the QCD energy-momentum tensor and are accessible in lattice QCD and hard exclusive reactions.

Test the simple candidate

\[
F_3(B)=|D_B(0)|.
\]

For the preferred pole-family central values,

\[
\frac{|D_\pi|}{|D_p|}
=\frac{0.900}{3.87}
\simeq0.2326,
\]

which is extremely close to the independently required ratio 0.2309 from the mass/length data.

The resulting D-weighted values are

\[
\Lambda_{D,\pi}=|D_\pi|\frac{\ell_\pi}{m_\pi}
\simeq2.1707\ \mathrm{fm/GeV},
\]

\[
\Lambda_{D,p}=|D_p|\frac{\ell_p}{m_p}
\simeq2.1551\ \mathrm{fm/GeV}.
\]

Their central-value ratio is

\[
\boxed{\Lambda_{D,\pi}/\Lambda_{D,p}\simeq1.0073}.
\]

This is a **candidate-line pass at the central-value level**, not a validation.

## Model-dependence cross-check

Using the z-expansion fits for both systems gives

\[
\ell_{A,\pi}\simeq0.4249\ \mathrm{fm},\qquad
\ell_{A,p}\simeq0.6591\ \mathrm{fm},
\]

and

\[
\Lambda_{D,\pi}\simeq2.1623\ \mathrm{fm/GeV},
\qquad
\Lambda_{D,p}\simeq2.4423\ \mathrm{fm/GeV}.
\]

Thus

\[
\boxed{\Lambda_{D,\pi}/\Lambda_{D,p}\simeq0.885}.
\]

The exact central-value coincidence weakens under a different fit model, but the discrepancy is still much smaller than the unweighted ell/m mismatch. The published D-term uncertainties, especially for the proton, are large enough that this comparison is exploratory rather than precision evidence.

## Why this is interesting

The unweighted geometric scale fails by factors of approximately 3.45--4.33 depending on fit model. Multiplying by |D(0)| brings the pion and proton values to within approximately 0.7% for the preferred fit family and approximately 11.5% for the z-expansion central values.

This is qualitatively consistent with the DSD expectation that a universal geometric-distortion coupling, if it exists, should involve not only mass and source size but also an independent dimensionless descriptor of bounded internal structure.

The D-term is especially interesting because it is tied to the EMT mechanical sector rather than observer resolution. It therefore does not suffer the immediate problem that invalidated using R_D itself as a gravitational charge.

## Critical caveats

1. **Not independent data:** ell_A and D are extracted from the same underlying EMT/GFF calculations, so their statistical and systematic correlations are not known in this simplified audit.
2. **Fit-model sensitivity:** the preferred-fit near-equality is not exact under the z-expansion.
3. **Minimality not proven:** pion and proton remain B_min candidates, not established DSD minimal bounded realizations.
4. **Class identity not proven:** meson and baryon may have different z_B signatures and need not share the same universal F3 law.
5. **D-term interpretation nuance:** pressure/shear interpretations of EMT densities have known conceptual subtleties; only the D-term as a well-defined EMT form factor is required for this test.
6. **No G prediction yet:** the common scale, if real, still has dimensions L/M. A dynamics/response bridge is still needed before comparing any resulting 3D coupling with measured G.

## Audit verdict

- FAIL: F3=1 for pion/proton candidate pair.
- PROMISING CANDIDATE: F3=|D(0)| substantially compensates the mass/length mismatch.
- PASS as pre-G methodology: no gravitational constant or gravitational observable is used to construct the ratio.
- OPEN: repeat across additional hadrons using comparable EMT A and D determinations and, where possible, statistically independent datasets.
- OPEN: determine whether |D|, or a D-derived boundedness invariant, can be motivated directly from DSD formation/boundedness dynamics rather than selected after observing this numerical coincidence.
