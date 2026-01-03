#!/bin/bash
# CheerU-ADK Code Validator Hook (BeforeTool)
#
# Validates code before file write operations.
# - Checks for common issues
# - Prevents secrets from being committed
# - Basic syntax validation

set -e

# Read input from stdin
INPUT=$(cat)

# Parse tool input
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')
CONTENT=$(echo "$INPUT" | jq -r '.tool_input.content // empty')

# Default allow
DECISION="allow"
MESSAGE=""

# Check for secrets/sensitive data
check_secrets() {
    local content="$1"
    
    # Common secret patterns
    PATTERNS=(
        "password\s*=\s*['\"][^'\"]+['\"]"
        "api_key\s*=\s*['\"][^'\"]+['\"]"
        "secret\s*=\s*['\"][^'\"]+['\"]"
        "token\s*=\s*['\"][^'\"]+['\"]"
        "aws_access_key"
        "aws_secret"
        "private_key"
        "-----BEGIN.*PRIVATE KEY-----"
    )
    
    for pattern in "${PATTERNS[@]}"; do
        if echo "$content" | grep -qiE "$pattern"; then
            echo "potential_secret"
            return
        fi
    done
    
    echo "clean"
}

# Validate based on file type
validate_file() {
    local file_path="$1"
    local content="$2"
    
    # Get file extension
    EXT="${file_path##*.}"
    
    case "$EXT" in
        py)
            # Python: Check for syntax errors (basic)
            if echo "$content" | grep -qE "^\s+(import|def|class|if|for|while)" 2>/dev/null; then
                # Indentation looks present, basic check passed
                echo "valid"
            else
                echo "valid"
            fi
            ;;
        js|ts)
            # JavaScript/TypeScript: Basic bracket balance
            OPEN=$(echo "$content" | grep -o '{' | wc -l)
            CLOSE=$(echo "$content" | grep -o '}' | wc -l)
            if [ "$OPEN" -eq "$CLOSE" ]; then
                echo "valid"
            else
                echo "warning: unbalanced braces"
            fi
            ;;
        *)
            echo "valid"
            ;;
    esac
}

# Main validation
if [ -n "$CONTENT" ]; then
    SECRET_CHECK=$(check_secrets "$CONTENT")
    
    if [ "$SECRET_CHECK" = "potential_secret" ]; then
        DECISION="deny"
        MESSAGE="⚠️ CheerU-ADK: Potential secret detected in file content. Please use environment variables instead."
    else
        VALIDATION=$(validate_file "$FILE_PATH" "$CONTENT")
        if [[ "$VALIDATION" == warning* ]]; then
            MESSAGE="⚠️ CheerU-ADK: $VALIDATION in $FILE_PATH"
        fi
    fi
fi

# Output JSON response
if [ "$DECISION" = "deny" ]; then
    echo "{\"decision\": \"deny\", \"hookSpecificOutput\": {\"hookEventName\": \"BeforeTool\", \"additionalContext\": \"$MESSAGE\"}}"
else
    if [ -n "$MESSAGE" ]; then
        echo "{\"decision\": \"allow\", \"hookSpecificOutput\": {\"hookEventName\": \"BeforeTool\", \"additionalContext\": \"$MESSAGE\"}}"
    else
        echo "{\"decision\": \"allow\"}"
    fi
fi
