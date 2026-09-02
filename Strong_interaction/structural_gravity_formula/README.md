# Structural Gravity Formula Workspace

This directory is separated from the existing `Strong_interaction` validation pipeline.
It is a formula-development and thought-experiment workspace for testing whether temporary bounded concentration of interacting particles can provide a useful structural-gravity source descriptor.

No empirical validation or gravitational derivation is claimed here.

## 1. Minimal transient-source state

For a temporary interacting/bounded configuration, use

\[
\mathcal S_{\rm transient}
=
(E_{\rm cm},R_{\rm eff},\tau).
\]

- \(E_{\rm cm}\): center-of-mass energy of the temporary composite system.
- \(R_{\rm eff}\): explicitly declared effective spatial scale of the temporary composite description.
- \(\tau\): lifetime of the temporary bounded/interacting state when available.

For a two-body system,

\[
M_*^2c^4
=
E_{\rm tot}^2-c^2|\mathbf P_{\rm tot}|^2.
\]

In the center-of-mass frame,

\[
M_*c^2=E_{\rm cm}.
\]

Thus

\[
M_*=
\frac{E_{\rm cm}}{c^2}.
\]

## 2. Coarse-grained source concentration

Use the provisional spherical-volume descriptor

\[
V_{\rm eff}
=
\frac{4\pi}{3}R_{\rm eff}^3,
\]

\[
\mathcal C_{\rm src}
=
\frac{E_{\rm cm}}{V_{\rm eff}},
\]

or, in mass-density units,

\[
\rho_{\rm src}
=
\frac{E_{\rm cm}}{c^2V_{\rm eff}}.
\]

For two states,

\[
\frac{\mathcal C_2}{\mathcal C_1}
=
\frac{E_2}{E_1}
\left(\frac{R_1}{R_2}\right)^3.
\]

This quantity is a coarse-grained source-concentration descriptor, not an asserted fundamental gravitational density.

## 3. Internal/external describability

For observer or description resolution \(\epsilon\), a provisional resolution-limited scale is

\[
R_{\rm eff}^{(\epsilon)}
=
\max(R_{\rm pair},\epsilon).
\]

Then

\[
\mathcal C^{(\epsilon)}
=
\frac{E_{\rm cm}}
{\frac{4\pi}{3}[R_{\rm eff}^{(\epsilon)}]^3}.
\]

Different resolutions can therefore satisfy

\[
\mathcal C_{\rm int}
\neq
\mathcal C_{\rm ext}.
\]

This is to be interpreted as a describability difference, not as energy creation or destruction.

## 4. Structural-gravity target relation

Do not yet assume a direct law such as \(g\propto E\mathcal C^\beta\).

The current minimal target is only

\[
(E_{\rm cm},R_{\rm eff},\tau)
\longrightarrow
X,
\]

where \(X\) is a future geometric-distortion variable or field whose physical meaning must be fixed separately.

The first differential questions are

\[
\frac{\partial X}{\partial E_{\rm cm}},
\qquad
\left.
\frac{\partial X}{\partial R_{\rm eff}}
\right|_{E_{\rm cm}},
\qquad
\frac{\partial X}{\partial \tau}.
\]

If a distant response depends only on total mass-energy, the null baseline is

\[
\left.
\frac{\partial X_{\rm far}}
{\partial R_{\rm eff}}
\right|_{E_{\rm cm}}
=0.
\]

A nonzero residual would require separate physical validation before any structural-gravity claim.

## 5. Candidate empirical inputs

Priority data classes for later application:

1. Electron-ion dielectronic-recombination resonances: \(E_{\rm cm}\), resonance width \(\Gamma\), and \(\tau\simeq\hbar/\Gamma\).
2. Temporary negative-ion electron-molecule resonances: collision energy, resonance width, cross section, and molecular scale.
3. Electron-nucleus scattering: \(E_{\rm cm}\), \(Q^2\), form factors, with \(R_Q\sim\hbar c/\sqrt{Q^2}\) treated strictly as a resolution scale rather than a literal pair separation.
4. Atomic/molecular close-approach and collision-complex data: interparticle distance or effective complex size where independently available.

## 6. Audit rules

- Keep this workspace separate from the existing standard/structural validation pipeline.
- Do not treat \(R_Q\), bond length, orbital radius, cross-section radius, and fitted interaction radius as interchangeable definitions of \(R_{\rm eff}\).
- Do not identify temporary invariant-mass increase with creation of new total energy; it is the center-of-mass energy of the interacting system.
- Do not insert \(G\), Planck scales, \(GM\), Schwarzschild radius, or quantities derived from them when attempting an independent gravity bridge.
- Do not infer gravitational response from \(\mathcal C_{\rm src}\) before an explicit constitutive bridge is justified.
