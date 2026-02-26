# solar/ 개념 레이어 — 우주필드 → 지구환경(1~7일)

**목적**: 폴더 구조와 개념이 **흐름 순서**로 이해되도록 레이어를 한곳에 정의.  
(코드/import는 변경 없음. 구현은 기존 `core/`, `data/`, `em/`, `atmosphere/`, `surface/`, `cognitive/`에 그대로 둠.)

---

## 1. 전체 흐름 (한눈에)

```
[우주필드]  →  [태양]  →  [태양계]  →  [달]  →  [지구]
     │              │           │          │         │
     └──────────────┴───────────┴──────────┴─────────┘
                    core/ + data/  (N-body, 궤도, 질량, 반지름)

                              ↓  지구 기준 환경 설정

[지구 환경 레이어]
  · 1일 — 빛이 있으라         →  em/           (광도, 복사)
  · 2일 — 궁창 (바다-하늘)    →  atmosphere/   (온실, 수순환)
  · 3일 — 땅과 바다           →  surface/      (land_fraction, 알베도)
  · 4일~ — 해·달·별, 생명…    →  core/ + em/ + cognitive/ (기존) / Phase 8+
```

---

## 2. 레이어 ↔ 폴더 매핑

| 순서 | 개념 (환경 설정 흐름) | 구현 폴더 | 비고 |
|------|------------------------|----------|------|
| **0** | 우주필드·태양·태양계·달·지구 | `core/`, `data/` | N-body, 10-body, 세차, 조석, 해류 |
| **1** | 빛이 있으라 | `em/` | 광도 F(r), 복사 |
| **2** | 궁창 (바다-하늘 분리) | `atmosphere/` | 온실, column, 수순환(Phase 6a/6b) |
| **3** | 땅과 바다 | `surface/` | land_fraction, effective_albedo (Phase 7) |
| **4~** | 해·달·별, 생명·인지 | `core/`, `em/`, `cognitive/` | 궤도·광원·Ring Attractor, Phase 8+ |

---

## 3. 개념 폴더 (직관용)

레이어 순서를 **폴더로** 보고 싶을 때는 아래를 연다.  
(실제 코드는 상위 `solar/` 의 `core/`, `em/` 등에 있음.)

```
solar/concept/
├── 00_system/      ← 우주필드·태양·태양계·달·지구
├── 01_light/       ← 빛이 있으라
├── 02_firmament/   ← 궁창 (대기·수순환)
├── 03_surface/     ← 땅·바다
└── 04_onward/      ← 넷째날 이후 (해·달·별, 생명·인지)
```

각 폴더에는 **README만** 있고, 내용은 “이 레이어가 뭔지 + 구현은 `../core/` 등 어디에 있는지” 정리.

---

## 4. 의존 방향 (기어 규칙)

```
data/  ──►  core/   ◄──  em/
                ◄──  surface/   (독립)
                ◄──  atmosphere/  (em, surface 읽기)
                ◄──  cognitive/
                ◄──  brain_core_bridge.py  (조립)
```

- **surface/** 는 다른 레이어를 import 하지 않음.
- **atmosphere/** 는 em/, surface/ 를 **읽기 전용**으로 사용.

---

## 5. 요약

| 질문 | 답 |
|------|----|
| **개념상 레이어 순서** | system(0) → light(1) → firmament(2) → surface(3) → onward(4~) |
| **그걸 폴더로 보려면** | `solar/concept/` 아래 00~04 |
| **실제 코드 위치** | `solar/core/`, `data/`, `em/`, `atmosphere/`, `surface/`, `cognitive/` |
| **문서** | `docs/CREATION_DAYS_AND_PHASES.md` (날짜↔Phase), 이 파일 (폴더↔개념) |
