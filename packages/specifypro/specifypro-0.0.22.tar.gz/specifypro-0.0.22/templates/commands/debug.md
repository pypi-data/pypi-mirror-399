---
description: Analyze and debug code issues, errors, or unexpected behavior.
scripts:
  sh: scripts/bash/debug-analysis.sh --json "{ARGS}"
  ps: scripts/powershell/debug-analysis.ps1 -Json "{ARGS}"
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Debug Analysis

Given the user input, analyze and debug the specified issues:

1. **Problem Identification**:
   - Review the error messages, logs, or unexpected behavior
   - Identify the affected components or modules
   - Determine the scope and impact of the issue

2. **Root Cause Analysis**:
   - Examine the relevant code sections
   - Check for logical errors, syntax issues, or configuration problems
   - Review recent changes that might have introduced the issue
   - Analyze dependencies and external factors

3. **Debugging Strategy**:
   - Suggest debugging techniques (logging, breakpoints, unit tests)
   - Propose systematic approaches to isolate the problem
   - Recommend tools or methods for analysis

4. **Solution Implementation**:
   - Provide specific fixes or workarounds
   - Suggest code modifications with clear explanations
   - Consider potential side effects of the proposed solutions

5. **Verification**:
   - Recommend testing approaches to validate the fix
   - Suggest ways to prevent similar issues in the future
   - Provide instructions for confirming the resolution

6. **Output**:
   - Analyze the issue and provide debugging steps
   - Suggest fixes and verification methods
   - Document the debugging process for future reference

## Guidelines

- Focus on systematic debugging approaches
- Provide clear, actionable steps
- Consider multiple potential causes
- Suggest both immediate fixes and preventive measures
- Include relevant code examples when proposing solutions
- Document the debugging process for future reference
