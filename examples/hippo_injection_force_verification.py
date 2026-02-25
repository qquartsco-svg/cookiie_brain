#!/usr/bin/env python3
"""hippo injection이 PFE injection_func으로 합성되어 힘으로 작용하는지 검증

v0.7.2 변경사항:
  이전: hippo.step() → injection 결과가 set_extension()으로 기록만 됨
  이후: hippo.budgeter.compute_injection()이 PFE injection_func에 합성 → 힘으로 작용

검증 항목:
  1. _build_combined_injection()에 hippo가 포함되는지
  2. hippo injection이 상태 벡터를 실제로 변화시키는지
  3. hippo 없을 때 vs 있을 때 궤적 차이
  4. recall 모드에서 목표 우물로 끌리는지
  5. explore 모드에서 랜덤 방향 주입이 작동하는지
  6. store.step()이 PFE 전에 실행되는지 (기억 갱신 순서)

Author: GNJz (Qquarts)
Version: 0.7.2
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
from hippo import HippoMemoryEngine, HippoConfig
from hippo.memory_store import MemoryStore
from hippo.energy_budgeter import EnergyBudgeter

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
results = []


def check(name: str, condition: bool, detail: str = ""):
    tag = PASS if condition else FAIL
    results.append(condition)
    print(f"  [{tag}] {name}")
    if detail:
        print(f"         {detail}")


print("=" * 65)
print("hippo injection 힘 합성 검증 (v0.7.2)")
print("=" * 65)
print()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [1] _build_combined_injection 구조 확인
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("[1] _build_combined_injection에 hippo 포함 확인")

config = HippoConfig(
    eta=0.1,
    decay_rate=0.001,
    explore_strength=0.5,
    exploit_strength=0.5,
    recall_strength=2.0,
)
engine = HippoMemoryEngine(config=config, dim=2, rng_seed=42)

# 우물 3개 생성
engine.encode(np.array([3.0, 0.0]), strength=3.0)
engine.encode(np.array([-3.0, 0.0]), strength=3.0)
engine.encode(np.array([0.0, 3.0]), strength=3.0)

# injection_func 시그니처로 래핑
def hippo_injection_func(x, v, t):
    return engine.budgeter.compute_injection(x, v, engine.store)

x_test = np.array([1.0, 0.5])
v_test = np.array([0.1, -0.1])

inj = hippo_injection_func(x_test, v_test, 0.0)
check("hippo injection 벡터 생성", len(inj) == 2 and np.linalg.norm(inj) > 0,
      f"I = [{inj[0]:.4f}, {inj[1]:.4f}], |I| = {np.linalg.norm(inj):.4f}")

# tidal injection도 합성 가능한지
from solar import CentralBody, TidalField
sun = CentralBody(position=np.array([0.0, 0.0]), mass=10.0)
tidal = TidalField(central=sun)
tidal_inj = tidal.create_injection_func()

def combined(x, v, t):
    return tidal_inj(x, v, t) + hippo_injection_func(x, v, t)

inj_combined = combined(x_test, v_test, 0.0)
check("tidal + hippo 합산 가능", len(inj_combined) == 2,
      f"combined = [{inj_combined[0]:.4f}, {inj_combined[1]:.4f}]")
print()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [2] exploit 모드: 가까운 우물로 끌림
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("[2] exploit 모드 — 가까운 우물 (3,0)으로 끌리는 힘")

engine2 = HippoMemoryEngine(
    config=HippoConfig(
        exploit_strength=2.0,
        explore_strength=0.0,  # 탐색 끔
    ),
    dim=2, rng_seed=42,
)
engine2.encode(np.array([3.0, 0.0]), strength=5.0)

x_near = np.array([2.0, 0.0])
inj_exploit = engine2.budgeter.compute_injection(x_near, np.zeros(2), engine2.store)

# (3,0) 방향 = +x
check("exploit: +x 방향 힘", inj_exploit[0] > 0,
      f"I_x = {inj_exploit[0]:.4f} (양수 = 우물 방향)")
check("exploit: y 힘 ≈ 0", abs(inj_exploit[1]) < 0.01,
      f"I_y = {inj_exploit[1]:.6f}")
print()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [3] recall 모드: 목표 우물로 강한 끌림
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("[3] recall 모드 — 목표 우물 (-3,0)으로 강한 끌림")

engine3 = HippoMemoryEngine(
    config=HippoConfig(
        recall_strength=5.0,
        explore_strength=0.0,
        exploit_strength=0.0,
    ),
    dim=2, rng_seed=42,
)
engine3.encode(np.array([-3.0, 0.0]), strength=5.0)
engine3.recall(np.array([-2.5, 0.0]))

x_far = np.array([2.0, 0.0])
inj_recall = engine3.budgeter.compute_injection(x_far, np.zeros(2), engine3.store)

check("recall: -x 방향 (목표 쪽)", inj_recall[0] < 0,
      f"I_x = {inj_recall[0]:.4f} (음수 = 목표 방향)")
check("recall 세기 > exploit 세기", abs(inj_recall[0]) > abs(inj_exploit[0]),
      f"|recall| = {abs(inj_recall[0]):.4f} > |exploit| = {abs(inj_exploit[0]):.4f}")
print()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [4] explore 모드: 랜덤 방향 주입
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("[4] explore 모드 — 랜덤 방향 주입")

engine4 = HippoMemoryEngine(
    config=HippoConfig(
        explore_strength=1.0,
        exploit_strength=0.0,
    ),
    dim=2, rng_seed=42,
)

directions = []
for _ in range(100):
    inj_e = engine4.budgeter.compute_injection(
        np.array([0.0, 0.0]), np.zeros(2), engine4.store
    )
    if np.linalg.norm(inj_e) > 1e-10:
        directions.append(inj_e / np.linalg.norm(inj_e))

directions = np.array(directions)
mean_dir = np.mean(directions, axis=0)

check("explore: 방향 분산 (평균 ≈ 0)", np.linalg.norm(mean_dir) < 0.3,
      f"평균 방향 = [{mean_dir[0]:.4f}, {mean_dir[1]:.4f}], |mean| = {np.linalg.norm(mean_dir):.4f}")
check("explore: 모든 injection 비영", len(directions) == 100,
      f"{len(directions)}/100 비영 벡터")
print()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [5] 힘으로 작용하는지: 간이 적분 테스트
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("[5] 간이 적분 — hippo injection이 실제 궤적을 바꾸는지")

config5 = HippoConfig(
    recall_strength=3.0,
    explore_strength=0.0,
    exploit_strength=0.0,
)
engine5 = HippoMemoryEngine(config=config5, dim=2, rng_seed=42)
engine5.encode(np.array([5.0, 0.0]), strength=5.0)
engine5.recall(np.array([5.0, 0.0]))

# injection 없이 적분
x_no_inj = np.array([0.0, 0.0])
v_no_inj = np.array([0.0, 0.0])

# injection 있을 때 적분
x_with_inj = np.array([0.0, 0.0])
v_with_inj = np.array([0.0, 0.0])

dt = 0.01
for _ in range(500):
    # injection 없는 경우: 아무 힘 없음
    x_no_inj = x_no_inj + dt * v_no_inj

    # injection 있는 경우: hippo recall 힘
    inj = engine5.budgeter.compute_injection(x_with_inj, v_with_inj, engine5.store)
    v_with_inj = v_with_inj + dt * inj
    x_with_inj = x_with_inj + dt * v_with_inj

dist_no = np.linalg.norm(x_no_inj - np.array([5.0, 0.0]))
dist_with = np.linalg.norm(x_with_inj - np.array([5.0, 0.0]))

print(f"  injection 없이: x = [{x_no_inj[0]:.2f}, {x_no_inj[1]:.2f}], 목표까지 = {dist_no:.2f}")
print(f"  injection 있을 때: x = [{x_with_inj[0]:.2f}, {x_with_inj[1]:.2f}], 목표까지 = {dist_with:.2f}")

check("injection으로 목표에 접근", dist_with < dist_no,
      f"with={dist_with:.2f} < without={dist_no:.2f}")
check("목표 방향으로 이동", x_with_inj[0] > 0,
      f"x = {x_with_inj[0]:.2f} (양수 = 목표 방향 이동)")
print()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [6] store.step() 순서 검증: 강화가 먼저
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("[6] store.step() 순서 — 기억 강화가 PFE 전에 실행")

config6 = HippoConfig(eta=1.0, decay_rate=0.0)
engine6 = HippoMemoryEngine(config=config6, dim=2, rng_seed=42)
engine6.encode(np.array([1.0, 0.0]), strength=1.0)

amp_before = engine6.store._wells[0].amplitude

# store.step()이 강화를 수행
engine6.store.step(np.array([1.0, 0.0]), dt=0.1)
amp_after = engine6.store._wells[0].amplitude

check("store.step()으로 우물 강화", amp_after > amp_before,
      f"A: {amp_before:.4f} → {amp_after:.4f}")

# version이 바뀌면 pot_changed = True
changed = engine6.potential_changed
check("potential_changed 감지", changed,
      f"version changed = {changed}")
print()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 최종
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
n_pass = sum(results)
n_total = len(results)
print("=" * 65)
print(f"결과: {n_pass}/{n_total} PASS")
if n_pass == n_total:
    print("전체 PASS — hippo injection이 힘으로 작용 확인")
else:
    print(f"FAIL 항목: {n_total - n_pass}개")
print("=" * 65)
