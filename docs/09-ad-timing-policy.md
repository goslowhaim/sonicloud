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
- `FakeAdAdapter.maybe_show(context) -> AdDecision`

이 모듈은 실제 광고 SDK를 사용하지 않습니다. Android 구현 단계에서 AdMob, AppLovin, Meta, Unity 같은 SDK 어댑터를 붙일 때 정책 레이어를 그대로 재사용하는 것을 목표로 합니다.

## 다음 구현 후보

- Android/Kotlin 포팅
- 광고 포맷별 세부 정책
- 앱 카테고리별 정책 preset
- 정책 로그 수집
- A/B 테스트용 decision reason 집계
