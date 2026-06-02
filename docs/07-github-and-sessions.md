# GitHub 및 세션 운영

## 현재 확인된 상태

- GitHub MCP 인증 계정: `goslowhaim`
- 설치 계정: `goslowhaim`
- 접근 가능한 저장소:
  - `goslowhaim/mybed`
  - `goslowhaim/mybed_public`
  - `goslowhaim/sonicloud`

프로젝트 연결 대상 저장소는 `goslowhaim/sonicloud`입니다.

## 권장 저장소 운영

이 프로젝트는 현재 `goslowhaim/sonicloud` public repo에 연결합니다.

주의:

- public repo이므로 실제 사업 아이디어, 유료 데이터, API 키, 비공개 리서치 원문은 올리지 않습니다.
- 민감한 후보 데이터가 쌓이기 시작하면 private repo 또는 private storage로 분리하는 편이 안전합니다.

## 모바일 세션에서 보는 방법

현재 모바일 세션이 개인 로컬 맥 환경과 연결되어 있다면, 이 `/home/ubuntu/project` 워크스페이스 자체를 그대로 모바일 세션에서 보는 직접적인 방법은 제한적입니다.

현실적인 방법은 GitHub를 공통 동기화 지점으로 쓰는 것입니다.

1. 이 환경의 문서를 `goslowhaim/sonicloud`에 업로드
2. 맥 로컬 환경에서 `sonicloud` repo clone 또는 pull
3. 모바일 세션에서는 맥 환경을 통해 같은 repo 내용을 확인

주의:

- `sonicloud`는 public repo이므로 민감 데이터는 올리지 않습니다.
- 실제 후보 DB, API 키, 유료 데이터 원문은 private 저장소나 별도 storage로 분리합니다.

대안:

- 현재 문서를 gist나 기존 private repo에 임시 업로드
- `mybed` 같은 기존 private repo 안에 임시 폴더로 업로드
- 최종 저장소를 만든 뒤 해당 위치로 이전
