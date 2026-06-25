# D2 다중채널 정적식: hold-out 예측 토이모델 명세

## 상태

- 분류: 유한 조합론적 hold-out 토이 검증
- 기반: 현재 `Structural Admissibility` 공리의 3×3 D2 격자 실현
- 목적: 단일채널 toy descriptor와 3채널 정적식이 **공리와 독립적으로 계산한 구조적 목표량**을 얼마나 잘 근사하는지 비교
- 비대상: 물리 관측량 예측, 양자 탈동조화, 입자 크기 상한, 표준 이론 대체

## 데이터

전체 admissible D2 configurations는 빈 carrier 하나를 포함해 21,799개다. 정규화된 정적 기술자를 계산할 수 있는 비어 있지 않은 carrier configurations 21,798개만 사용한다.

학습·평가 분할은 configuration이 아니라 selected carrier \(S\) 단위로 한다. 동일한 \(S\)에서 나온 서로 다른 active relation record \(A\)가 학습과 hold-out에 동시에 포함되는 것을 막기 위해서다. 분할은 \(|S|\)별 층화와 고정 seed를 사용한다.

## 입력 채널

현재 D2 정합 시험과 같은 세 채널을 사용한다.

\[
D_q(p)=\frac{1}{|C_p|}\sum_{x\in C_p}\alpha_{p,q}(x),
\qquad C_p=S_p.
\]

\[
\alpha_{p,1}(x)=\frac{\deg_A(x)}{\deg_X(x)}.
\]

\[
\alpha_{p,2}(x)=\frac{\deg_{R_S}(x)}{\deg_X(x)}.
\]

\[
\alpha_{p,3}(x)=\frac{1}{1+\deg_{\partial_R S}(x)}.
\]

## 독립 정답값

정답은 기술자 값으로 만들지 않는다. 각 admissible configuration \(p=(S,A)\)에 대해 모든 nonempty element-complete restriction을 직접 열거한다.

\[
Y_{\mathrm{surv}}(p)
=
\frac{1}{2^{|S|}-1}
\sum_{\varnothing\ne Y\subseteq S}
\mathbf 1\!\left[A\cap R_Y\ne\varnothing\right].
\]

이는 무작위로 하나의 nonempty restriction을 택했을 때, 적어도 하나의 기록된 활성 관계가 살아남을 정확한 확률이다.

## 비교 모형

단일채널 기준선:

\[
\widehat Y_1=\beta_0+\beta_1D_1.
\]

고정 3채널식:

\[
\widehat Y_{\mathrm{fixed}}
=\beta_0+\beta_1(0.5D_1+0.3D_2+0.2D_3).
\]

학습 3채널식:

\[
\widehat Y_N
=\beta_0+\beta_1\sum_{q=1}^{3}\theta_qD_q,
\qquad
\theta_q\ge0,
\qquad
\sum_q\theta_q=1.
\]

학습 표본에서의 3채널 affine 회귀 계수가 모두 음수가 아니면, 그 계수는 정확히 위 convex descriptor 형태로 재매개화한다. 어느 채널 계수가 음수이면 이 정적식 형태를 유지하지 못하므로 해당 실행은 실패로 처리한다.

## 평가 지표

hold-out carrier에 대해 MAE, RMSE, \(R^2\)를 비교한다.

\[
\operatorname{MAE}_N<\operatorname{MAE}_1,
\qquad
\operatorname{RMSE}_N<\operatorname{RMSE}_1
\]

이면 이 D2 목표에 한해 다중채널 기술자가 단일채널보다 구조 보존률을 더 잘 근사했다고 기록한다.