# D2 carrier--boundary ablation benchmark (10 carrier-level splits)

## Scope

This is a finite structural ablation in an extended D2 comparison regime. It is not an empirical or physical validation. The canonical D2 regime is retained as the all-blocked, carrier-exact subset.

## M4 vs M1, repeated selected-domain hold-outs

```text
Target                              M1 MAE mean     M4 MAE mean     MAE effect         all improved
restriction_survival               0.059615151       0.047593673       +20.163% ± 0.832%  True
restriction_connectivity           0.115414720       0.119634863       -3.646% ± 1.281%  False
selected_inactive_interface_reach  0.392009587       0.306323984       +21.860% ± 0.331%  True
```

```text
Target                              M1 RMSE mean    M4 RMSE mean    RMSE effect        all improved
restriction_survival               0.073676574       0.060325068       +18.119% ± 0.847%  True
restriction_connectivity           0.155046652       0.163976188       -5.756% ± 0.463%  False
selected_inactive_interface_reach  0.427654108       0.359915778       +15.842% ± 0.540%  True
```

## Interpretation

M4 improves two of the three exact D2 targets across every split: restriction survival and selected-inactive interface reach. It is consistently worse for restriction connectivity. Therefore this benchmark supports a scoped claim that active-carrier and boundary-clause information add useful structural signal for certain targets; it does not establish universal scalar-descriptor superiority.

## Exact compatibility checks

```text
Canonical subset recovery, C=S:
M1=M2 maximum absolute descriptor-channel error: 0
M3=M4 maximum absolute descriptor-channel error: 0

Conservative interface gluing witness:
The bridge relation between (0,0) and (0,1) becomes internal after gluing,
but remains absent from the active-relation record. Auto-activation: false.
```
