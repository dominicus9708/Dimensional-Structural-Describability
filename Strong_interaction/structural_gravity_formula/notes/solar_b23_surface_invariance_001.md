# Solar B23 surface geometric-distortion invariance test 001

## Purpose

Test whether different B23/SF-III solar-composition models can change the geometric-distortion value at the solar surface when the calibrated solar mass and radius are held fixed.

## Source basis

The B23/SF-III dataset contains solar models for GS98, AGSS09, C11, AAG21, MB22 meteoritic and MB22 photospheric compositions. These models differ in internal composition and associated internal structure, while representing the same present-day Sun and using a common solar radius calibration.

For the numerical surface baseline used here:

- common solar mass parameter reference: GM = 1.3271244e20 m^3 s^-2 (IAU nominal solar mass parameter)
- B23 solar radius summary value: R = 6.9599e8 m
- c = 299792458 m/s

The nominal GM is used only for the standard weak-field/GR comparison baseline. It is not treated as a DSD-derived gravity constant.

## Surface quantities

Define the potential-like surface depth scale

X_phi(R) = GM/(R c^2).

Then

X_phi(R) = 2.121618181368e-6.

If one instead records the leading metric-departure scale,

2 GM/(R c^2) = 4.243236362735e-6.

The corresponding standard-reference surface quantities are

|Phi(R)| = GM/R = 1.906815327806e11 m^2 s^-2,

g(R) = GM/R^2 = 273.9716558868 m s^-2,

v_esc(R) = sqrt(2GM/R) = 6.175460027895e5 m s^-1,

and the Schwarzschild exterior clock factor at the surface is

sqrt(1 - 2GM/(Rc^2)) = 0.9999978783796.

The corresponding gravitational redshift relative to infinity is

z = 2.121624933293e-6.

## B23 composition null test

Because all listed B23 composition models are calibrated to the same present-day solar boundary mass and radius, the spherical monopole surface value is identical:

X_phi,GS98(R) = X_phi,AGSS09(R) = X_phi,C11(R) = X_phi,AAG21(R) = X_phi,MB22m(R) = X_phi,MB22p(R).

Therefore

Delta X_phi(R) = 0

between these composition models under the common M,R monopole baseline.

This does not imply identical internal geometry. Different composition models can have different rho(r), temperature, sound-speed, opacity, abundance and enclosed-mass profiles. Hence Delta X(r) may be nonzero for r<R while the boundary difference closes to zero at R.

## Structural-gravity reading

This provides a useful boundary null condition:

1. internal structure may reshape the geometric-distortion surface inside the star;
2. the exterior spherical monopole is fixed by the common total source and outer radius;
3. an additional DSD structural term that survives at the surface despite identical total mass and radius would require independent empirical evidence and must not be inserted by definition;
4. the first target is therefore the radial residual Delta X(r) between composition models, subject to Delta X(R)=0 in the null baseline.

## DSD absolute-value limitation

The number 2.121618181368e-6 is not yet an independently derived DSD absolute distortion constant. It is the standard potential-like dimensionless baseline obtained after using the externally known solar GM.

Without importing the standard gravitational coupling, DSD currently supplies only an uncalibrated form such as

X_DSD(R) = Gamma_X M/R,

or a dimensionless normalization relative to a chosen reference surface.

Recovering Gamma_X without circular use of G remains a separate structural-gravity task.
