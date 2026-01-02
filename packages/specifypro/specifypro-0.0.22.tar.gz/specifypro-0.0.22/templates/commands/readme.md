---
description: Generate or update README.md file with project documentation.
scripts:
  sh: scripts/bash/generate-readme.sh --json "{ARGS}"
  ps: scripts/powershell/generate-readme.ps1 -Json "{ARGS}"
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Generate README Documentation

Given the user input, create or update the README.md file with comprehensive project documentation:

1. **Analyze Project Context**:
   - Review existing project files, configuration, and structure
   - Identify the technology stack, dependencies, and architecture
   - Understand the project's purpose and functionality

2. **Generate README Structure**:
   - Title and description
   - Table of contents
   - Installation instructions
   - Usage examples
   - Features
   - Contributing guidelines
   - License information
   - Acknowledgements

3. **Include Essential Sections**:
   - Clear project description
   - Prerequisites and setup instructions
   - Configuration details
   - API documentation if applicable
   - Screenshots or diagrams if available
   - Testing instructions
   - Deployment information

4. **Follow Best Practices**:
   - Use clear, concise language
   - Include code examples where appropriate
   - Provide visual aids (images, diagrams, GIFs)
   - Make it accessible to both technical and non-technical users
   - Ensure the README is up-to-date with current functionality

5. **Output**:
   - Write the generated content to README.md in the project root
   - Preserve any custom sections that were previously added
   - Ensure proper formatting and markdown syntax

## Guidelines

- Focus on clarity and usability
- Include practical examples
- Document any special configuration requirements
- Mention any third-party services or APIs used
- Provide troubleshooting tips if relevant
