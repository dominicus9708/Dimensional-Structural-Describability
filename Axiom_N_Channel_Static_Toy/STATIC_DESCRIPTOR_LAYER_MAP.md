# 정적 기술자 층위 지도 및 재검사 규칙

## 목적

이 문서는 기존 코드와 결과를 재사용해, 수식이 **정적/동적**, **스칼라/벡터** 중 어디에 속하는지를 같은 기준으로 기록한다. `공리-준수`는 논문 정식명칭이 아니라 내부 비교 구분자일 뿐이다.

## 판정 기준

\[
\text{static} \Longleftrightarrow p \text{와 구조 성분이 시간에 따라 고정됨.}
\]

\[
\text{scalar} \Longleftrightarrow \operatorname{codomain}=\mathbb R.
\]

\[
\text{vector} \Longleftrightarrow \operatorname{codomain}=\mathbb R^m,\quad m\ge2.
\]

따라서 채널이 세 개여도

\[
D_{\theta}^{[3]}=\boldsymbol\theta^{\mathsf T}\mathbf D
\]

처럼 최종 출력이 하나이면 **스칼라 정적 투영식**이다. 반대로

\[
\mathbf D=(D_1,D_2,D_3)
\]

를 보존하면 **벡터 정적 기술자**다.

## 현재 등록 상태

```text
구현된 스칼라 정적식
- single_channel_toy_dw
- nchannel_descriptor(theta)
- carrier--boundary ablation M0--M4

구현된 벡터 정적 중간표현
- channel_descriptors = (D1, D2, D3)

제안된 논문 수준 벡터 정적 기술자
- Static Structural Descriptor Vector
- 아직 각 성분의 최종 정의·정리·명제가 닫히지 않음

기존 스칼라 동역학
- D_w(t), Delta_res^str(t), S_str(t)

기존 scalar-field 동역학
- alpha(x,t)

미구현 벡터 동역학
- coupled vector descriptor dynamics
```

## 기존 결과를 다시 쓰는 방법

`run_static_descriptor_audit.py`는 새 수식을 만들지 않고 다음을 한다.

1. `channel_descriptors`가 길이 3의 벡터 출력인지 확인한다.
2. `nchannel_descriptor`가 \(\boldsymbol\theta^\mathsf T\mathbf D\)와 정확히 일치하는지 확인한다.
3. \(N=1\)에서 `single_channel_toy_dw`로 환원되는지 확인한다.
4. 저장된 predictive 및 carrier--boundary ablation 결과가 존재하고 `pass`인지 읽는다.
5. registry에서 각 표현의 층위가 중복·충돌 없이 선언되었는지 확인한다.

이는 과거 결과의 의미를 다시 해석하거나 수식을 새로 작성하지 않고, 변경 뒤에도 같은 층위와 환원 관계가 유지되는지 빠르게 확인하는 용도다.

## 재실행 수준

```text
--rerun none
- 레지스트리·환원·투영·저장 결과만 빠르게 감사

--rerun structure
- 기존 공리 정합성 D2 실행도 재수행

--rerun predictive
- structure + 단일/반복 hold-out 벤치마크 재수행

--rerun full
- predictive + 10-split carrier--boundary ablation 재수행
```

새로운 벡터 성분을 실제로 추가할 때에만 수식 구현을 보완한다. 그 외의 재확인·층위 구분·기존 오차 확인은 이 audit과 이미 있는 스크립트를 사용한다.
