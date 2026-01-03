---
description: 🐙 GitHub에 변경사항 커밋
---

# GitHub 커밋

현재 변경사항을 GitHub에 커밋합니다.

## Step 1: 사전 확인

GitHub 레포가 없는 경우:
- 레포 생성 여부 확인
- GitHub Personal Access Token 요청

## Step 2: 변경사항 확인

1. `git status`로 변경된 파일 확인
2. 현재 진행 중인 Phase 확인 (`.cheeru/plan.json`)

## Step 3: 커밋

Use the github-manager agent to:

커밋 메시지 형식:
```
[Phase X.X] Phase 제목

- 생성된 파일 목록
- 구현된 기능 설명
```

### 실행 명령어

// turbo
```bash
git add .
```

// turbo  
```bash
git commit -m "[Phase X.X] 커밋 메시지"
```

// turbo
```bash
git push origin main
```

## Step 4: Phase 완료 처리

커밋 성공 시:
1. `.cheeru/plan.json`에서 해당 Phase status를 `"completed"`로 변경
2. 다음 Phase가 있으면 안내

## Step 5: 다음 단계

- `/cheeru-code` - 다음 Phase 코드 생성
- `/cheeru-doc` - Notion 문서화 (모든 Phase 완료 시)
