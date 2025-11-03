# GitHub Actions Syntax Reference

Quick reference for common GitHub Actions patterns and syntax used in this project.

## Common Syntax Errors & Solutions

### ❌ Unsupported Functions

```yaml
# WRONG - These functions don't exist in GitHub Actions
${{ upper(github.event.inputs.program) }}
${{ lower(github.event.inputs.program) }}
${{ capitalize(github.event.inputs.program) }}
```

```yaml
# CORRECT - Use bash string manipulation in run steps
run: |
  PROGRAM="${{ github.event.inputs.program }}"
  OUTPUT_FILE="NEWS-${PROGRAM^^}.md"    # Uppercase
  echo "Processing ${PROGRAM,,}"         # Lowercase
```

### ❌ Pipe Operators

```yaml
# WRONG - Pipe operators not supported
${{ github.event.inputs.program | upper }}
${{ matrix.program | lower }}
```

```yaml
# CORRECT - Use bash variables
run: |
  PROGRAM="${{ github.event.inputs.program }}"
  UPPER_PROGRAM="${PROGRAM^^}"
  echo "Program: $UPPER_PROGRAM"
```

## Bash String Manipulation

### Case Conversion

```bash
# Uppercase
VAR="hello"
echo "${VAR^^}"        # Output: HELLO

# Lowercase
VAR="HELLO"
echo "${VAR,,}"        # Output: hello

# Capitalize first letter
VAR="hello"
echo "${VAR^}"         # Output: Hello
```

### String Operations

```bash
# Length
VAR="hello"
echo "${#VAR}"         # Output: 5

# Substring
VAR="hello world"
echo "${VAR:0:5}"      # Output: hello

# Replace
VAR="hello world"
echo "${VAR/world/GitHub}"  # Output: hello GitHub
```

## GitHub Actions Context Variables

### Commonly Used

```yaml
# Event information
${{ github.event_name }}                    # workflow_dispatch, push, etc.
${{ github.event.inputs.program }}          # Manual input
${{ github.event.inputs.verbose }}          # Boolean input

# Repository information
${{ github.repository }}                    # owner/repo-name
${{ github.ref }}                          # refs/heads/main
${{ github.sha }}                          # commit SHA

# Matrix context
${{ matrix.program }}                       # Current matrix value
${{ matrix.os }}                           # Operating system

# Job context
${{ job.status }}                          # success, failure, cancelled
${{ steps.step_id.outputs.result }}       # Step outputs
```

### Environment Variables

```yaml
env:
  TIMEZONE: Asia/Ho_Chi_Minh

# Access in steps
${{ env.TIMEZONE }}
```

## Workflow Triggers

### Schedule (Cron)

```yaml
on:
  schedule:
    - cron: '0 */1 * * *'    # Every hour
    - cron: '*/30 * * * *'   # Every 30 minutes
    - cron: '0 0 * * *'      # Daily at midnight
```

### Manual Dispatch

```yaml
on:
  workflow_dispatch:
    inputs:
      program:
        description: 'Program to crawl'
        required: true
        default: 'apcs'
        type: choice
        options:
        - 'apcs'
        - 'standard'
        - 'clc'
      verbose:
        description: 'Enable verbose output'
        required: false
        default: true
        type: boolean
```

## Conditional Execution

### If Conditions

```yaml
jobs:
  job1:
    if: github.event_name == 'workflow_dispatch'

  job2:
    if: github.event.inputs.program != 'all'

steps:
- name: Step Name
  if: steps.previous_step.outputs.changes == 'true'
```

### Matrix Strategy

```yaml
strategy:
  matrix:
    program: [apcs, standard, clc]
    os: [ubuntu-latest, windows-latest]

# Reference in steps
runs-on: ${{ matrix.os }}
```

## Step Outputs

### Set Output

```yaml
- name: Check Changes
  id: check_changes
  run: |
    if [ -f "changed.txt" ]; then
      echo "changes=true" >> $GITHUB_OUTPUT
      echo "file_count=5" >> $GITHUB_OUTPUT
    else
      echo "changes=false" >> $GITHUB_OUTPUT
    fi
```

### Use Output

```yaml
- name: Use Output
  if: steps.check_changes.outputs.changes == 'true'
  run: |
    echo "Found ${{ steps.check_changes.outputs.file_count }} changes"
```

## Common Patterns

### Multi-line Commands

```yaml
run: |
  echo "Starting process..."
  for item in apcs standard clc; do
    echo "Processing $item"
    ./process.sh "$item"
  done
  echo "Process complete"
```

### Environment Setup

```yaml
- name: Set up Python
  uses: actions/setup-python@v4
  with:
    python-version: '3.11'
    cache: 'pip'

- name: Install Dependencies
  run: |
    python -m pip install --upgrade pip
    pip install -r requirements.txt
```

### Git Operations

```yaml
- name: Configure Git
  run: |
    git config --local user.email "action@github.com"
    git config --local user.name "GitHub Action Bot"
    git config --local core.autocrlf false

- name: Commit Changes
  run: |
    git add .
    git commit -m "Auto-update: $(date)"
    git push
```

## Best Practices

### 1. Use Specific Action Versions

```yaml
# GOOD
uses: actions/checkout@v4
uses: actions/setup-python@v4

# AVOID
uses: actions/checkout@main
```

### 2. Handle Secrets Properly

```yaml
- name: Deploy
  env:
    API_KEY: ${{ secrets.API_KEY }}
  run: |
    curl -H "Authorization: Bearer $API_KEY" ...
```

### 3. Add Descriptive Names

```yaml
- name: Install Python Dependencies and Setup Package
  run: |
    pip install -r requirements.txt
    pip install -e .
```

### 4. Use Conditional Steps

```yaml
- name: Skip if No Changes
  if: steps.check.outputs.changes == 'false'
  run: echo "No changes detected, skipping deployment"
```

### 5. Timeout Long Operations

```yaml
- name: Long Running Task
  timeout-minutes: 10
  run: ./long-task.sh
```

## Debugging Tips

### 1. Add Debug Output

```yaml
- name: Debug Information
  run: |
    echo "Event: ${{ github.event_name }}"
    echo "Input program: ${{ github.event.inputs.program }}"
    echo "Matrix program: ${{ matrix.program }}"
    ls -la
    pwd
```

### 2. Use continue-on-error

```yaml
- name: Optional Step
  continue-on-error: true
  run: ./optional-command.sh
```

### 3. Save Artifacts for Debugging

```yaml
- name: Upload Logs
  if: failure()
  uses: actions/upload-artifact@v3
  with:
    name: debug-logs
    path: |
      *.log
      debug/
```

This reference covers the most common patterns used in the HCMUS News Crawler workflows.
