# Folder Map

**실제 폴더·코드 위치**만 정리한다. 시간 흐름은 [LAYER_FLOW.md](LAYER_FLOW.md) 참고.

---

## solar/ 루트

```
solar/
├── __init__.py          # 별칭 등록, 핵심 심볼 re-export
├── pipeline.py          # run_pipeline, 5단계 흐름 엔진
├── verify_imports.py     # 구조 검증 스크립트
├── FOLDER_MAP.md        # (solar 루트용 폴더 요약)
├── LAYER_FLOW.md        # (solar 루트용 시간 흐름)
├── INDEX_CODE_AND_DOCS.md
├── AUDIT_REPORT.md
└── _meta/
```

---

## _01_beginnings

```
_01_beginnings/
├── __init__.py
└── joe/
    ├── __init__.py
    ├── observer.py      # compute_planet_stress_and_instability, JOE 동역학
    └── run.py           # run(ic, water_snapshot)
```

- planet_dynamics 폴더는 제거됨. `solar.planet_dynamics` = `solar.joe` 별칭.

---

## _02_creation_days

```
_02_creation_days/
├── __init__.py
├── day1/                # 빛 (em: magnetic_dipole, solar_wind, magnetosphere, luminosity)
├── day2/                 # 궁창 (atmosphere)
├── day3/                 # 땅·바다 (surface, biosphere, gaia_fire)
├── day4/                 # 해·달·별 (core, data, cycles, nitrogen, gravity_tides, season_engine)
├── day5/                 # 생물 (mobility_engine, seed_transport, food_web)
├── day6/                 # 인지·종 (species_engine, mutation_engine, gaia_feedback, niche_model, ...)
├── day7/                 # 완결 (runner, sabbath, completion_engine)
├── bridge/               # GaiaBridge, GaiaLoopConnector, ring_attractor_shim, ...
├── engines/              # 01_solar_well ~ 12_evos_well
├── fields/               # firmament step/get_layer0 (래퍼)
└── physics/              # lucifer_core (래퍼)
```

- surface는 별도 최상위 폴더 없음. **day3/surface/** (SurfaceSchema, effective_albedo).  
- `solar.surface` → `solar._02_creation_days.day3.surface`

---

## _03_eden_os_underworld

```
_03_eden_os_underworld/
├── __init__.py
├── eden/                 # firmament, flood, initial_conditions, eden_os, search, biology, ...
├── biosphere/            # day3.biosphere re-export
├── cognitive/            # ring_attractor, spin_ring_coupling
├── governance/           # hades (listen, HadesObserver)
├── monitoring/           # Siren re-export
└── underworld/           # hades, deep_monitor, siren, wave_bus, consciousness
```

---

## _04_firmament_era

```
_04_firmament_era/
├── __init__.py           # firmament, initial_conditions re-export
├── engine.py             # run_firmament_era_step
└── README.md             # 구현 위치: _03/eden/firmament
```

---

## _05_noah_flood

```
_05_noah_flood/
├── __init__.py           # flood, firmament, initial_conditions re-export
├── engine.py             # run_flood_step, run_trigger_flood
└── README.md             # 구현 위치: _03/eden/flood
```

---

## 문서 역할 정리

| 문서 | 역할 |
|------|------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | 시스템 개요, 검증·Quick Test |
| [LAYER_FLOW.md](LAYER_FLOW.md) | 시간 흐름 (Pre-Creation → Flood Era) |
| [FOLDER_MAP.md](FOLDER_MAP.md) | 실제 폴더 구조 (이 문서) |
| [LAYERS.md](LAYERS.md) | 레이어↔경로 표 (기존) |
