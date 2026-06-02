# 하네스 엔지니어링 계획

## 목적

하네스는 "보고서가 그럴듯한가"가 아니라 "조사 파이프라인이 이전보다 실제로 나아졌는가"를 검증합니다.

## 평가 대상

1. 수집 품질
2. 추출 품질
3. 클러스터링 품질
4. 기회 후보 생성 품질
5. 점수화 품질
6. 보고서 품질
7. 실제 실행 성과와의 연결성

## 골든셋

초기 골든셋은 사람이 직접 만든 소규모 기준 데이터로 시작합니다.

예시:

- 성공한 소형 안드로이드 앱 사례
- 실패했거나 수익화가 어려웠던 앱 사례
- 경쟁앱 리뷰에서 명확한 pain point가 있는 사례
- 겉보기에는 좋아 보이지만 정책/수익화상 부적합한 사례
- 해외 검증 후 한국 로컬라이즈 가능성이 있는 사례

각 사례에는 다음 라벨을 붙입니다.

- valid_opportunity: yes/no/uncertain
- demand_strength
- monetization_fit
- mvp_feasibility
- competitive_gap
- risk_level
- expected_decision: pursue/watch/reject
- rationale

## 자동 평가

### Schema Validity

LLM 추출 결과가 스키마를 지키는지 검사합니다.

- 필수 필드 누락
- evidence_id 누락
- 허용되지 않은 enum
- 근거 없는 결론

### Evidence Grounding

각 결론이 실제 근거와 연결되는지 검사합니다.

- 보고서 문장 -> evidence_id 연결
- evidence 원문에 없는 주장 탐지
- 출처 다양성 측정

### Ranking Regression

기존 골든셋에서 좋은 후보가 상위에 유지되는지 확인합니다.

- top-k recall
- pairwise ranking accuracy
- reject 후보가 상위로 올라온 비율

### Consistency

같은 입력에 대해 결과가 크게 흔들리는지 확인합니다.

- 동일 데이터 재실행 점수 분산
- 프롬프트/모델 변경 전후 차이
- 요약 문장과 점수 간 불일치

### Report Quality Rubric

보고서 품질은 다음 기준으로 평가합니다.

- 결론이 명확한가?
- 근거가 충분한가?
- 반증 신호가 포함됐는가?
- 다음 액션이 실행 가능한가?
- 과장된 표현이 없는가?
- 2주 MVP 범위가 현실적인가?

## 사람 평가

매일 전체를 보지 않고 샘플링합니다.

- 상위 후보 3개 전수 검수
- 보류/탈락 후보 중 랜덤 5개 검수
- 추출 결과 중 evidence grounding 오류 샘플 검수

리뷰 결과는 다음 날 평가 데이터로 들어갑니다.

## 실험 관리

파이프라인 변경은 실험 단위로 기록합니다.

- experiment_id
- changed_component
- hypothesis
- before_metric
- after_metric
- decision: ship/revert/iterate

예:

- 리뷰 불만 추출 프롬프트 변경
- Google Trends 가중치 조정
- 유료앱 존재 여부를 수익화 점수에 추가
- 리스크 패널티 강화

## 장기 백테스트

실제 출시 또는 수동 검토 결과가 쌓이면 다음을 측정합니다.

- 상위 점수 후보가 실제 선택된 비율
- 선택 후보의 MVP 완성률
- 출시 후 초기 설치/유지/수익 지표
- 조사 점수와 실제 성과의 상관
- 실패 후에도 재사용 모듈이 남은 비율

## 하네스 산출물

매일 보고서 끝에 다음을 포함합니다.

- 오늘 수집 성공/실패 소스
- 스키마 오류 수
- 근거 연결 오류 수
- 골든셋 회귀 결과
- 전일 대비 점수 분포 변화
- 사람이 확인해야 할 품질 경고
