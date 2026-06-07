# 광고 타이밍 정책 모듈

## 목적

첫 `pursue` 산출물은 앱이 아니라 광고형 Android 유틸 앱을 반복 출시하기 위한 공통 모듈입니다.

문서, QR, 파일 유틸 앱 조사에서 반복적으로 확인된 리스크는 광고 자체가 아니라 잘못된 광고 타이밍입니다. 작업 도중, 저장 전, 공유 직전, 오류 화면에서 전면 광고가 나오면 사용자 신뢰와 앱 품질이 빠르게 무너집니다.

## 정책 원칙

- 사용자의 핵심 작업이 끝나기 전에는 전면 광고를 막는다.
- 입력, 처리 중, 오류 화면에서는 광고를 막는다.
- 저장되지 않은 작업이 있으면 광고를 막는다.
- 첫 세션 초반에는 광고를 막는다.
- 광고 간 최소 간격을 둔다.
- 결과 저장, 공유 완료, 작업 종료처럼 방해가 적은 이벤트에서만 허용한다.

## 구현 위치

- `src/sonicloud_harness/ad_policy.py`
- `tests/test_ad_policy.py`

## 현재 API

- `AdTimingPolicy.decide(context) -> AdDecision`
- `AdTimingPolicy.for_category(category) -> AdTimingPolicy`
- `FakeAdAdapter.maybe_show(context) -> AdDecision`

이 모듈은 실제 광고 SDK를 사용하지 않습니다. Android 구현 단계에서 AdMob, AppLovin, Meta, Unity 같은 SDK 어댑터를 붙일 때 정책 레이어를 그대로 재사용하는 것을 목표로 합니다.

## 다음 구현 후보

- Android/Kotlin 포팅
- 정책 로그 수집
- A/B 테스트용 decision reason 집계

## 카테고리 preset

현재 preset은 다음 카테고리를 지원합니다.

| 카테고리 | 정책 방향 |
| --- | --- |
| `document_scanner` | 저장/공유 후에만 보수적으로 허용. 공유 화면 자체는 차단. |
| `pdf_converter` | 결과 생성/저장/공유 후 허용. 기본 정책과 유사. |
| `qr_scanner` | 카메라/URL 신뢰 리스크 때문에 쿨다운을 길게 두고 공유 화면 차단. |
| `file_manager` | 파일 접근 권한 민감도가 높아 결과/공유 화면도 차단. 설정/종료 이벤트 위주 허용. |

## 시뮬레이션

앱 플로우를 JSONL로 넣으면 정책 결정 로그를 Markdown으로 렌더링할 수 있습니다.

```bash
PYTHONPATH=src python3 -m sonicloud_harness.cli simulate-ads \
  --category document_scanner \
  --flow samples/ad_flows.document_scanner.seed.jsonl \
  --output reports/ad-simulation.document-scanner.md
```

샘플 플로우:

- `samples/ad_flows.document_scanner.seed.jsonl`
- `samples/ad_flows.qr_scanner.seed.jsonl`
- `samples/ad_flows.file_manager.seed.jsonl`
