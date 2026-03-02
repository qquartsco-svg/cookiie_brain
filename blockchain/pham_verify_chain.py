#!/usr/bin/env python3
"""
PHAM 체인 무결성 검증.

사용법:
  python3 pham_verify_chain.py pham_chain_<이름>.json [pham_chain_*.json ...]

pham_sign_v4.py 와 동일한 해시 규칙으로 각 블록의 hash·previous_hash 연결을 검사한다.
GENESIS 블록(index 0, data.name == "GENESIS")은 건너뛴다.
"""

import hashlib
import json
import sys
from pathlib import Path


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def compute_block_hash(index: int, prev_hash: str, timestamp: float, data_dict: dict) -> str:
    """pham_sign_v4.py 와 동일한 블록 해시 계산."""
    data_hash = sha256_text(json.dumps(data_dict, sort_keys=True))
    s = f"{index}|{prev_hash}|{timestamp}|{data_hash}"
    return hashlib.sha256(s.encode()).hexdigest()


def verify_chain(path: Path) -> tuple:
    """
    단일 체인 파일 검증.
    Returns:
        (ok: bool, message: str)
    """
    if not path.exists():
        return False, f"파일 없음: {path}"
    try:
        chain = json.loads(path.read_text("utf-8"))
    except Exception as e:
        return False, f"JSON 로드 실패: {e}"
    if not isinstance(chain, list):
        return False, "체인은 배열이어야 함"
    if len(chain) == 0:
        return True, "빈 체인 (OK)"
    prev_hash = "0"
    for i, block in enumerate(chain):
        if not isinstance(block, dict):
            return False, f"블록 {i}: 객체가 아님"
        idx = block.get("index")
        ts = block.get("timestamp")
        data = block.get("data")
        stored_prev = block.get("previous_hash")
        stored_hash = block.get("hash")
        if data is None:
            return False, f"블록 {i}: 'data' 없음"
        if isinstance(data, dict) and data.get("name") == "GENESIS":
            prev_hash = stored_hash or "0"
            continue
        if idx is None or ts is None or stored_prev is None or stored_hash is None:
            return False, f"블록 {i}: index/timestamp/previous_hash/hash 중 누락"
        if stored_prev != prev_hash:
            return False, f"블록 {i}: previous_hash 불일치 (기대 {prev_hash!r}, 실제 {stored_prev!r})"
        expected_hash = compute_block_hash(idx, prev_hash, ts, data)
        if stored_hash != expected_hash:
            return False, f"블록 {i}: hash 불일치 (기대 {expected_hash!r}, 실제 {stored_hash!r})"
        prev_hash = stored_hash
    return True, "OK"


def main():
    if len(sys.argv) < 2:
        print("사용법: python3 pham_verify_chain.py pham_chain_<이름>.json [ ... ]")
        sys.exit(1)
    root = Path(__file__).parent
    all_ok = True
    for name in sys.argv[1:]:
        path = Path(name) if Path(name).is_absolute() else root / name
        ok, msg = verify_chain(path)
        if ok:
            print(f"✅ {path.name}: {msg}")
        else:
            print(f"❌ {path.name}: {msg}")
            all_ok = False
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
