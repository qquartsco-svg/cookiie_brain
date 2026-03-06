"""Phase A: 부호 및 직교성 수치 검증 (MATH_VERIFICATION_CHECKLIST)

실행: Phase_A/ 에서
  python verify_math.py

또는 00_BRAIN 기준:
  python CookiieBrain/Phase_A/verify_math.py

체크 1: field_func = -∇E 인지 (고정 W, b로 수치 미분과 비교)
체크 2: r·R(x) ≈ 0 인지 (여러 x, pole에 대해)
"""

import numpy as np
import sys
from pathlib import Path

# Phase_A 내부이므로 현재 디렉터리
Phase_A_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(Phase_A_dir.parent))

# Well formation integration (field = Wx+b)
pfe_path = Phase_A_dir.parent.parent / "Brain_Disorder_Simulation_Engine" / "Unsolved_Problems_Engines" / "PotentialFieldEngine"
sys.path.insert(0, str(pfe_path))

def test_field_sign():
    """체크 1: create_field_from_wells 반환값이 -∇E 인지 확인."""
    try:
        from well_formation_integration import create_potential_from_wells, create_field_from_wells
    except ImportError as e:
        print("체크 1 스킵 (well_formation_integration 미사용):", e)
        return False
    # 고정 W, b (2x2)
    W = np.array([[1.0, 0.2], [0.2, 1.0]])
    b = np.array([0.1, -0.1])
    class Well:
        pass
    well = Well()
    well.W = W
    well.b = b
    V = create_potential_from_wells(well)
    field = create_field_from_wells(well)
    eps = 1e-6
    x = np.array([0.5, -0.3])
    # 수치 gradient of E (E = V)
    grad = np.zeros(2)
    for i in range(2):
        xp = x.copy()
        xp[i] += eps
        xm = x.copy()
        xm[i] -= eps
        grad[i] = (V(xp) - V(xm)) / (2 * eps)
    neg_grad_E = -grad
    field_at_x = field(x)
    err = np.linalg.norm(field_at_x - neg_grad_E)
    ok = err < 1e-5
    print("체크 1 (부호): field(x) vs -∇E(x) 오차 norm =", err, "->", "OK" if ok else "FAIL")
    return ok


def test_orthogonality():
    """체크 2: r·R(x) ≈ 0 (단순형)."""
    try:
        from Phase_A import Pole, create_rotational_field
    except ImportError:
        from rotational_field import Pole, create_rotational_field
    pole = Pole(position=np.array([0.0, 0.0]), rotation_direction=1, strength=1.0)
    R = create_rotational_field(pole, use_simple_form=True)
    points = [np.array([1.0, 0.0]), np.array([0.3, -0.5]), np.array([-0.2, 0.8])]
    all_ok = True
    for x in points:
        r = x - pole.position
        Rx = R(x)
        dot = np.dot(r, Rx)
        ok = abs(dot) < 1e-10
        if not ok:
            all_ok = False
        print("  r·R at", x, "=", dot, "->", "OK" if ok else "FAIL")
    print("체크 2 (직교성 r·R=0):", "OK" if all_ok else "FAIL")
    return all_ok


def main():
    print("Phase A 수학 검증 (부호 + 직교성)")
    print("---")
    r1 = test_field_sign()
    print("---")
    r2 = test_orthogonality()
    print("---")
    print("전체:", "PASS" if (r1 and r2) else "일부 FAIL")


if __name__ == "__main__":
    main()
