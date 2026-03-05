# SIGNATURE — _06_lucifer_impact 레이어 서명

이 문서는 `_06_lucifer_impact` 레이어를 구성하는 파일들의
**Git 객체 해시(SHA1)** 를 기록하여, 코드 무결성을 검증하기 위한 용도다.

기준 리포지터리:
- `qquartsco-svg/cookiie_brain` 의 `main` 브랜치

생성 방법:

```bash
cd CookiieBrain
git hash-object solar/_06_lucifer_impact/__init__.py
git hash-object solar/_06_lucifer_impact/impact_estimator.py
```

아래 표의 값과 일치해야 한다.

| 파일 | git hash-object (blob SHA1) |
|------|-----------------------------|
| `solar/_06_lucifer_impact/__init__.py` | `d1392bdd5286cfff0f50a5716bba0c25a9c7a8dd` |
| `solar/_06_lucifer_impact/impact_estimator.py` | `1a099273f31cf49caaa7b18b736a50a8b850055d` |

검증 시 위 명령을 다시 실행해 같은 SHA1 이 나오면,  
루시퍼 임팩트 레이어의 코드가 서명 시점 이후로 변경되지 않았음을 의미한다.

