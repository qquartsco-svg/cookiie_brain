"""trunk — 줄기 (Phase A/B/C)

운동 방정식의 구성 요소:
  Phase A: 자전 (ωJv 코리올리 회전)
  Phase B: 공전 (가우시안 다중 우물 퍼텐셜)
  Phase C: 요동 (Langevin noise, FDT)

이 세 Phase가 합쳐져 trunk(줄기)을 이룬다:
  m ẍ = -∇V(x) + ωJv - γv + I(x,v,t) + σξ(t)

trunk 위에 layers/(Layer 1~6) 분석 도구가 올라간다.
"""
