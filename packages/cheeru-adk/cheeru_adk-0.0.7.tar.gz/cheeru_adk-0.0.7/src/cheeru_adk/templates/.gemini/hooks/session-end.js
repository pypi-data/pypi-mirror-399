#!/usr/bin/env node
/**
 * CheerU-ADK Session End Hook
 * 
 * Saves session learnings and progress for future reference.
 * - Records completed tasks
 * - Saves TDD cycle summary
 * - Updates project memory
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

function summarizeSession(sessionData) {
    const summary = {
        timestamp: new Date().toISOString(),
        duration: 'unknown',
        highlights: [],
    };

    // Extract key actions from session
    if (sessionData.tool_calls) {
        const toolCounts = {};
        for (const call of sessionData.tool_calls) {
            const tool = call.name || 'unknown';
            toolCounts[tool] = (toolCounts[tool] || 0) + 1;
        }
        summary.toolUsage = toolCounts;
    }

    return summary;
}

async function main() {
    try {
        const input = JSON.parse(await readStdin());
        const projectDir = process.env.GEMINI_PROJECT_DIR || process.cwd();
        const cheeruDir = path.join(projectDir, '.cheeru');

        // Ensure .cheeru directory exists
        if (!fs.existsSync(cheeruDir)) {
            fs.mkdirSync(cheeruDir, { recursive: true });
        }

        // Load session history
        const historyPath = path.join(cheeruDir, 'session_history.json');
        let history = [];
        if (fs.existsSync(historyPath)) {
            history = JSON.parse(fs.readFileSync(historyPath, 'utf8'));
        }

        // Create session summary
        const sessionSummary = summarizeSession(input);

        // Load TDD state if exists
        const tddStatePath = path.join(cheeruDir, 'tdd_state.json');
        if (fs.existsSync(tddStatePath)) {
            const tddState = JSON.parse(fs.readFileSync(tddStatePath, 'utf8'));
            sessionSummary.tddState = {
                phase: tddState.phase,
                feature: tddState.feature,
                status: tddState.status,
            };
        }

        // Add to history (keep last 20 sessions)
        history = [...history.slice(-19), sessionSummary];
        fs.writeFileSync(historyPath, JSON.stringify(history, null, 2));

        // Update active context with learnings
        const activeContextPath = path.join(cheeruDir, 'active_context.md');
        let contextContent = '';
        if (fs.existsSync(activeContextPath)) {
            contextContent = fs.readFileSync(activeContextPath, 'utf8');
        }

        // Append session note
        const sessionNote = `\n\n## Session ${new Date().toLocaleDateString('ko-KR')}\n- TDD Phase: ${sessionSummary.tddState?.phase || 'N/A'}\n- Feature: ${sessionSummary.tddState?.feature || 'N/A'}\n`;

        // Only append if not already present (prevent duplicates)
        if (!contextContent.includes(sessionNote.trim())) {
            fs.appendFileSync(activeContextPath, sessionNote);
        }

        const output = {
            decision: "allow",
            hookSpecificOutput: {
                hookEventName: "SessionEnd",
                additionalContext: `📝 CheerU-ADK: Session saved. TDD: ${sessionSummary.tddState?.phase || 'N/A'}`
            }
        };

        console.log(JSON.stringify(output));
    } catch (error) {
        console.log(JSON.stringify({
            decision: "allow",
            hookSpecificOutput: {
                hookEventName: "SessionEnd",
                additionalContext: `CheerU-ADK Session End: ${error.message}`
            }
        }));
    }
}

main();
