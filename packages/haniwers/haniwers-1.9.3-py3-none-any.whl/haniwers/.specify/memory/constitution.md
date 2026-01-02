<!-- Sync Impact Report: constitution.md v1.0.0
  - Initial constitution creation from template
  - 5 core principles defined (Beginner-Friendly, Educational, Spec-Driven, Code Quality, Versioning)
  - Governance framework established
  - All dependent templates remain valid with initial constitution
  - No template updates required at this stage
-->

# Haniwers Constitution

## Core Principles

### I. Beginner-Friendly Project

Code and documentation MUST be written for clarity and learning. New contributors
should understand the purpose and structure without extensive prior knowledge. Complex
algorithms are explained, educational value is prioritized alongside functionality.

**Rationale**: Haniwers is both a production tool and an educational resource for
cosmic ray physics. Clear code facilitates knowledge transfer and collaboration.

### II. Educational Docstrings

Every function, class, and module MUST have comprehensive docstrings explaining:

- What the code does (purpose)
- How to use it (parameters, return values, examples)
- Why it exists (context or scientific rationale where applicable)
- Edge cases or assumptions

Docstrings use clear English and avoid jargon without explanation.

**Rationale**: Self-documenting code reduces maintenance burden and onboards new
developers efficiently. Docstrings serve as primary documentation source.

### III. Spec-Driven Development

All non-trivial features MUST follow the Spec-Driven Workflow:

1. Create `spec.md` documenting requirements and design
2. Run `/clarify` if requirements are ambiguous
3. Generate `plan.md` with `/plan`
4. Generate `tasks.md` with `/tasks`
5. Run `/analyze` to validate consistency
6. Execute `tasks.md` with `/implement`

Direct code changes bypass this workflow ONLY for: bug fixes, documentation updates,
configuration tweaks.

**Rationale**: Structured specification prevents scope creep, ensures alignment,
and creates auditable records of design decisions.

### IV. Code Quality (DRY, SRP, YAGNI)

Code MUST adhere to three foundational principles:

- **DRY (Don't Repeat Yourself)**: Extract reusable functions, constants, and
  configurations. Avoid code duplication across modules or versions.
- **SRP (Single Responsibility Principle)**: Each class, function, and module has
  ONE clear reason to change. Multi-purpose components are refactored into
  focused units.
- **YAGNI (You Aren't Gonna Need It)**: Implement features only when needed.
  Do not add speculative "flexibility" or pre-emptive abstractions. Simple
  solutions are preferred over complex ones.

**Rationale**: These practices ensure maintainability, testability, and reduce
cognitive load for future contributors.

### V. Semantic Versioning

The project follows semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Backward-incompatible changes (breaking API changes)
- **MINOR**: New features or enhancements (backward-compatible)
- **PATCH**: Bug fixes and documentation updates (no new features)

Version updates MUST be accompanied by:

- Updated `pyproject.toml` version field
- Updated `src/haniwers/v*//__init__.py:__version__` for all applicable versions
- Release notes in `docs/releases/vX.Y.Z.md`
- Git tag with format `vX.Y.Z`

**Rationale**: Clear versioning enables reproducible research, manages user
expectations, and facilitates dependency management.

## Development Workflow

### Spec-Driven Process

1. **Specification Phase**: Create `/specs/[###-feature-name]/spec.md`
   - User requirements and use cases
   - Design decisions and rationale
   - Scope boundaries and non-goals
2. **Clarification Phase** (if needed): Run `/clarify`
   - Address ambiguous requirements
   - Validate assumptions with stakeholders
3. **Planning Phase**: Run `/plan` to generate `plan.md`
   - Implementation strategy and approach selection
   - Critical files and architectural decisions
   - Trade-off analysis
4. **Task Generation**: Run `/tasks` to create `tasks.md`
   - Actionable, dependency-ordered tasks
   - Clear success criteria
   - Measurable progress tracking
5. **Consistency Check**: Run `/analyze` before implementation
   - Validate spec, plan, and tasks consistency
   - Ensure constitution compliance
   - Identify missing requirements
6. **Implementation**: Execute `/implement` to track task progress
   - Implement features according to plan
   - Update tasks in real-time
   - Document discoveries and decisions

### Testing Standards

**Test Coverage Requirement**: Minimum 80% code coverage for production code.

**Test Organization**:

- Unit tests: `tests/v1/unit/<module>/<component>/`
- Integration tests: `tests/v1/integration/`
- Fixtures and test data: Organized by module

**TDD Methodology**:

- Write skeleton test structure first
- User approves test descriptions before implementation
- Red-Green-Refactor cycle enforced
- Pre-commit hooks verify coverage

**Scientific Accuracy**:

- Physics calculations validated against published references
- Edge cases tested with known datasets
- Results compared against expected cosmic ray detector behavior

### Code Review & Quality Gates

All pull requests MUST pass:

- **Pre-commit hooks**: Formatting (ruff), linting, trailing whitespace
- **Test suite**: `pytest --cov` ≥ 80% coverage
- **Constitution compliance**: Spec-driven process followed, principles adhered
- **Manual review**: At least one maintainer approval

### Version Management

**Branch Structure**:

- `main`: Stable v2 development (next-generation)
- `v1`: Maintenance and refactoring (current stable)
- `v0`: Legacy maintenance only
- Feature branches: Short-lived, deleted after merge

**Release Process**:

1. Create release notes in `docs/releases/vX.Y.Z.md`
2. Use `cz bump` to increment version and generate changelog
3. Tag release with `git tag vX.Y.Z`
4. Push to remote with `git push origin --tags`
5. Create GitLab MR for review and merge

## Governance

**Constitution Enforcement**: This constitution supersedes all other development
practices. Code, design, and process decisions must align with these principles.

**Amendment Procedure**:

1. Proposed amendment submitted with rationale
2. Community discussion and feedback period (minimum 3 days)
3. Amendment vote or maintainer approval
4. Update constitution with new version number
5. Update dependent templates and documentation
6. Publish amendment notice in release notes

**Compliance Review**: Constitution compliance is verified:

- During code review via PR checklist
- In automated checks (test coverage, linting)
- In manual review (spec-driven process, principle adherence)

**Version Governance**:

- v0: Maintenance-only (critical bug fixes, documentation)
- v1: Active maintenance (refactoring, improvements)
- v2: Active development (new features, architectural improvements)
- Each version maintains independent `__version__` in `__init__.py`

**Development Guidance**: Runtime development guidance is documented in:

- `CLAUDE.md` for AI assistant context
- `docs/developers/` for contributor guides
- Inline docstrings for code-level documentation

**Version**: 1.0.0 | **Ratified**: 2025-12-29 | **Last Amended**: 2025-12-29
