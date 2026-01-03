---
description: 🎫 Plan Task를 GitHub Issue로 변환
---

# GitHub Issue Synchronization

`.cheeru/plan.json`의 Task들을 실제 GitHub Issue로 변환하여 체계적인 관리를 시작합니다.

## Step 1: Plan 로드

Use the `project-manager` agent to:
- `.cheeru/plan.json` 파일 로드
- 현재 Phase의 Task 목록 확인

## Step 2: GitHub Issue 생성

Use the `project-manager` agent to:
- 각 Task에 대해 `gh issue create` 명령 생성 및 실행
- **Title**: `[Type] Task Name` 형식 적용
- **Body**: 상세 요구사항 및 Acceptance Criteria 포함
- **Label**: `phase-1`, `backend/frontend` 등 적절한 라벨 적용

## Step 3: 메타데이터 동기화

Use the `project-manager` agent to:
- 생성된 Issue ID 및 URL을 `.cheeru/plan.json`에 기록
- `status`를 `pending` -> `tracked`로 업데이트

## Step 4: 결과 보고

- 생성된 이슈 목록과 링크를 사용자에게 보고
