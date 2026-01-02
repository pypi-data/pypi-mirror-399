---
description: Create a git commit with an optimized commit message following conventional commit standards.
scripts:
  sh: scripts/bash/git-commit.sh --json "{ARGS}"
  ps: scripts/powershell/git-commit.ps1 -Json "{ARGS}"
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Create Git Commit

Given the user input, create a git commit with an optimized commit message:

1. **Analyze Changes**:
   - Review the current git status and staged files
   - Identify the types of changes made (features, fixes, documentation, etc.)
   - Determine the scope and impact of the changes

2. **Generate Conventional Commit Message**:
   - Use the format: `<type>(<scope>): <subject>`
   - Types: feat, fix, docs, style, refactor, test, chore
   - Include a descriptive subject line (imperative mood, 50 chars max)
   - Add a body if needed for detailed explanation
   - Include breaking changes notice if applicable

3. **Commit Process**:
   - Stage any unstaged changes if appropriate
   - Create the commit with the generated message
   - Verify the commit was successful

4. **Commit Message Guidelines**:
   - Start with a capital letter
   - Do not end with a period
   - Use imperative mood ("Add" not "Added")
   - Be specific and descriptive
   - Reference issue numbers if applicable

5. **Output**:
   - Execute the git commit command with the generated message
   - Report the commit hash and status

## Guidelines

- Follow conventional commit standards
- Keep messages concise but descriptive
- Match the commit type to the actual changes
- Include scope when relevant to specific components
- Ensure the commit message explains the why, not just the what
