# 개발 로드맵

## Phase 0. 기획 확정

목표:

- Grill Me 질문 답변 수집
- 조사 대상과 제외 카테고리 확정
- 서치 테마와 집중 테마의 보고서 포맷 분리
- 초기 데이터 소스 확정
- 점수 가중치 초안 확정
- 일일 보고서 포맷 확정

산출물:

- PRD v0.1
- 데이터 소스 정책
- 기회 후보 스키마
- 점수표 v0.1
- 운영 모드 스펙

## Phase 1. Offline Research Harness

목표:

- 실제 크롤러 없이 샘플 데이터로 조사 로직과 하네스를 먼저 만든다.

기능:

- evidence 스키마
- opportunity 스키마
- 수동 업로드 샘플
- LLM 추출 JSON 검증
- 점수 계산기
- Markdown 보고서 생성
- 골든셋 평가

완료 기준:

- 샘플 evidence 50개 이상 처리
- 골든셋 20개 이상 평가
- 보고서 1개 생성
- 스키마/근거 검증 실패가 CI에서 잡힘

## Phase 2. Source Collection MVP

목표:

- 약관과 접근성이 명확한 소스부터 자동 수집한다.

기능:

- Source Registry
- collection job runner
- raw evidence 저장
- 중복 제거
- 수집 실패 재시도
- 수집 상태 리포트

우선 소스:

- Google Play 앱/리뷰 데이터 접근 방식 확정
- Google Trends 또는 키워드 데이터
- 수동 CSV/JSON 업로드
- 허용 가능한 커뮤니티/API 소스

완료 기준:

- 매일 동일 시간 실행
- 실패 소스가 있어도 부분 보고서 생성
- evidence 원문과 추출 결과 분리 저장

## Phase 3. Opportunity Engine

목표:

- 문제 신호를 앱 기회 후보로 변환한다.

기능:

- pain point clustering
- app/category/entity resolution
- JTBD extraction
- monetization fit classifier
- MVP feasibility classifier
- risk classifier
- opportunity scoring

완료 기준:

- 하루 후보 20개 이상 생성
- 상위 후보 5개 상세 분석
- 탈락 후보와 탈락 사유 기록

## Phase 4. Report Product

목표:

- 매일 읽고 실행할 수 있는 보고서를 만든다.

기능:

- daily report Markdown/HTML
- search theme report
- focus theme report
- evidence appendix
- watchlist
- rejected candidates
- mini PRD draft
- next action generator

완료 기준:

- 보고서가 10분 내 검토 가능
- 서치 테마는 매일 후보 10개와 상위 후보 상세 분석을 제공
- 집중 테마는 지정 주제의 2주 추적 로그와 일일 변화 요약을 제공
- 후보별 다음 작업이 명확함
- 출처 없는 주장이 없음

## Phase 5. Continuous Improvement Harness

목표:

- 파이프라인 변경이 품질을 개선했는지 측정한다.

기능:

- golden set runner
- ranking regression
- grounding checker
- report rubric evaluator
- experiment tracking
- human feedback ingestion

완료 기준:

- 주요 변경 전후 품질 비교 가능
- 회귀 발생 시 배포 차단 가능
- 사람 리뷰가 다음 평가 데이터로 누적됨

## Phase 6. App Experiment Loop

목표:

- 조사 결과가 실제 앱 출시 사이클로 이어지게 한다.

기능:

- 상위 후보 -> 1-page PRD
- 화면 목록
- MVP 작업 단위
- 스토어 리스팅 초안
- 수익화 가정
- 출시 후 지표 입력
- 조사 점수와 실제 성과 백테스트

완료 기준:

- 2-3주 단위 앱 실험 1개 실행
- 출시/미출시/보류 결과가 리서치 DB에 환류
- 다음 후보 선정 기준이 개선됨

## 권장 초기 기술 스택

초기에는 운영비와 복잡도를 낮춥니다.

- Python: 배치, 추출, 평가, 보고서 생성
- SQLite 또는 PostgreSQL: 구조화 데이터
- Pydantic: 스키마 검증
- Prefect 또는 Dagster: 파이프라인 오케스트레이션
- Playwright/API clients: 허용된 소스 수집
- Markdown + static HTML: 보고서
- pytest: 하네스 테스트
- GitHub Actions 또는 VPS cron: 일일 실행

## 첫 구현 순서

1. 샘플 evidence 스키마와 opportunity 스키마 작성
2. 수동 샘플 데이터 20-50개 준비
3. 추출기 인터페이스 작성
4. 점수 계산기 작성
5. 보고서 템플릿 작성
6. 골든셋 평가기 작성
7. 첫 데이터 소스 커넥터 추가
