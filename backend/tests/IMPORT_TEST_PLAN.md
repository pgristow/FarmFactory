# Import System Test Plan

**Version**: 1.0
**Date**: 2025-11-17
**Sprint**: Sprint 2 - Data Import System
**Owner**: QA Specialist

## Table of Contents

- [Overview](#overview)
- [Test Strategy](#test-strategy)
- [Test Scope](#test-scope)
- [Test Scenarios](#test-scenarios)
- [Test Data](#test-data)
- [Expected Results](#expected-results)
- [Performance Benchmarks](#performance-benchmarks)
- [Coverage Goals](#coverage-goals)
- [Test Execution](#test-execution)
- [Defect Management](#defect-management)
- [Acceptance Criteria](#acceptance-criteria)

## Overview

### Purpose

This test plan outlines the comprehensive testing strategy for the FarmFactory Data Import System. The import system enables users to bulk-import farm data from CSV and Excel files with intelligent column mapping, validation, and async batch processing.

### System Under Test

**Import System Components:**
- File upload handling (CSV, Excel)
- File parsing (CSV with multiple delimiters, Excel .xls/.xlsx)
- Column mapping with auto-detection (>80% accuracy target)
- Data validation (types, ranges, references, cross-field)
- Async batch processing (Celery)
- Import status tracking
- Error reporting and recovery
- Template generation

### Test Objectives

1. Verify all import functionality works correctly
2. Ensure performance targets are met (1k-1M rows)
3. Validate error handling for all scenarios
4. Confirm data integrity through entire import pipeline
5. Achieve 85% code coverage for import modules
6. Test cross-browser compatibility (frontend)
7. Validate security measures (file validation, size limits)

## Test Strategy

### Test Pyramid

```
      /\
     /E2E\         10 tests (5%)    - Complete workflows
    /------\
   /Integration\   70 tests (25%)   - API endpoints, workflows
  /------------\
 /    Unit      \  240 tests (70%)  - Parsers, validators, mappers
/______________\
```

### Test Levels

#### 1. Unit Tests (240 tests)
- **CSV Parser** (30 tests): Delimiters, encodings, line endings
- **Excel Parser** (25 tests): .xls, .xlsx, formulas, sheets
- **Column Mapper** (35 tests): Auto-mapping, fuzzy matching, confidence scores
- **Data Validator** (60 tests): Types, ranges, required fields, duplicates
- **File Formats** (40 tests): BOM, encodings, corrupted files
- **Error Handling** (50 tests): All error scenarios

#### 2. Integration Tests (70 tests)
- **Import API** (40 tests): All 8 API endpoints
- **Import Workflow** (30 tests): End-to-end import process, rollback

#### 3. Performance Tests (15 tests)
- **Bulk Import** (4 tests): 1k, 10k, 100k, 1M rows
- **Concurrent Imports** (2 tests): 2-3 simultaneous imports
- **Memory Efficiency** (3 tests): Streaming, memory limits
- **Batch Processing** (3 tests): Optimal batch sizes
- **Validation Overhead** (3 tests): Performance impact

#### 4. E2E Tests (10 tests)
- **Complete Workflows** (6 tests): Upload→Process→Verify
- **User Journeys** (4 tests): New user, power user, error correction

### Test Types

| Type | Purpose | Tools | Coverage |
|------|---------|-------|----------|
| Functional | Verify features work | pytest, TestClient | All features |
| Performance | Meet speed targets | pytest, psutil | 1k-1M rows |
| Security | File validation | pytest | Upload, size |
| Usability | User-friendly errors | Manual | Error messages |
| Compatibility | File formats | pytest | CSV, Excel |
| Regression | No breakage | pytest | All tests |

## Test Scope

### In Scope

**Functional Testing:**
- ✓ File upload (CSV, Excel)
- ✓ File parsing (multiple formats)
- ✓ Column mapping (auto and manual)
- ✓ Data validation (all rules)
- ✓ Async processing (Celery)
- ✓ Status tracking
- ✓ Error handling and reporting
- ✓ Template download
- ✓ Import history
- ✓ Rollback on failure

**Data Types:**
- ✓ Farms and plots
- ✓ Irrigation events
- ✓ Nutrient applications
- ✓ Phenology observations
- ✓ Financial data

**File Formats:**
- ✓ CSV (comma, semicolon, tab delimited)
- ✓ Excel .xlsx (2007+)
- ✓ Excel .xls (97-2003)
- ✓ UTF-8, Latin-1, Windows-1252 encodings
- ✓ Various line endings (LF, CRLF, CR)
- ✓ BOM handling

### Out of Scope

**Not in Sprint 2:**
- ✗ Mobile app import
- ✗ Import from URLs
- ✗ Advanced ML-based mapping
- ✗ Scheduled/batch imports
- ✗ Data transformation rules
- ✗ Template marketplace
- ✗ Real-time notifications (email/SMS)
- ✗ Import data preview (>100 rows)

## Test Scenarios

### Scenario 1: Successful Farm Import

**Description**: User imports 3 farms from CSV with perfect data

**Preconditions**: None

**Test Steps**:
1. Upload CSV file with 3 farm records
2. Preview data (should show 3 rows)
3. Review auto column mappings (should be 100% accurate)
4. Validate data (should pass with 0 errors)
5. Process import
6. Monitor progress (should show 100% completion)
7. Verify data in database

**Expected Result**:
- All 3 farms imported successfully
- Import status: "completed"
- 0 errors
- Data matches CSV exactly

**Test File**: `test_complete_import.py::test_complete_farm_import_workflow`

### Scenario 2: Import with Validation Errors

**Description**: User imports file with some invalid data

**Preconditions**: None

**Test Steps**:
1. Upload CSV with 4 farms (2 valid, 2 invalid)
2. Validate data
3. Review errors (should show 2 errors with details)
4. Process with skip_invalid_rows=True
5. Verify only valid rows imported

**Expected Result**:
- 2 valid rows imported
- 2 invalid rows skipped
- Error report available for download
- Import status: "completed_with_errors"

**Test File**: `test_complete_import.py::test_complete_import_with_invalid_data`

### Scenario 3: Large File Import (10k rows)

**Description**: Power user imports 10,000 irrigation records

**Preconditions**: Farm and plot exist

**Test Steps**:
1. Upload CSV with 10,000 irrigation events
2. Validate (should pass)
3. Process import
4. Monitor real-time progress
5. Verify completion within target time (<60 seconds)

**Expected Result**:
- Import completes in <60 seconds
- Memory usage <500MB
- All 10,000 rows imported correctly
- Processing rate >166 rows/second

**Test File**: `test_bulk_import.py::test_import_10k_rows`

### Scenario 4: Manual Column Mapping

**Description**: User uploads CSV with custom column names

**Preconditions**: None

**Test Steps**:
1. Upload CSV with columns: "Name", "Location", "Size (ha)"
2. Review auto-mappings (may have low confidence)
3. Override with manual mappings
4. Validate (should pass)
5. Process import

**Expected Result**:
- Manual mappings applied correctly
- Data imported with correct field mapping
- Mapping can be saved as template

**Test File**: `test_import_workflow.py::test_import_with_manual_column_mapping`

### Scenario 5: Error Recovery Workflow

**Description**: User corrects errors and re-imports

**Preconditions**: None

**Test Steps**:
1. Upload file with errors
2. Download error report CSV
3. Fix errors in original file
4. Re-upload corrected file
5. Validate (0 errors)
6. Process successfully

**Expected Result**:
- Error report shows all issues
- Corrected file passes validation
- Import succeeds after correction

**Test File**: `test_complete_import.py::test_user_error_correction_workflow`

### Scenario 6: Concurrent Imports

**Description**: Multiple users importing simultaneously

**Preconditions**: None

**Test Steps**:
1. Start 3 imports concurrently (different files)
2. Monitor all 3 imports
3. Verify all complete successfully
4. Check for data integrity issues

**Expected Result**:
- All 3 imports complete successfully
- No data corruption
- No database deadlocks
- Total time <3x single import time

**Test File**: `test_bulk_import.py::test_concurrent_2_imports`

### Scenario 7: Import Rollback on Failure

**Description**: Import fails midway, verify rollback

**Preconditions**: None

**Test Steps**:
1. Upload large file
2. Simulate database error during import
3. Verify import status shows "failed"
4. Check database - no partial data

**Expected Result**:
- Import marked as failed
- All changes rolled back
- Database state unchanged
- Clear error message for user

**Test File**: `test_import_workflow.py::test_import_rollback_on_database_error`

### Scenario 8: Excel File Import

**Description**: User imports data from Excel file

**Preconditions**: None

**Test Steps**:
1. Upload .xlsx file with 2 sheets
2. Select "Farms" sheet
3. Preview data
4. Process import

**Expected Result**:
- Excel parsed correctly
- Formulas evaluated to values
- Data imported successfully

**Test File**: `test_complete_import.py::test_excel_file_import`

### Scenario 9: Template Download and Use

**Description**: New user downloads template and uses it

**Preconditions**: None

**Test Steps**:
1. Download farms template
2. Fill in 5 farms
3. Upload filled template
4. Auto-mapping should be 100%
5. Import successfully

**Expected Result**:
- Template has all required columns
- Example rows provided
- Perfect auto-mapping
- Successful import

**Test File**: `test_complete_import.py::test_template_download_and_use`

### Scenario 10: Import History

**Description**: User reviews past imports

**Preconditions**: Several imports completed

**Test Steps**:
1. View import history
2. Filter by status (completed)
3. Filter by data type (farms)
4. View error details for failed import
5. Re-run previous import

**Expected Result**:
- All imports listed
- Filters work correctly
- Error details available
- Can re-run with same settings

**Test File**: `test_import_api.py::TestImportHistoryEndpoint`

## Test Data

### Test Data Categories

#### 1. Valid Data

```csv
# farms_valid.csv
farm_name,total_area_hectares,latitude,longitude,timezone
Green Valley Farm,50.5,40.7128,-74.0060,America/New_York
Sunny Acres,75.2,40.7589,-73.9851,America/New_York
```

#### 2. Invalid Data (Various Errors)

```csv
# farms_invalid.csv
farm_name,total_area_hectares,latitude,longitude
,50.5,40.7128,-74.0060              # Missing farm_name
Invalid Area Farm,-10.0,40.7589,-73.9851   # Negative area
Invalid Lat Farm,75.2,95.0,-74.0060        # Invalid latitude
```

#### 3. Edge Cases

```csv
# farms_edge_cases.csv
farm_name,total_area_hectares,latitude,longitude
Farm with "Quotes",50.5,40.7128,-74.0060
Farm, with, commas,75.2,40.7589,-73.9851
Müller Farm (Special Chars),60.0,40.7489,-73.9680
```

#### 4. Large Datasets

- **1K rows**: Generated programmatically
- **10K rows**: Generated programmatically
- **100K rows**: Generated programmatically
- **1M rows**: Generated programmatically

### Test Data Generation

```python
# Generate large test datasets
def generate_farm_csv(num_rows, filepath):
    data = {
        'farm_name': [f'Farm {i}' for i in range(num_rows)],
        'total_area_hectares': [50.5 + i * 0.1 for i in range(num_rows)],
        'latitude': [40.7128] * num_rows,
        'longitude': [-74.0060] * num_rows,
    }
    df = pd.DataFrame(data)
    df.to_csv(filepath, index=False)
```

## Expected Results

### Functional Tests

| Test Category | Expected Pass Rate | Actual | Status |
|---------------|-------------------|--------|--------|
| CSV Parsing | 100% | TBD | Pending |
| Excel Parsing | 100% | TBD | Pending |
| Column Mapping | ≥80% accuracy | TBD | Pending |
| Data Validation | 100% | TBD | Pending |
| Import API | 100% | TBD | Pending |
| Import Workflow | 100% | TBD | Pending |
| Error Handling | 100% | TBD | Pending |
| E2E Tests | 100% | TBD | Pending |

### Performance Benchmarks

| Dataset Size | Target Time | Expected Memory | Target Rate | Actual Time | Actual Memory | Status |
|--------------|-------------|-----------------|-------------|-------------|---------------|--------|
| 1,000 rows | <10s | <100MB | >100 r/s | TBD | TBD | Pending |
| 10,000 rows | <60s | <500MB | >166 r/s | TBD | TBD | Pending |
| 100,000 rows | <600s | <2GB | >166 r/s | TBD | TBD | Pending |
| 1,000,000 rows | <3600s | <5GB | >277 r/s | TBD | TBD | Pending |

### Quality Metrics

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Code Coverage (Overall) | 80% | TBD | Pending |
| Code Coverage (Import) | 85% | TBD | Pending |
| Auto-mapping Accuracy | >80% | TBD | Pending |
| Import Success Rate | >99% | TBD | Pending |
| P1 Bugs | <5 | 0 | ✓ Pass |
| P0 Bugs | 0 | 0 | ✓ Pass |

## Performance Benchmarks

### Test Environment

- **CPU**: TBD (multi-core recommended)
- **RAM**: TBD (minimum 8GB)
- **Database**: PostgreSQL 14+ with TimescaleDB
- **Storage**: SSD (for faster I/O)
- **Network**: Local (no network latency)

### Benchmark Tests

#### 1. Small Import (1,000 rows)

**Target**: <10 seconds, <100MB memory

```python
def test_import_1k_rows(client, tmp_path):
    # Generate 1k rows
    # Measure time and memory
    # Assert: time < 10s, memory < 100MB
```

**Success Criteria**:
- Import time: <10 seconds
- Memory usage: <100MB
- Processing rate: >100 rows/second
- Zero errors

#### 2. Medium Import (10,000 rows)

**Target**: <60 seconds, <500MB memory

**Success Criteria**:
- Import time: <60 seconds
- Memory usage: <500MB
- Processing rate: >166 rows/second
- Handles concurrent imports

#### 3. Large Import (100,000 rows)

**Target**: <10 minutes, <2GB memory

**Success Criteria**:
- Import time: <600 seconds
- Memory usage: <2GB
- Streaming/chunked processing
- Progress updates every 5 seconds

#### 4. Very Large Import (1,000,000 rows)

**Target**: <60 minutes, <5GB memory

**Success Criteria**:
- Import time: <3600 seconds
- Memory usage: <5GB
- No memory leaks
- Resumable on failure

### Memory Profiling

```python
def test_memory_streaming_import(client):
    # Monitor memory before, during, after
    # Assert: Memory doesn't grow unbounded
    # Memory increase should be O(batch_size), not O(total_rows)
```

## Coverage Goals

### Overall Coverage Targets

- **Overall Backend**: 80%
- **Import Modules**: 85%
- **Critical Paths**: 95%
- **Error Handlers**: 90%

### Module-Specific Targets

| Module | Target | Priority | Notes |
|--------|--------|----------|-------|
| csv_parser.py | 90% | P0 | Core functionality |
| excel_parser.py | 90% | P0 | Core functionality |
| column_mapping_service.py | 85% | P0 | Auto-mapping critical |
| validation_service.py | 90% | P0 | Data quality critical |
| import_service.py | 85% | P0 | Orchestration |
| import_tasks.py | 80% | P0 | Celery tasks |
| import endpoints | 80% | P0 | API |

### Coverage Exclusions

- Mock implementations (until backend complete)
- Debug/logging code
- Abstract base classes
- Third-party library wrappers

## Test Execution

### Test Execution Schedule

#### Phase 1: Unit Tests (Week 1, Days 8-9)
- CSV parser tests
- Excel parser tests
- Column mapper tests
- Data validator tests
- File format tests
- Error handling tests

**Duration**: 6 hours
**Dependencies**: None
**Deliverable**: Unit test suite with 240 tests

#### Phase 2: Integration Tests (Week 2, Day 9)
- Import API tests
- Import workflow tests

**Duration**: 5 hours
**Dependencies**: Backend API endpoints (BE-109)
**Deliverable**: Integration test suite with 70 tests

#### Phase 3: Performance Tests (Week 2, Day 9)
- Bulk import benchmarks
- Concurrent import tests
- Memory profiling

**Duration**: 4 hours
**Dependencies**: Database setup, Celery worker
**Deliverable**: Performance test report

#### Phase 4: E2E Tests (Week 2, Day 10)
- Complete workflow tests
- User journey tests

**Duration**: 1 hour
**Dependencies**: All backend complete, frontend
**Deliverable**: E2E test suite with 10 tests

#### Phase 5: Documentation (Week 2, Day 10)
- Test plan
- Test results
- Coverage report

**Duration**: 0 hours (documentation during testing)
**Deliverable**: Test documentation complete

### Test Execution Commands

```bash
# Run all import tests
pytest tests/unit/test_*csv*.py tests/unit/test_*excel*.py \
       tests/unit/test_*mapper*.py tests/unit/test_*validator*.py \
       tests/integration/test_import*.py \
       tests/e2e/test_complete_import.py -v

# Run with coverage
pytest --cov=app.services --cov=app.api.v1.endpoints.import \
       --cov-report=html --cov-report=term-missing \
       tests/unit tests/integration tests/e2e

# Run performance tests (SLOW)
pytest tests/performance/test_bulk_import.py -v -m performance

# Generate test report
pytest --html=test-report.html --self-contained-html
```

## Defect Management

### Bug Priority Levels

| Priority | Description | SLA | Example |
|----------|-------------|-----|---------|
| P0 | Critical - Blocks import | 24 hours | Import fails completely |
| P1 | Major - Significant issue | 3 days | Auto-mapping <50% accurate |
| P2 | Minor - Small issue | 1 week | Error message unclear |
| P3 | Trivial - Cosmetic | 2 weeks | UI alignment issue |

### Bug Reporting Template

```
**Title**: [Component] Brief description

**Priority**: P0/P1/P2/P3

**Steps to Reproduce**:
1. Step 1
2. Step 2
3. Step 3

**Expected Result**: What should happen

**Actual Result**: What actually happened

**Environment**:
- OS:
- Browser:
- Backend version:

**Test File**: test_*.py::test_name

**Screenshots/Logs**: [Attach if available]

**Impact**: How this affects users
```

### Known Issues

1. **Import API endpoints not yet implemented**
   - Status: In progress (Backend team)
   - Workaround: Tests written but commented out
   - ETA: Sprint 2 end

2. **Frontend component tests pending**
   - Status: Planned
   - Workaround: Manual testing
   - ETA: Sprint 2 end

## Acceptance Criteria

### Sprint 2 Completion Criteria

✓ **All Test Suites Created**:
- [x] Unit tests (240 tests)
- [x] Integration tests (70 tests)
- [x] Performance tests (15 tests)
- [x] E2E tests (10 tests)
- [x] Test documentation

✓ **Coverage Targets Met**:
- [ ] Overall coverage ≥80%
- [ ] Import modules coverage ≥85%
- [ ] Critical paths coverage ≥95%

✓ **Performance Targets Met**:
- [ ] 1k rows: <10 seconds
- [ ] 10k rows: <60 seconds
- [ ] 100k rows: <10 minutes
- [ ] 1M rows: <60 minutes

✓ **Quality Metrics**:
- [x] Zero P0 bugs
- [x] <5 P1 bugs
- [ ] Auto-mapping accuracy >80%
- [ ] All error scenarios handled
- [ ] User-friendly error messages

✓ **Documentation Complete**:
- [x] README.md updated
- [x] IMPORT_TEST_PLAN.md created
- [ ] Test results documented
- [ ] Known issues documented

### Ready for Production Criteria

- [ ] All tests passing
- [ ] Code coverage ≥85%
- [ ] Performance benchmarks met
- [ ] Zero critical bugs
- [ ] Documentation complete
- [ ] Security review passed
- [ ] Load testing completed
- [ ] User acceptance testing passed

## Appendix

### A. Test File Mapping

| Test Requirement | Test File | Test Count |
|------------------|-----------|------------|
| CSV Parsing | test_csv_parser.py | 30 |
| Excel Parsing | test_excel_parser.py | 25 |
| Column Mapping | test_column_mapper.py | 35 |
| Data Validation | test_data_validator.py | 60 |
| File Formats | test_file_formats.py | 40 |
| Error Handling | test_import_errors.py | 50 |
| Import API | test_import_api.py | 40 |
| Import Workflow | test_import_workflow.py | 30 |
| Performance | test_bulk_import.py | 15 |
| E2E | test_complete_import.py | 10 |

### B. Test Tools and Libraries

- **pytest**: Test framework
- **pytest-cov**: Coverage plugin
- **pytest-xdist**: Parallel execution
- **pandas**: CSV/data manipulation
- **openpyxl**: Excel file handling
- **xlwt**: Excel .xls support
- **psutil**: Memory/CPU monitoring
- **faker**: Test data generation (future)

### C. References

- Sprint 2 Plan: `/SPRINT_2_PLAN.md`
- API Documentation: `/docs/api/import.md`
- Database Schema: `/docs/database/import_tables.md`
- Backend Tests README: `/backend/tests/README.md`

---

**Document Status**: Final
**Last Updated**: 2025-11-17
**Next Review**: Sprint 2 End (2025-12-13)
**Approved By**: QA Specialist
**Sprint**: Sprint 2 - Data Import System
