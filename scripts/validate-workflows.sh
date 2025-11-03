#!/bin/bash
# Validate GitHub Actions workflows syntax

set -e

echo "Validating GitHub Actions workflows..."

WORKFLOWS_DIR=".github/workflows"
ISSUES_FOUND=0

if [ ! -d "$WORKFLOWS_DIR" ]; then
    echo "Workflows directory not found: $WORKFLOWS_DIR"
    exit 1
fi

# Function to check for common GitHub Actions syntax errors
validate_workflow() {
    local file="$1"
    local filename=$(basename "$file")

    echo "Checking $filename..."

    # Check for pipe operators in expressions
    if grep -q "| upper\|| lower\|| capitalize" "$file"; then
        echo "Found unsupported pipe operators in $filename"
        echo "Use bash string manipulation instead: \${VAR^^} for uppercase"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    fi

    # Check for unsupported GitHub Actions functions
    if grep -q "upper(\|lower(\|capitalize(" "$file"; then
        echo "Found unsupported GitHub Actions functions in $filename"
        echo "GitHub Actions doesn't support upper(), lower(), capitalize()"
        echo "Use bash string manipulation: \${VAR^^} for uppercase, \${VAR,,} for lowercase"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    fi

    # Check for basic YAML syntax
    if command -v yamllint >/dev/null 2>&1; then
        if ! yamllint -c /dev/null "$file" >/dev/null 2>&1; then
            echo "YAML syntax errors in $filename"
            ISSUES_FOUND=$((ISSUES_FOUND + 1))
        fi
    else
        echo "yamllint not installed, skipping YAML validation"
    fi

    # Check for missing required fields
    if ! grep -q "name:" "$file"; then
        echo "Missing 'name:' field in $filename"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    fi

    if ! grep -q "on:" "$file"; then
        echo "Missing 'on:' field in $filename"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    fi

    if ! grep -q "jobs:" "$file"; then
        echo "Missing 'jobs:' field in $filename"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    fi

    # Check for job dependency issues
    if grep -q "needs:" "$file"; then
        # Extract job names and needs references
        job_names=$(grep -E "^[[:space:]]*[a-zA-Z0-9_-]+:$" "$file" | grep -v "^[[:space:]]*-" | sed 's/:$//' | sed 's/^[[:space:]]*//')
        needs_refs=$(grep "needs:" "$file" | sed 's/.*needs:[[:space:]]*//' | sed 's/[[:space:]]*$//')

        for need in $needs_refs; do
            if ! echo "$job_names" | grep -q "^$need$"; then
                echo "Job dependency error: '$need' referenced but not defined in $filename"
                ISSUES_FOUND=$((ISSUES_FOUND + 1))
            fi
        done
    fi

    echo "$filename validation completed"
}

# Validate all workflow files
for workflow in "$WORKFLOWS_DIR"/*.yml "$WORKFLOWS_DIR"/*.yaml; do
    if [ -f "$workflow" ]; then
        validate_workflow "$workflow"
    fi
done

echo ""
if [ $ISSUES_FOUND -eq 0 ]; then
    echo "All workflows validated successfully!"
    echo "No syntax errors found"
    exit 0
else
    echo "Found $ISSUES_FOUND issue(s) in workflows"
    echo "Please fix the issues before committing"
    exit 1
fi
