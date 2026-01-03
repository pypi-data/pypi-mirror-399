#!/usr/bin/env node
/**
 * CheerU-ADK TDD Detector Hook (AfterModel)
 * 
 * Automatically detects TDD state from model responses and updates tracking.
 * - Detects test execution results
 * - Tracks RED/GREEN/REFACTOR phases
 * - Updates TDD state file
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

function detectTDDPhase(responseText) {
    const text = responseText.toLowerCase();

    // Detect test results
    if (text.includes('passed') && text.includes('test')) {
        if (text.includes('refactor') || text.includes('리팩토링')) {
            return { phase: 'refactor', status: 'passed' };
        }
        return { phase: 'green', status: 'passed' };
    }

    if (text.includes('failed') && text.includes('test')) {
        return { phase: 'red', status: 'failed' };
    }

    if (text.includes('error') && text.includes('test')) {
        return { phase: 'red', status: 'error' };
    }

    // Detect phase keywords
    if (text.includes('red phase') || text.includes('🔴')) {
        return { phase: 'red', status: 'active' };
    }

    if (text.includes('green phase') || text.includes('🟢')) {
        return { phase: 'green', status: 'active' };
    }

    if (text.includes('refactor phase') || text.includes('🔵')) {
        return { phase: 'refactor', status: 'active' };
    }

    return null;
}

function extractFeatureName(responseText) {
    // Try to extract feature name from common patterns
    const patterns = [
        /feature[:\s]+['""]?([^'""\\n]+)['""]?/i,
        /implementing[:\s]+['""]?([^'""\\n]+)['""]?/i,
        /testing[:\s]+['""]?([^'""\\n]+)['""]?/i,
        /tdd.*for[:\s]+['""]?([^'""\\n]+)['""]?/i,
    ];

    for (const pattern of patterns) {
        const match = responseText.match(pattern);
        if (match) {
            return match[1].trim().slice(0, 50);
        }
    }

    return null;
}

async function main() {
    try {
        const input = JSON.parse(await readStdin());
        const projectDir = process.env.GEMINI_PROJECT_DIR || process.cwd();

        // Get model response
        const modelResponse = input.model_response || '';
        const responseText = typeof modelResponse === 'string'
            ? modelResponse
            : JSON.stringify(modelResponse);

        const detected = detectTDDPhase(responseText);

        if (detected) {
            const tddStatePath = path.join(projectDir, '.cheeru', 'tdd_state.json');
            const cheeruDir = path.join(projectDir, '.cheeru');

            // Ensure .cheeru directory exists
            if (!fs.existsSync(cheeruDir)) {
                fs.mkdirSync(cheeruDir, { recursive: true });
            }

            // Load existing state
            let tddState = {};
            if (fs.existsSync(tddStatePath)) {
                tddState = JSON.parse(fs.readFileSync(tddStatePath, 'utf8'));
            }

            // Update state
            const feature = extractFeatureName(responseText) || tddState.feature || 'Unknown';
            tddState = {
                ...tddState,
                phase: detected.phase,
                status: detected.status,
                feature: feature,
                lastUpdated: new Date().toISOString(),
                history: [
                    ...(tddState.history || []).slice(-10),
                    { phase: detected.phase, status: detected.status, timestamp: new Date().toISOString() }
                ]
            };

            fs.writeFileSync(tddStatePath, JSON.stringify(tddState, null, 2));

            const output = {
                decision: "allow",
                hookSpecificOutput: {
                    hookEventName: "AfterModel",
                    additionalContext: `🔄 TDD State Updated: ${detected.phase.toUpperCase()} (${detected.status}) - Feature: ${feature}`
                }
            };

            console.log(JSON.stringify(output));
        } else {
            console.log(JSON.stringify({ decision: "allow" }));
        }
    } catch (error) {
        console.log(JSON.stringify({
            decision: "allow",
            hookSpecificOutput: {
                hookEventName: "AfterModel",
                additionalContext: `CheerU-ADK TDD Detector: ${error.message}`
            }
        }));
    }
}

main();
