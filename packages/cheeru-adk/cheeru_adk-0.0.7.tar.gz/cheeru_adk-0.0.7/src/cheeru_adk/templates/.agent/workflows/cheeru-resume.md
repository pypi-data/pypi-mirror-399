---
description: 🔄 세션 재개 및 컨텍스트 복원
---

# Session Resume Workflow

이전 세션의 작업 상태를 복원하고, 이어서 작업할 수 있도록 컨텍스트를 로드합니다.

## Step 1: 컨텍스트 로드

Use the `context-manager` agent to:
- `.cheeru/active_context.md` 파일 로드
- 현재 진행 중인 Phase/Task 확인
- 마지막 작업 내용 요약

## Step 2: 상태 요약 출력

사용자에게 다음 정보 제공:
- 현재 작업 중인 항목
- 진행률 (%)
- 블로커 (있는 경우)
- 다음 단계 제안

## Step 3: 작업 재개

사용자 선택에 따라:
- `/cheeru-code` - 코드 작성 계속
- `/cheeru-plan` - 계획 수정
- `/cheeru-doc` - 문서화 진행

## Step 4: 세션 종료 시

작업 완료 후:
- 변경사항 `active_context.md`에 기록
- 다음 세션을 위한 요약 저장
