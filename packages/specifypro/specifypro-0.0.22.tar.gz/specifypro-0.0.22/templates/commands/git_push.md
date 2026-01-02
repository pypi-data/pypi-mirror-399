---
description: Push current branch to remote repository with appropriate flags.
scripts:
  sh: scripts/bash/git-push.sh --json "{ARGS}"
  ps: scripts/powershell/git-push.ps1 -Json "{ARGS}"
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Push to Remote Repository

Given the user input, push the current branch to the remote repository:

1. **Analyze Current State**:
   - Check current branch name
   - Verify the remote origin exists and is accessible
   - Review the number of commits ahead/behind the remote
   - Check for any uncommitted changes

2. **Determine Push Strategy**:
   - For new branches: use --set-upstream to establish tracking
   - For existing branches: regular push
   - Handle any special requirements from user input

3. **Execute Push**:
   - Run git push with appropriate flags
   - Handle authentication if required
   - Monitor for any conflicts or errors

4. **Verification**:
   - Confirm the push was successful
   - Verify the remote repository reflects the changes
   - Report the push status

5. **Output**:
   - Execute the git push command
   - Report success status and any relevant information
   - Provide links to remote repository if available

## Guidelines

- Use --set-upstream for first-time pushes to new branches
- Handle authentication prompts appropriately
- Verify the remote repository is accessible before pushing
- Report any merge conflicts or errors that occur
- Follow repository-specific branching and pushing conventions
