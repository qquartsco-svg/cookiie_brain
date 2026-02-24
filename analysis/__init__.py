"""analysis — 분석 도구 (Layer 1~6)

trunk(줄기) 위에 쌓이는 물리 분석 레이어:
  Layer 1: 통계역학 (Kramers, 전이 행렬, 엔트로피)
  Layer 2: 다체/장론 (N-body 상호작용)
  Layer 3: 게이지/기하학 (위치 의존 자기장)
  Layer 4: 비평형 일 정리 (Jarzynski, Crooks)
  Layer 5: 확률역학 (Fokker-Planck, Nelson)
  Layer 6: 정보 기하학 (Fisher 계량, 곡률)

사용법:
  from analysis.Layer_1 import kramers_rate
  from analysis.Layer_6 import FisherMetricCalculator
"""
