---
description: 📋 프로젝트 계획 및 PRD 생성 (Spec-First)
---

# Phase 2: Spec-First Planning

사용자의 요구사항을 분석하여 상세한 기술 명세(PRD)와 프로젝트 로드맵을 수립합니다.

## Step 1: 프로젝트 구상 및 요구사항 분석

Use the `portfolio-planner` agent to:
- 사용자 인터뷰 (Context Gathering)
- 시장 트렌드 분석 및 기술 스택 선정
- 핵심 기능(Core Features) 및 차별점(Hook) 정의

## Step 2: PRD (Product Requirement Document) 생성

Use the `portfolio-planner` agent to:
- `README.md` (Project Overview) 작성
- `specs/phase-1.md` (Phase 1 상세 명세) 작성
- `.cheeru/plan.json` (기계 판독용 로드맵) 생성

## Step 3: 프로젝트 관리 체계 수립 (GitHub Issues)

Use the `project-manager` agent to:
- `.cheeru/plan.json`의 Task를 GitHub Issue로 변환
- 우선순위(Priority) 및 라벨(Label) 지정
- Milestone 생성 및 할당

## Step 4: 문서화 초기화 (Notion)

Use the `notion-documenter` agent to:
- Notion 대시보드 페이지 생성
- GitHub Issue와 Notion 페이지 연동 준비

## Step 5: 사용자 검토

- 생성된 PRD와 Plan을 사용자에게 제시하고 승인 요청
- 승인 시 `/cheeru-start` 또는 `/cheeru-code`로 구현 시작
