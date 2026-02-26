# 00 — 우주필드 · 태양 · 태양계 · 달 · 지구

**개념**: 중력장 위에 점 질량이 놓이고, 태양계·달·지구가 형성되는 단계.  
지구 "환경 설정"의 **무대**가 되는 스케일.

---

## 구현 위치

| 폴더 | 내용 |
|------|------|
| **`../data/`** | NASA/JPL 기반 행성 데이터, build_solar_system() |
| **`../core/`** | N-body 엔진, Body3D, EvolutionEngine, SurfaceOcean, 조석·세차·해류 |

---

## 상태공간

- pos, vel, spin_axis, depths[], vorticity[] (core)
- 공간 격자 없음: 전역 궤도·자전·표면 우물

---

## 다음 레이어

→ **01_light**: 이 계에 빛(광도)이 켜짐.
