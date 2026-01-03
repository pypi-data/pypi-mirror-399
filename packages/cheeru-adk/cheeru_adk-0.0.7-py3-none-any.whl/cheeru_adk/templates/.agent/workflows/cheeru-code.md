---
description: 💻 현재 Phase 코드 생성 (w/ Review & Test)
---

# Phase 코드 생성 및 검증

`.cheeru/plan.json`의 다음 pending Phase에 대해 코드 생성, 리뷰, 테스트를 수행합니다.

## Step 1: 현재 진행 상황 확인

1. `.cheeru/plan.json` 읽기
2. `status: "pending"` 인 첫 번째 Phase 확인
3. 해당 Phase의 tasks 목록 확인

## Step 2: 코드 생성 (Draft)

Use the code-generator agent to:
- 해당 Phase에 필요한 파일들 초안 생성
- 소스 코드 파일 (src/)
- 기본 테스트 코드 파일 (tests/)

## Step 3: 코드 리뷰 (Code Review)

Use the code-reviewer agent to:
- 생성된 코드의 정적 분석 및 보안 점검
- 스타일 가이드 준수 여부 확인
- **Fail** 시 Step 2로 돌아가 수정 요청

## Step 4: 테스트 (TDD Verification)

Use the test-engineer agent to:
- 단위 테스트 실행
- 테스트 실패 시 원인 분석
- **Fail** 시 Step 2로 돌아가 수정 요청

## Step 5: 최종 확정

1. 모든 검증(리뷰, 테스트) 통과 시 파일 확정
2. `.cheeru/plan.json`에서 해당 Phase status를 `"in_progress"`로 변경
3. 생성된 파일 목록 표시

## Step 6: 다음 단계 안내

- `/cheeru-commit` - 검증된 코드를 GitHub에 커밋
- `/cheeru-code` - 다음 Phase 진행
