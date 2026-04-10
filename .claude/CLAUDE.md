# CLAUDE.md

## Commands

- Lint: `make lint`
- Format: `make format`
- Test: `make test`
- Test (filter): `uv run pytest tests/{test_pattern}.py -v`

For other python commands, always prefix with `uv run` to activate the virtual environment.

## Project Overview

See @README.md for project purpose, guidelines, and local setup instructions.

## Development Workflow

### Testing Changes

- After finishing a task, run `make lint` to check for syntax/style errors. Fix if any problems detected.

### Committing Changes
```bash
git add .
git commit -m "subject\n\n<body" -m "..."
```

### PR Guidelines
- Keep PRs small and focused
- Include detailed PR description
- Link to related issues
- Add any new code and documentation

## Key Design Patterns

- **Dependency Injection**: Most components inject interfaces via function parameters
- **Composition**: Data loading happens via DuckDB's SQL on Parquet files
- **Separation of Concerns**: Data collection separated from analysis logic

## Documentation

### Reading Existing Documentation
- **Writing Analyses**: `docs/ANALYSIS.md` - Template for writing custom analysis scripts
- **Data Schemas**: `docs/SCHEMAS.md` - Parquet file schemas
- **General Info**: `README.md` - Project overview and setup instructions
- **Contributing**: `CONTRIBUTING.md` - Guidelines for contributions
- **Analysis Templates**: `docs/ANALYSIS.md` - Common query patterns and usage

### Understanding the Code
1. Start from `src/common/analysis.py` - Understand the analysis contract
2. Follow the `run()` → `Visualization` → `Export` flow
3. Check `docs/ANALYSIS.md` for common patterns
4. Examine `docs/SCHEMAS.md` for data types and relationships

## Configuration

### Environment Variables
Check `.env.example` for configuration templates.

### Tool Configuration
- **Ruff** (code linter/formatter): See `pyproject.toml` configuration
- **pytest**: Test runner configuration in `pyproject.toml`

## Data Sources

### External Dependencies
- **Kalshi**: Major U.S. stock market prediction platform
- **Polymarket**: Crypto market prediction platform with blockchain-based trades
