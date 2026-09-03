# Solar radial geometric-surface diagnostic 001

## Purpose

Move the structural-gravity test from planetary bulk quantities to a stellar radial structure where enclosed mass, local density, temperature and composition are available as functions of radius.

## Data hierarchy

Primary calculation input in this first pass:

- Bahcall & Pinsonneault BP2004 machine-readable Standard Solar Model table.
- Source: https://www.sns.ias.edu/~jnb/SNdata/Export/BP2004/bp2004stdmodel.dat
- The table provides M/Msun, R/Rsun, T, rho, P, L/Lsun, X(1H), X(4He), X(3He), X(12C), X(14N), X(16O).

Modern upgrade source already selected:

- Herrera & Serenelli, Standard Solar Models B23 / Solar Fusion III, Zenodo 10.5281/zenodo.10822316.
- The package contains updated inner-structure variables and chemical abundances for GS98, AGSS09, C11, AAG21, MB22m and MB22p composition choices.
- BP2004 is therefore used here as a transparent method-validation baseline, not as the final composition standard.

## Important composition audit

Stellar spectroscopy directly constrains mainly photospheric/atmospheric abundances. It does not directly measure the exact core elemental mixture. For the Sun, core/interior composition is additionally constrained through helioseismology, solar-neutrino observations and calibrated solar models. Therefore structural-gravity work must keep the following provenance classes separate:

1. photospheric spectroscopic abundance,
2. helioseismic inversion or constraint,
3. neutrino constraint,
4. stellar-model inferred radial abundance.

In stellar astrophysics, "metals" means elements heavier than helium; these are not macroscopic solid metal or rock inclusions in the solar core.

## Geometric diagnostics without using G

For radius fraction x=r/Rsun and enclosed mass fraction m=M(<r)/Msun, define

slope_rel_surface = m/x^2.

For a spherical baseline this has exactly the same radial scaling as g(r)/g(Rsun), but no absolute gravitational constant is used.

Define also

enclosed_depth_proxy_rel_surface = m/x.

This is only the enclosed-mass contribution scale. It is NOT the full potential inside a star, because outer shells contribute a radius-independent potential offset at an interior point.

Define

mean_density_proxy_rel_solar_mean = m/x^3.

This is proportional to the mean enclosed density. The machine-readable model also supplies the distinct local density rho(r).

## Selected radial results

At r=0.00649 Rsun:

- M(<r)=2.98e-5 Msun
- rho=153.1 g/cm^3
- H mass fraction=0.33984
- He4 mass fraction=0.64034
- slope_rel_surface=0.708

At r=0.07759 Rsun:

- M(<r)=0.04026 Msun
- rho=105.4 g/cm^3
- slope_rel_surface=6.69

At r=0.17103 Rsun:

- M(<r)=0.25173 Msun
- rho=46.37 g/cm^3
- slope_rel_surface=8.61

At r=0.41974 Rsun:

- M(<r)=0.81583 Msun
- rho=3.155 g/cm^3
- slope_rel_surface=4.63

At r=0.71805 Rsun:

- M(<r)=0.97696 Msun
- rho=0.1793 g/cm^3
- slope_rel_surface=1.89

At r=0.88850 Rsun:

- M(<r)=0.99775 Msun
- rho=0.03136 g/cm^3
- slope_rel_surface=1.26

## Structural-gravity reading

The stellar profile confirms the same separation already found in the 10^4 Msun thought experiment, but now with a real calibrated solar-model profile:

- local density rho(r) decreases strongly outward;
- enclosed mass M(<r) increases monotonically;
- the slope diagnostic M(<r)/r^2 rises from the center, reaches an interior maximum and then falls toward the surface;
- therefore local source concentration, total enclosed source and geometric-surface slope are not interchangeable quantities.

For a potential-like geometric descriptor X, the physically meaningful radial shape must be reconstructed from the slope, schematically

X(r)-X(R) proportional to integral from r to R of [M(<s)/s^2] ds,

with the eventual DSD constitutive bridge left unspecified. The simple M(<r)/r quantity is retained only as an enclosed-source diagnostic, not as the full interior potential.

## Next step

1. Replace the BP2004 baseline with one or more B23/SF-III radial profiles.
2. Compare high-Z and low-Z / modern composition choices while holding total solar M and R fixed.
3. Add helioseismic sound-speed constraints and neutrino production profiles.
4. Test whether any proposed DSD bounded-structure descriptor changes the external or radial geometric response after ordinary density, pressure, rotation and composition effects are accounted for.
