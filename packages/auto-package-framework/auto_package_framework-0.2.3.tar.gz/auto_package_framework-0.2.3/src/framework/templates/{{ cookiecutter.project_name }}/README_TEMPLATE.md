# Project Template - Complete Guide

This directory contains a complete project template with all best practices and AI-friendly configurations.

> **👋 START HERE**: Read **[START_HERE.md](./START_HERE.md)** first - it's your navigation hub!

## 📁 Directory Structure

```
PROJECT_TEMPLATE/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml              # Continuous Integration
│   │   └── release.yml         # Automated releases
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.yml      # Bug report template
│   │   └── feature_request.yml # Feature request template
│   ├── dependabot.yml          # Automated dependency updates
│   └── pull_request_template.md # PR template
├── docs/                       # (Create this directory)
│   └── DEVELOPMENT_PHILOSOPHY.md  # Copy from parent docs/
├── PROJECT_IDEA.md             # ⭐⭐ Project vision & AI entry point
├── AI_CONTEXT.md               # ⭐ AI assistant guide
├── AI_START_PROMPT.md          # AI prompt templates
├── .pre-commit-config.yaml     # Pre-commit hooks
├── release-please-config.json  # Automated versioning
├── pyproject.toml              # Python project config
├── CODE_OF_CONDUCT.md          # Community standards
├── SECURITY.md                 # Security policy
├── CONTRIBUTING.md             # Contribution guidelines
├── README.md                   # Project README template
└── QUICK_START.md              # Setup instructions
```

## 🎯 Key Files Explained

### START_HERE.md ⭐⭐⭐
**THE FIRST FILE TO READ - Navigation Hub!**

This is your starting point. It will:
- Guide you to the right files based on your goal
- Explain file priorities and reading order
- Provide quick navigation links
- Show common workflows

**Read this file first**, then follow the links to relevant documentation.

### PROJECT_IDEA.md ⭐⭐
**THE PRIMARY ENTRY POINT - Start here!**

This is where you:
- Write your project concept and requirements
- Plan architecture and features
- Track development progress
- Document design decisions

**For AI Assistants**: This is the FIRST file to read! It contains:
- Project vision and goals
- Requirements and features
- Architecture plans
- Current development status

**Always keep this file updated** as ideas evolve.

### AI_CONTEXT.md ⭐
**Technical context for AI assistants**

This file provides comprehensive technical context:
- Project structure and philosophy
- Coding standards and conventions
- Technology stack and tools
- Development workflows
- Code quality guidelines

**For AI Assistants**: Read this AFTER PROJECT_IDEA.md for technical details.

**Always keep this file updated** as the project evolves.

### AI_START_PROMPT.md
**Ready-to-use prompts for AI assistants**

Contains pre-written prompts for:
- Project kickoff
- Ongoing development
- Code review
- Debugging
- Documentation updates

### .pre-commit-config.yaml
Automatically runs checks before each commit:
- Code formatting
- Linting
- Type checking
- File validation

### release-please-config.json
Automates version management:
- Creates Release PRs
- Generates CHANGELOG
- Updates version numbers
- Creates GitHub Releases

### .github/workflows/
CI/CD automation:
- **ci.yml**: Runs tests on every PR
- **release.yml**: Publishes packages on release

## 🚀 Quick Setup

1. **Copy template to your project**
   ```bash
   cp -r PROJECT_TEMPLATE your-project-name
   cd your-project-name
   ```

2. **Follow QUICK_START.md** for step-by-step setup

3. **Customize AI_CONTEXT.md** with your project specifics

## 📚 Best Practices Included

✅ **AI Integration**
- AI_CONTEXT.md for AI assistants
- AI-friendly code structure
- Comprehensive documentation

✅ **Automation**
- Pre-commit hooks
- Automated testing
- Automated releases
- Dependency updates

✅ **Community**
- Code of Conduct
- Contribution guidelines
- Issue/PR templates
- Security policy

✅ **Code Quality**
- Linting and formatting
- Type checking
- Test coverage
- CI/CD pipeline

## 🔧 Customization Checklist

After copying the template:

- [ ] Update `README.md` with project details
- [ ] Update `pyproject.toml` (or equivalent) with package info
- [ ] Customize `AI_CONTEXT.md` with project specifics
- [ ] Update `release-please-config.json` with package name
- [ ] Configure `.github/workflows/*.yml` for your stack
- [ ] Update badges in `README.md` with your repo
- [ ] Set up GitHub Secrets (PyPI token, etc.)
- [ ] Install dependencies: `pip install -e ".[dev]"`
- [ ] Install pre-commit: `pre-commit install`

## 📖 Learn More

- [QUICK_START.md](QUICK_START.md) - Detailed setup guide
- [AI_CONTEXT.md](AI_CONTEXT.md) - AI assistant guide
- [CONTRIBUTING.md](CONTRIBUTING.md) - How to contribute
- [docs/DEVELOPMENT_PHILOSOPHY.md](../docs/DEVELOPMENT_PHILOSOPHY.md) - Development practices

## 🎓 Philosophy

This template embodies three core principles:

1. **AI as Amplifier**: Use AI to enhance, not replace, human judgment
2. **Community First**: Lower barriers, respond quickly, grow together
3. **Platform Leverage**: Maximize use of existing tools and services

---

**Ready to start?** 

1. **Read [START_HERE.md](./START_HERE.md)** - Your navigation hub
2. **Write [PROJECT_IDEA.md](./PROJECT_IDEA.md)** - Document your ideas
3. **Follow [QUICK_START.md](./QUICK_START.md)** - Set up the project

