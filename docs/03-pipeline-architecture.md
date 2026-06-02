# 배치 파이프라인 설계

## 전체 흐름

```text
Source Registry
  -> Collection Jobs
  -> Raw Evidence Store
  -> Normalization
  -> Entity Resolution
  -> Signal Extraction
  -> Opportunity Generation
  -> Research Scoring
  -> Report Builder
  -> Human Review
  -> Harness Feedback
```

## 1. Source Registry

조사 가능한 소스를 등록하고, 각 소스의 수집 방식과 제약을 명시합니다.

필드 예시:

- source_id
- source_type: app_store, review, trend, community, freelance, keyword, paid_intel
- access_method: api, export, crawler, manual_upload
- legal_status: allowed, restricted, manual_only, excluded
- refresh_cycle
- rate_limit
- reliability
- cost

기본 정책:

- 무료 소스와 무료 티어를 우선한다.
- 유료 데이터 소스는 초기 범위에서 제외한다.
- API와 공식 export가 있으면 우선 검토한다.
- 크롤러는 허용 여부, robots/약관, 요청량, 데이터 민감도를 확인한 뒤 제한적으로 검토한다.

## 2. Collection Jobs

초기 수집 잡은 다음 범위로 시작합니다.

- Google Play 앱 메타데이터와 리뷰
- Google Trends/키워드 신호
- Reddit/커뮤니티 문제 신호
- 외주의뢰 게시판의 반복 요청 유형
- 경쟁앱 스토어 설명과 가격 구조

각 수집 결과는 원문을 보존하고, 추출 결과와 분리 저장합니다.

초기 구현은 실제 수집 잡보다 오프라인 하네스를 먼저 만듭니다. 수집기는 하네스에서 검증한 스키마와 평가 기준을 만족한 뒤 붙입니다.

## 3. Raw Evidence Store

모든 근거는 변환 전 원본을 남깁니다.

필드 예시:

- evidence_id
- source_id
- collected_at
- url_or_locator
- raw_text_or_payload
- language
- country
- terms_snapshot
- content_hash

## 4. Normalization

소스별 데이터를 공통 스키마로 맞춥니다.

- 앱
- 리뷰
- 키워드
- 문제 문장
- 구매/외주 요청
- 커뮤니티 게시글
- 가격/수익화 정보

## 5. Entity Resolution

서로 다른 소스에서 같은 앱, 같은 문제, 같은 사용자군을 가리키는 항목을 연결합니다.

예:

- `PDF converter`, `HTML to PDF`, `webpage to PDF`를 하나의 문제 클러스터로 묶음
- 동일 앱의 국가별 Play Store 페이지를 하나의 앱 엔티티로 묶음
- 같은 불만 표현을 pain point 클러스터로 묶음

## 6. Signal Extraction

LLM과 규칙 기반 추출을 함께 사용합니다.

추출 대상:

- pain point
- target user
- job-to-be-done
- current workaround
- willingness-to-pay hint
- retention trigger
- monetization pattern
- policy risk
- MVP feature candidate

LLM 출력은 반드시 JSON 스키마 검증을 통과해야 하며, 출처 evidence_id를 포함해야 합니다.

## 7. Opportunity Generation

문제 클러스터를 앱 기회 후보로 변환합니다.

생성 규칙:

- 단일 목적 앱으로 표현 가능해야 함
- 예상 입력과 결과가 명확해야 함
- 최소 2개 이상의 근거 소스가 있어야 함
- 금지/고위험 카테고리는 제외 또는 보류

## 8. Research Scoring

점수는 deterministic feature와 LLM judgment를 분리합니다.

Deterministic feature 예:

- 리뷰 수
- 최근 리뷰 빈도
- 평점 분포
- 키워드 트렌드 변화율
- 경쟁앱 수
- 유료/구독 경쟁앱 존재 여부

LLM judgment 예:

- 불만의 본질 분류
- MVP 절단 가능성
- 차별화 내러티브
- 구독 가치 판단

## 9. Report Builder

매일 보고서는 다음 구조를 가집니다.

- Executive Summary
- Top Opportunities
- Watchlist
- Rejected Candidates
- Evidence Appendix
- Methodology Notes
- Harness Quality Report

각 상위 후보는 다음을 포함합니다.

- 한 줄 기회 정의
- 타깃 사용자
- 문제와 사용 장면
- 근거 요약
- 수익화 가정
- 경쟁앱 빈틈
- 2주 MVP 범위
- 리스크
- 다음 검증 액션

## 10. Human Review

사람의 리뷰는 데이터로 저장합니다.

- accept/reject/hold
- 수정된 문제 정의
- 잘못된 추출 표시
- 놓친 소스
- 점수 조정 사유
- 실제 실행 여부

## 11. 저장소 초안

초기 구현은 저비용을 우선합니다.

- PostgreSQL 또는 SQLite: 구조화 데이터
- Object storage 또는 로컬 파일: 원문 스냅샷
- Markdown/HTML: 일일 보고서
- Git: 방법론과 프롬프트 버전 관리
