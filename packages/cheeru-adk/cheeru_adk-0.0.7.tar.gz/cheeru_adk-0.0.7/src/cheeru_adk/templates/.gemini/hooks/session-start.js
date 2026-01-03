#!/usr/bin/env node
/**
 * CheerU-ADK Session Start Hook
 * 
 * Automatically loads project context when a Gemini CLI session starts.
 * - Loads active_context.md
 * - Detects current SPEC status
 * - Identifies TDD phase
 */

const fs = require('fs');
const path = require('path');

async function readStdin() {
    const chunks = [];
    for await (const chunk of process.stdin) {
        chunks.push(chunk);
    }
    return Buffer.concat(chunks).toString('utf8');
}

async function main() {
    try {
        const input = JSON.parse(await readStdin());
        const projectDir = process.env.GEMINI_PROJECT_DIR || process.cwd();

        let additionalContext = [];

        // 1. Load active_context.md if exists
        const activeContextPath = path.join(projectDir, '.cheeru', 'active_context.md');
        if (fs.existsSync(activeContextPath)) {
            const contextContent = fs.readFileSync(activeContextPath, 'utf8');
            additionalContext.push(`## 📋 Active Context\n${contextContent}`);
        }

        // 2. Check for current SPEC
        const specsDir = path.join(projectDir, '.cheeru', 'specs');
        if (fs.existsSync(specsDir)) {
            const specs = fs.readdirSync(specsDir).filter(f => f.startsWith('SPEC-'));
            if (specs.length > 0) {
                additionalContext.push(`## 📄 Active SPECs: ${specs.join(', ')}`);
            }
        }

        // 3. Check TDD state
        const tddStatePath = path.join(projectDir, '.cheeru', 'tdd_state.json');
        if (fs.existsSync(tddStatePath)) {
            const tddState = JSON.parse(fs.readFileSync(tddStatePath, 'utf8'));
            additionalContext.push(`## 🔄 TDD State: ${tddState.phase || 'unknown'} - ${tddState.feature || 'No active feature'}`);
        }

        // 4. Load GEMINI.md context file
        const geminiContextPath = path.join(projectDir, '.agent', 'context', 'GEMINI.md');
        if (fs.existsSync(geminiContextPath)) {
            additionalContext.push(`## 🤖 Project Context loaded from GEMINI.md`);
        }

        const output = {
            decision: "allow",
            hookSpecificOutput: {
                hookEventName: "SessionStart",
                additionalContext: additionalContext.length > 0
                    ? additionalContext.join('\n\n')
                    : "CheerU-ADK session initialized. No active context found."
            }
        };

        console.log(JSON.stringify(output));
    } catch (error) {
        console.log(JSON.stringify({
            decision: "allow",
            hookSpecificOutput: {
                hookEventName: "SessionStart",
                additionalContext: `CheerU-ADK: Session start error - ${error.message}`
            }
        }));
    }
}

main();
