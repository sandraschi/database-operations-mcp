# Version Control Branching Strategy

## Overview
This document outlines our Git branching strategy for MCP server development, based on Git Flow principles but simplified for our needs.

## Branch Types

### Main Branches
- `main`
  - Production-ready code
  - Protected branch (direct commits disabled)
  - Only updated via pull requests from `develop` or `release/*` branches
  - Tags for releases (e.g., `v1.0.0`)

- `develop`
  - Integration branch for completed features
  - Always in a deployable state
  - Source for feature branches

### Supporting Branches

#### Feature Branches (`feature/*`)
- For developing new features
- Branch from: `develop`
- Merge back into: `develop`
- Naming: `feature/feature-name` (e.g., `feature/user-authentication`)

#### Bugfix Branches (`fix/*`)
- For fixing bugs in production
- Branch from: `main`
- Merge back into: `main` and `develop`
- Naming: `fix/description` (e.g., `fix/login-error`)

#### Release Branches (`release/*`)
- For preparing production releases
- Branch from: `develop`
- Merge into: `main` and `develop`
- Naming: `release/v1.0.0`

#### Hotfix Branches (`hotfix/*`)
- For critical production fixes
- Branch from: `main`
- Merge into: `main` and `develop`
- Naming: `hotfix/description` (e.g., `hotfix/security-patch`)

## Workflow

### Starting a New Feature
```bash
# Update develop branch
git checkout develop
git pull origin develop

# Create and switch to a new feature branch
git checkout -b feature/amazing-feature
```

### Finishing a Feature
```bash
# Make sure all tests pass
pytest

# Stage changes
git add .

# Commit with a descriptive message
git commit -m "feat: add amazing feature"

# Push to remote
git push -u origin feature/amazing-feature

# Create a pull request from GitHub UI to merge into develop
```

### Creating a Release
```bash
# Create a release branch from develop
git checkout -b release/v1.0.0 develop

# Bump version in pyproject.toml
# Update CHANGELOG.md

git add .
git commit -m "chore: prepare for v1.0.0 release"
git push -u origin release/v1.0.0

# Create a pull request to merge into main
# After merging, tag the release
```

### Hotfix Process
```bash
# Create a hotfix branch from main
git checkout -b hotfix/critical-issue main

# Fix the issue
# Bump version (e.g., 1.0.0 → 1.0.1)

git add .
git commit -m "fix: resolve critical issue"
git push -u origin hotfix/critical-issue

# Create pull requests:
# 1. hotfix/critical-issue → main
# 2. hotfix/critical-issue → develop
```

## Commit Message Format

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools

### Examples
```
feat(auth): add OAuth2 support

Add support for OAuth2 authentication using the 'auth0' provider.
Closes #123
```

```
fix(api): prevent race condition in user creation

Add a unique constraint to the email field to prevent duplicate users.
Fixes #456
```

## Pull Request Guidelines
- Keep PRs small and focused
- Include tests for new features
- Update documentation as needed
- Get at least one code review before merging
- Use the PR template
- Link related issues

## Branch Protection Rules
- `main` and `develop` branches are protected
- Require pull request reviews before merging
- Require status checks to pass before merging
- Require linear history
- Include administrators in branch protection

## Tagging and Versioning
- Use [Semantic Versioning](https://semver.org/)
- Create tags for each release (e.g., `v1.0.0`)
- Annotated tags are preferred

## Best Practices
1. **Keep your branches up to date**
   ```bash
   git checkout feature/your-feature
   git fetch origin
   git merge origin/develop
   ```

2. **Clean up old branches**
   ```bash
   # Delete local branch
git branch -d feature/old-feature

   # Delete remote branch
git push origin --delete feature/old-feature
   ```

3. **Use interactive rebase**
   ```bash
   git rebase -i develop
   ```

4. **Write good commit messages**
   - Use the imperative mood ("Add feature" not "Added feature")
   - Keep the subject line under 50 characters
   - Reference issues and pull requests

## Tools
- [GitHub Desktop](https://desktop.github.com/) - GUI client
- [Sourcetree](https://www.sourcetreeapp.com/) - Free Git GUI
- [GitKraken](https://www.gitkraken.com/) - Feature-rich Git client
- [Lazygit](https://github.com/jesseduffield/lazygit) - Terminal UI for Git
