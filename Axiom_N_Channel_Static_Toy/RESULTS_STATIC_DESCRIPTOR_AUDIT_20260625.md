# 정적 기술자 층위 audit 결과 노트

## 노트 분류

```text
검증 노트 / 정적식 / structural / descriptor layer audit
```

## 목적

기존 D2 코드와 저장된 결과를 재사용해, 현재 수식이 정적/동적 및 스칼라/벡터 중 어느 층에 속하는지 고정 기준으로 확인했다. 이 audit은 새 수식이나 새 물리 주장을 만들지 않는다.

## 현재 선긋기

```text
스칼라 정적
- single_channel_toy_dw
- nchannel_descriptor(theta)
- carrier--boundary M0--M4

벡터 정적
- channel_descriptors = (D1, D2, D3)
  단, 현재는 D2 구현의 중간표현이며 논문 수준 최종 벡터 정의는 아직 보류

스칼라 동역학
- D_w(t), Delta_res^str(t), S_str(t)

스칼라장 동역학
- alpha(x,t)

벡터 동역학
- 아직 정의·구현되지 않음
```

## 다시 계산한 정합성 결과

```text
D2 비어 있지 않은 admissible configurations: 21,798
channel vector dimension: 3
N=1 recovery maximum absolute error: 0
vector-to-scalar projection reconstruction maximum absolute error: 0
```

따라서 채널이 세 개라는 사실만으로 `nchannel_descriptor`가 벡터식이 되는 것은 아니다.

\[
\mathbf D=(D_1,D_2,D_3)
\]

는 벡터 정적 중간표현이고,

\[
D_\theta=\boldsymbol\theta^{\mathsf T}\mathbf D
\]

는 스칼라 정적 투영식이다.

## 기존 benchmark 결과 상태

```text
predictive hold-out summary: pass
20-seed predictive robustness summary: pass
10-seed carrier--boundary ablation summary: pass
```

carrier--boundary ablation의 의미도 그대로 보존된다.

```text
M4는 restriction survival 및 selected-inactive interface reach에서는 M1보다 개선.
M4는 restriction connectivity에서는 개선되지 않음.
```

이는 현재 static scalar projection의 적용 한계를 보이는 결과이지, 벡터 정적식을 이미 완성했다는 뜻은 아니다.

## 운영 규칙

향후 정적식 관련 수정 시에는 새 검증 코드를 처음부터 만들지 않는다.

1. `descriptor_registry.json`에 새 표현의 codomain, 시간 의존성, 구현 상태를 등록한다.
2. 기존 투영 또는 채널 구현을 바꿨다면 `run_static_descriptor_audit.py --rerun predictive`를 실행한다.
3. carrier/boundary 규칙을 바꿨다면 `--rerun full`을 사용한다.
4. 새 최종 벡터 성분을 실제로 정의하는 경우에만 그 성분 계산 코드를 별도 추가한다.
