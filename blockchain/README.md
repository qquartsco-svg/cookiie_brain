# blockchain/ — PHAM 블록체인 서명 (층위 분리)

**원칙**: 각 층위·레이어가 섞이지 않도록, **폴더별로** 체인을 둔다.  
(다윈의 종·속·과처럼 상위/하위 구조가 유기적으로 레이어로 이어지고, 상태공간 안에서 추적 가능해야 함.)

---

## 구조

| 위치 | 용도 |
|------|------|
| **이 폴더 (blockchain/)** | solar/ 및 프로젝트 루트 레이어용 PHAM 체인 (pham_chain_*.json). **루트에 있던 pham_chain_*.json 전부 여기로 이동됨.** |
| **cookiie_brain/blockchain/** | cookiie_brain/ 레이어용 체인 + pham_sign_v4.py |

- solar/ 관련 서명 시 **반드시 이 폴더(blockchain/)를 cwd로** 실행 → 체인 파일이 여기 생성됨.  
- 루트 README 등 루트급 문서는 루트에 두었던 pham_chain_README.json 등 기존 규칙 유지 가능.

---

## 서명 방법 (solar / 루트 레이어)

**이 레포(CookiieBrain) 루트 기준:**

```bash
# 방법 A: blockchain/ 폴더에서 실행 (체인 파일이 blockchain/ 에 생성됨)
cd blockchain
python3 pham_sign_v4.py ../solar/<파일경로> --author "GNJz" --desc "<설명>"

# 방법 B: 루트에서 실행
python3 blockchain/pham_sign_v4.py solar/<파일경로> --author "GNJz" --desc "<설명>"
```

→ `pham_chain_<파일stem>.json` 이 **blockchain/** 안에 생성됨.

**cookiie_brain/ 서브폴더가 있는 구조**에서는  
`python3 ../cookiie_brain/blockchain/pham_sign_v4.py ../solar/...` 형태로 cwd를 `blockchain/`으로 두고 실행 가능.

---

## 체인 검증 (Verification)

`pham_chain_*.json` 무결성 확인:

```bash
cd blockchain
python3 pham_verify_chain.py pham_chain_<이름>.json
```

- **prev_hash** 연결이 맞는지, 각 블록의 **hash**가 `index|prev_hash|timestamp|data_hash` 재계산값과 일치하는지 검사.
- GENESIS 블록은 건너뜀. 실패 시 첫 불일치 블록 인덱스와 이유를 출력.
- **참고**: 구 형식(previous_hash/hash 필드 누락 또는 이전 해시 규칙) 체인은 검증 실패할 수 있음. v4 형식만 지원.

---

## 이번에 추가된 체인 (개념 레이어 + 셋째날)

- pham_chain_LAYERS.json — solar/LAYERS.md (개념 레이어 정의)
- pham_chain_README.json — solar/README.md (solar 개념 섹션)
- pham_chain_surface_schema.json — solar/surface/surface_schema.py
- pham_chain_brain_core_bridge.json — solar/brain_core_bridge.py
