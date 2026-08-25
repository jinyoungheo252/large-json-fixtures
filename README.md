# large-json-fixtures

다양한 크기의 JSON 픽스처와 · 그 파일의 다운로드 주소를 담은 목(mock) 응답 모음.
데이터는 전부 무작위 생성한 합성 데이터다.

## 구성

- `api/{규모}.json` — 목 응답. 데이터 본문 없이 `download_url` 과 검증값만 담는다.
- 릴리스 자산 `{규모}.json` — 실제 데이터 파일. Releases 에 첨부되어 있다.

## 규모

| 규모 | 행 수 | 크기 |
|---|---|---|
| S | 1,000 | ~0.5 MB |
| M | 10,000 | ~5 MB |
| L | 100,000 | ~50 MB |
| XL | 500,000 | ~250 MB |

## 데이터 형식

```json
{"status": "OK", "rows": 1000, "data": [
  {"id": 1, "token": "a3f9c2e1", "values": ["...", "..."], "n": 48213}
]}
```

각 행의 `id` 는 1부터 연속이며 · `token` 은 8자리 16진수 난수다. 내려받은 파일이 온전한지
행 단위로 확인할 수 있다.

## 생성

```bash
python3 scripts/generate.py S --owner <owner> --tag v1
```
