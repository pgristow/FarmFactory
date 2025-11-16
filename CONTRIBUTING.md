# Contributing to FarmFactory

Thank you for your interest in contributing to FarmFactory! This document provides guidelines and best practices for contributing to the project.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Pull Request Process](#pull-request-process)
- [Documentation](#documentation)
- [Issue Reporting](#issue-reporting)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors. We expect everyone to:

- Be respectful and considerate in communication
- Accept constructive criticism gracefully
- Focus on what is best for the project
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment or discriminatory language
- Trolling or insulting/derogatory comments
- Publishing private information without permission
- Other conduct which could reasonably be considered inappropriate

---

## Getting Started

### Prerequisites

- **Git** - Version control
- **Docker & Docker Compose** - Container runtime (recommended)
- **Python 3.11+** - Backend development
- **Node.js 18+** - Frontend development
- **PostgreSQL 14+** - Database (via Docker)
- **Redis** - Caching (via Docker)

### Initial Setup

1. **Fork the repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/FarmFactory.git
   cd FarmFactory
   ```

2. **Add upstream remote**
   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/FarmFactory.git
   ```

3. **Copy environment file**
   ```bash
   cp .env.example .env
   # Edit .env with your local configuration
   ```

4. **Start development environment**
   ```bash
   docker-compose up -d
   ```

5. **Verify setup**
   ```bash
   # Check backend
   curl http://localhost:8000/health

   # Check frontend
   open http://localhost:3000
   ```

---

## Development Workflow

### Branching Strategy

We follow **Git Flow** branching model:

- **`main`** - Production-ready code
- **`develop`** - Integration branch for features
- **`feature/*`** - New features (`feature/add-irrigation-api`)
- **`bugfix/*`** - Bug fixes (`bugfix/fix-date-parsing`)
- **`hotfix/*`** - Critical production fixes (`hotfix/security-patch`)
- **`release/*`** - Release preparation (`release/v1.0.0`)

### Creating a Feature Branch

```bash
# Update your local develop branch
git checkout develop
git pull upstream develop

# Create feature branch
git checkout -b feature/your-feature-name

# Make your changes and commit
git add .
git commit -m "feat: add your feature"

# Push to your fork
git push origin feature/your-feature-name
```

### Keeping Your Branch Updated

```bash
# Fetch latest changes
git fetch upstream

# Rebase your branch on develop
git checkout feature/your-feature-name
git rebase upstream/develop

# Resolve conflicts if any, then
git push origin feature/your-feature-name --force-with-lease
```

---

## Coding Standards

### Backend (Python)

#### Style Guide

We follow **PEP 8** with some modifications:

- **Line length**: 100 characters (not 79)
- **Indentation**: 4 spaces
- **Quotes**: Double quotes for strings
- **Import order**: Standard library → Third-party → Local

#### Code Formatting

Use **Black** for automatic formatting:

```bash
cd backend
black app/ tests/
```

#### Linting

Use **Flake8** for linting:

```bash
flake8 app/ tests/ --max-line-length=100
```

Configuration in `backend/.flake8`:

```ini
[flake8]
max-line-length = 100
exclude = .git,__pycache__,venv,alembic/versions
ignore = E203, W503
```

#### Type Hints

Always use type hints for function arguments and return values:

```python
from typing import List, Optional
from uuid import UUID

def get_farm_by_id(db: Session, farm_id: UUID) -> Optional[Farm]:
    """Retrieve a farm by its ID."""
    return db.query(Farm).filter(Farm.id == farm_id).first()
```

#### Docstrings

Use **Google-style** docstrings:

```python
def calculate_irrigation_efficiency(
    water_volume: float,
    area_hectares: float,
    yield_kg: float
) -> float:
    """
    Calculate irrigation water use efficiency.

    Args:
        water_volume: Total water used in liters
        area_hectares: Plot area in hectares
        yield_kg: Total yield in kilograms

    Returns:
        Water use efficiency in liters per kilogram

    Raises:
        ValueError: If yield_kg is zero or negative
    """
    if yield_kg <= 0:
        raise ValueError("Yield must be positive")
    return water_volume / yield_kg
```

#### Error Handling

Always handle exceptions gracefully:

```python
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

try:
    farm = crud.get_farm(db, farm_id)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    return farm
except SQLAlchemyError as e:
    logger.error(f"Database error: {str(e)}")
    raise HTTPException(status_code=500, detail="Database error")
```

### Frontend (TypeScript/React)

#### Style Guide

- **TypeScript**: Strict mode enabled
- **Naming**:
  - Components: PascalCase (`FarmList`, `PlotDetail`)
  - Files: PascalCase for components, camelCase for utilities
  - Variables/Functions: camelCase
  - Constants: UPPER_SNAKE_CASE
  - Interfaces: PascalCase with `I` prefix optional

#### Code Formatting

Use **Prettier** for formatting:

```bash
cd frontend
npm run format
```

Configuration in `frontend/.prettierrc`:

```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2
}
```

#### Linting

Use **ESLint**:

```bash
npm run lint
```

#### Component Structure

```typescript
import React, { useState, useEffect } from 'react';
import { Box, Typography } from '@mui/material';

interface FarmListProps {
  onFarmSelect: (farmId: string) => void;
  showArchived?: boolean;
}

/**
 * Displays a list of farms with filtering and selection capabilities.
 */
export const FarmList: React.FC<FarmListProps> = ({
  onFarmSelect,
  showArchived = false
}) => {
  const [farms, setFarms] = useState<Farm[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchFarms();
  }, [showArchived]);

  const fetchFarms = async () => {
    try {
      setLoading(true);
      const data = await farmApi.getFarms({ archived: showArchived });
      setFarms(data);
    } catch (error) {
      console.error('Failed to fetch farms:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h5">Farms</Typography>
      {/* Component content */}
    </Box>
  );
};
```

#### Hooks

Create custom hooks for reusable logic:

```typescript
// hooks/useFarms.ts
export const useFarms = (options?: FarmQueryOptions) => {
  const { data, error, isLoading } = useQuery(
    ['farms', options],
    () => farmApi.getFarms(options)
  );

  return {
    farms: data ?? [],
    error,
    isLoading,
  };
};
```

### Database

#### Migration Naming

```bash
# Format: YYYYMMDD_HHMM_description
alembic revision -m "20251116_1400_add_irrigation_table"
```

#### SQL Style

- **Keywords**: UPPERCASE
- **Table/Column names**: lowercase_with_underscores
- **Always**: Use explicit column names (not SELECT *)

```sql
-- Good
SELECT
    f.id,
    f.name,
    f.total_area_hectares
FROM farms f
WHERE f.created_at > '2024-01-01'
ORDER BY f.name ASC;

-- Bad
SELECT * FROM farms WHERE created_at > '2024-01-01';
```

---

## Testing Guidelines

### Backend Testing

#### Unit Tests

```python
# tests/unit/test_crud_farm.py
import pytest
from app.crud import farm as crud_farm
from app.schemas.farm import FarmCreate

def test_create_farm(db_session):
    """Test farm creation."""
    farm_data = FarmCreate(
        name="Test Farm",
        total_area_hectares=10.5
    )
    farm = crud_farm.create_farm(db_session, farm_data)

    assert farm.id is not None
    assert farm.name == "Test Farm"
    assert farm.total_area_hectares == 10.5
```

#### Integration Tests

```python
# tests/integration/test_api_farms.py
from fastapi.testclient import TestClient

def test_get_farms_api(client: TestClient, test_farm):
    """Test GET /api/v1/farms endpoint."""
    response = client.get("/api/v1/farms")

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["name"] == test_farm.name
```

#### Running Tests

```bash
# Run all tests
cd backend
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_crud_farm.py

# Run with verbose output
pytest -v
```

### Frontend Testing

#### Component Tests

```typescript
// components/FarmList.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { FarmList } from './FarmList';

describe('FarmList', () => {
  it('renders farms list', async () => {
    render(<FarmList onFarmSelect={jest.fn()} />);

    await waitFor(() => {
      expect(screen.getByText('Farms')).toBeInTheDocument();
    });
  });

  it('calls onFarmSelect when farm is clicked', async () => {
    const onFarmSelect = jest.fn();
    render(<FarmList onFarmSelect={onFarmSelect} />);

    // Test interaction
  });
});
```

#### Running Tests

```bash
cd frontend
npm test              # Run tests
npm run test:coverage # With coverage
npm run test:watch    # Watch mode
```

### Test Coverage Requirements

- **Overall**: Minimum 80% coverage
- **Critical paths**: 100% coverage (authentication, data import, financial calculations)
- **New features**: Must include tests

---

## Commit Message Guidelines

We follow **Conventional Commits** specification.

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, no logic change)
- **refactor**: Code refactoring
- **perf**: Performance improvements
- **test**: Adding or updating tests
- **chore**: Maintenance tasks (dependencies, build config)
- **ci**: CI/CD changes

### Examples

```bash
# Feature
feat(api): add irrigation data endpoint

Implement GET /api/v1/plots/{id}/irrigation endpoint
with date range filtering and pagination support.

Closes #123

# Bug fix
fix(import): handle missing columns in CSV upload

Add validation to check required columns exist before
processing. Show user-friendly error message.

Fixes #456

# Documentation
docs(readme): update installation instructions

Add Docker Compose setup steps and troubleshooting guide.

# Refactoring
refactor(database): optimize farm queries

Use eager loading to reduce N+1 queries. Improves
performance by ~40% on farm list endpoint.
```

### Rules

1. **Subject line**:
   - Max 72 characters
   - Lowercase (except proper nouns)
   - No period at the end
   - Imperative mood ("add" not "added" or "adds")

2. **Body** (optional but recommended):
   - Wrap at 72 characters
   - Explain what and why, not how
   - Separate from subject with blank line

3. **Footer** (optional):
   - Reference issues: `Closes #123`, `Fixes #456`
   - Breaking changes: `BREAKING CHANGE: description`

---

## Pull Request Process

### Before Submitting

1. **Ensure tests pass**
   ```bash
   # Backend
   cd backend && pytest

   # Frontend
   cd frontend && npm test
   ```

2. **Check code quality**
   ```bash
   # Backend
   black app/ && flake8 app/

   # Frontend
   npm run lint && npm run format
   ```

3. **Update documentation**
   - Update README if needed
   - Update API docs if adding/modifying endpoints
   - Add docstrings/comments for complex logic

4. **Rebase on develop**
   ```bash
   git fetch upstream
   git rebase upstream/develop
   ```

### PR Title

Use conventional commit format:

```
feat(irrigation): add water efficiency analytics
fix(import): resolve CSV parsing error for dates
docs(api): update authentication endpoint documentation
```

### PR Description Template

```markdown
## Description
Brief description of what this PR does.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Related Issues
Closes #123
Relates to #456

## Changes Made
- Added irrigation efficiency calculation
- Updated database schema for water tracking
- Created new API endpoint for analytics

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Screenshots (if applicable)
[Add screenshots for UI changes]

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] Tests added and passing
- [ ] No new warnings or errors
- [ ] Dependent changes merged
```

### Review Process

1. **Automated checks**: Must pass CI/CD pipeline
2. **Code review**: At least one approval required
3. **Testing**: QA verification for significant changes
4. **Merge**: Squash and merge to keep history clean

### Review Criteria

Reviewers will check:

- **Functionality**: Does it work as intended?
- **Code quality**: Is it readable and maintainable?
- **Tests**: Are there adequate tests?
- **Performance**: Are there any performance concerns?
- **Security**: Are there any security issues?
- **Documentation**: Is it properly documented?

---

## Documentation

### Code Documentation

- **All public APIs**: Must have docstrings
- **Complex logic**: Inline comments explaining why, not what
- **Types**: Use type hints (Python) and TypeScript types

### API Documentation

- **FastAPI**: Automatic via Swagger/OpenAPI
- **Add descriptions**: Use `description` parameter in endpoints
- **Add examples**: Provide request/response examples

```python
@router.post(
    "/farms",
    response_model=FarmInDB,
    status_code=201,
    summary="Create a new farm",
    description="Create a new farm with the provided details",
    responses={
        201: {"description": "Farm created successfully"},
        400: {"description": "Invalid input data"},
        409: {"description": "Farm already exists"}
    }
)
async def create_farm(farm: FarmCreate, db: Session = Depends(get_db)):
    """
    Create a new farm.

    Example request:
    ```json
    {
        "name": "Green Valley Farm",
        "total_area_hectares": 25.5,
        "latitude": 34.0522,
        "longitude": -118.2437
    }
    ```
    """
    return crud_farm.create_farm(db, farm)
```

### User Documentation

Update user guides in `docs/user-guide/` when adding features:

- How to use the feature
- Screenshots/GIFs
- Common issues and solutions

---

## Issue Reporting

### Bug Reports

Use the bug report template:

```markdown
**Describe the bug**
Clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
 - OS: [e.g. Ubuntu 22.04]
 - Browser: [e.g. Chrome 120]
 - Version: [e.g. v1.0.0]

**Additional context**
Any other context about the problem.
```

### Feature Requests

```markdown
**Is your feature request related to a problem?**
Clear description of the problem.

**Describe the solution you'd like**
Clear description of what you want to happen.

**Describe alternatives you've considered**
Any alternative solutions or features you've considered.

**Additional context**
Any other context, mockups, or screenshots.
```

---

## Development Tips

### Database Migrations

```bash
# Create migration
cd backend
alembic revision --autogenerate -m "description"

# Review the migration file before applying!
# Edit alembic/versions/<revision_id>_description.py if needed

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Debugging

#### Backend

```python
# Add breakpoint
import pdb; pdb.set_trace()

# Or use IDE debugger with uvicorn
# Launch configuration in VSCode
```

#### Frontend

```typescript
// Use React DevTools
// Use browser debugger
debugger;

// Console logging
console.log('Debug:', { farms, loading });
```

### Performance Profiling

```bash
# Backend - Use py-spy
py-spy top --pid <process_id>

# Frontend - Use Chrome DevTools
# Network tab, Performance tab, React Profiler
```

---

## Getting Help

- **Documentation**: Check `/docs` directory
- **API Docs**: http://localhost:8000/docs
- **Issues**: Search existing issues first
- **Discussions**: Use GitHub Discussions for questions
- **Chat**: Join our Slack/Discord channel

---

## Recognition

Contributors will be recognized in:

- CHANGELOG.md for each release
- README.md contributors section
- Project website (when available)

---

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (see LICENSE file).

---

**Thank you for contributing to FarmFactory!**

We appreciate your time and effort in making this project better. Every contribution, no matter how small, helps improve the platform for farmers worldwide.

---

Last Updated: 2025-11-16
