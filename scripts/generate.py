#!/usr/bin/env python3
"""목 데이터 생성 스크립트.

규모별 합성 JSON 을 out/ 에 만들고 · sha256·행 수를 계산해 api/{규모}.json 에 주입한다.
표준 라이브러리만 사용 · pip 불필요.

    python3 scripts/generate.py S --owner <owner> --tag v1
    python3 scripts/generate.py S M L XL --owner <owner> --tag v1
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import string
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
API = ROOT / "api"

# 규모 → 행 수. 크기는 행당 ~500B 기준.
SIZES = {"S": 1_000, "M": 10_000, "L": 50_000, "XL": 500_000}

REPO = "large-json-fixtures"
HEX = "0123456789abcdef"
WORDCHARS = string.ascii_lowercase + string.digits


def make_row(rng: random.Random, i: int) -> dict:
    """행 하나. id 는 1부터 연속 · token 은 8자리 16진수 난수.

    values 는 행당 ~500B 를 맞추기 위한 채움값 · 의미 없음.
    """
    return {
        "id": i,
        "token": "".join(rng.choice(HEX) for _ in range(8)),
        "values": ["".join(rng.choice(WORDCHARS) for _ in range(24)) for _ in range(14)],
        "n": rng.randint(1, 999_999),
    }


def write_data(size: str, rows: int, seed: int) -> Path:
    """out/{size}.json 을 스트리밍으로 쓴다 (메모리에 전체를 올리지 않는다)."""
    rng = random.Random(seed)
    path = OUT / f"{size}.json"
    with path.open("w", encoding="utf-8") as f:
        f.write('{"status":"OK","rows":%d,"data":[' % rows)
        for i in range(1, rows + 1):
            if i > 1:
                f.write(",")
            json.dump(make_row(rng, i), f, separators=(",", ":"))
        f.write("]}")
    return path


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser(description="목 데이터 생성")
    ap.add_argument("sizes", nargs="+", choices=list(SIZES), help="생성할 규모")
    ap.add_argument("--owner", required=True, help="GitHub owner (download_url 조립용)")
    ap.add_argument("--tag", default="v1", help="릴리스 태그 (기본 v1)")
    ap.add_argument("--seed", type=int, default=42, help="난수 시드 (재현용)")
    args = ap.parse_args()

    OUT.mkdir(exist_ok=True)
    API.mkdir(exist_ok=True)

    for size in args.sizes:
        rows = SIZES[size]
        data_path = write_data(size, rows, args.seed)
        digest = sha256_of(data_path)
        mb = data_path.stat().st_size / 1024 / 1024

        # 목 응답 · 데이터 본문 없이 주소와 검증값만 담는다.
        response = {
            "status": "OK",
            "rows": rows,
            "bytes": data_path.stat().st_size,
            "sha256": digest,
            "download_url": (
                f"https://github.com/{args.owner}/{REPO}"
                f"/releases/download/{args.tag}/{size}.json"
            ),
        }
        api_path = API / f"{size}.json"
        api_path.write_text(json.dumps(response, indent=2) + "\n", encoding="utf-8")

        print(f"{size}: {rows:,}행 · {mb:.2f} MB · sha256 {digest[:12]}…")
        print(f"    {data_path.relative_to(ROOT)} → {api_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
