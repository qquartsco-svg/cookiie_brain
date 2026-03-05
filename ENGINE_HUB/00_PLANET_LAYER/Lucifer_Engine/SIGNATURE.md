# SIGNATURE — Lucifer Engine 서명

이 문서는 **Lucifer Engine** 패키지를 구성하는 파일들의 **Git 객체 해시(SHA1)** 를 기록하여, 코드·설정 무결성을 검증하기 위한 용도입니다.

기준: CookiieBrain 리포지터리 `ENGINE_HUB/00_PLANET_LAYER/Lucifer_Engine/` 내 파일.

생성 방법:

```bash
cd CookiieBrain
git hash-object ENGINE_HUB/00_PLANET_LAYER/Lucifer_Engine/lucifer_engine/__init__.py
git hash-object ENGINE_HUB/00_PLANET_LAYER/Lucifer_Engine/lucifer_engine/impact_estimator.py
git hash-object ENGINE_HUB/00_PLANET_LAYER/Lucifer_Engine/lucifer_engine/__main__.py
git hash-object ENGINE_HUB/00_PLANET_LAYER/Lucifer_Engine/README.md
git hash-object ENGINE_HUB/00_PLANET_LAYER/Lucifer_Engine/pyproject.toml
git hash-object ENGINE_HUB/00_PLANET_LAYER/Lucifer_Engine/requirements.txt
```

아래 표의 값과 일치해야 합니다.

| 파일 | git hash-object (blob SHA1) |
|------|-----------------------------|
| `lucifer_engine/__init__.py` | `8428b73e9b2510f4deb7a80b88427b10f9e22649` |
| `lucifer_engine/impact_estimator.py` | `343b8306475c998cefa744c95196e663b0558a4b` |
| `lucifer_engine/__main__.py` | `dc296c04f528b9d77068bf80f54d65eea996d8a0` |
| `README.md` | `d89006cdceeabdb41a97f255e5ba79b99dbab274` |
| `pyproject.toml` | `08e5f41368433526cdb289d54b2e53ccb91fc6da` |
| `requirements.txt` | `20a24e6efec4d042aa12ecfa21175d1548cb42f9` |

검증 시 위 명령을 다시 실행해 같은 SHA1 이 나오면, 해당 시점 이후로 파일이 변경되지 않았음을 의미합니다.
