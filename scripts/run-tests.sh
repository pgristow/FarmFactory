#!/bin/bash

###############################################################################
# FarmFactory Test Runner Script
#
# This script runs all tests for the FarmFactory project (backend + frontend)
# with various options for different test scenarios.
#
# Usage:
#   ./scripts/run-tests.sh [options]
#
# Options:
#   --all            Run all tests (backend + frontend)
#   --backend        Run backend tests only
#   --frontend       Run frontend tests only
#   --unit           Run unit tests only
#   --integration    Run integration tests only
#   --performance    Run performance tests only
#   --coverage       Run with coverage reporting
#   --watch          Run in watch mode (auto-rerun on changes)
#   --parallel       Run tests in parallel
#   --quick          Run quick tests only (skip slow tests)
#   --ci             Run in CI mode (no interactive prompts)
#   --help           Show this help message
#
# Examples:
#   ./scripts/run-tests.sh --all --coverage
#   ./scripts/run-tests.sh --backend --unit
#   ./scripts/run-tests.sh --frontend --watch
#
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default options
RUN_BACKEND=false
RUN_FRONTEND=false
TEST_TYPE="all"
WITH_COVERAGE=false
WATCH_MODE=false
PARALLEL=false
QUICK_MODE=false
CI_MODE=false

# Helper functions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

show_help() {
    cat << EOF
FarmFactory Test Runner

Usage: $0 [options]

Options:
  --all            Run all tests (backend + frontend)
  --backend        Run backend tests only
  --frontend       Run frontend tests only
  --unit           Run unit tests only
  --integration    Run integration tests only
  --performance    Run performance tests only
  --coverage       Run with coverage reporting
  --watch          Run in watch mode (auto-rerun on changes)
  --parallel       Run tests in parallel
  --quick          Run quick tests only (skip slow tests)
  --ci             Run in CI mode
  --help           Show this help message

Examples:
  $0 --all --coverage          # Run all tests with coverage
  $0 --backend --unit          # Run backend unit tests only
  $0 --frontend --watch        # Run frontend tests in watch mode
  $0 --quick --parallel        # Quick parallel test run

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --all)
            RUN_BACKEND=true
            RUN_FRONTEND=true
            shift
            ;;
        --backend)
            RUN_BACKEND=true
            shift
            ;;
        --frontend)
            RUN_FRONTEND=true
            shift
            ;;
        --unit)
            TEST_TYPE="unit"
            shift
            ;;
        --integration)
            TEST_TYPE="integration"
            shift
            ;;
        --performance)
            TEST_TYPE="performance"
            shift
            ;;
        --coverage)
            WITH_COVERAGE=true
            shift
            ;;
        --watch)
            WATCH_MODE=true
            shift
            ;;
        --parallel)
            PARALLEL=true
            shift
            ;;
        --quick)
            QUICK_MODE=true
            shift
            ;;
        --ci)
            CI_MODE=true
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# If no target specified, run all
if [ "$RUN_BACKEND" = false ] && [ "$RUN_FRONTEND" = false ]; then
    RUN_BACKEND=true
    RUN_FRONTEND=true
fi

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

# Track test results
BACKEND_RESULT=0
FRONTEND_RESULT=0

###############################################################################
# Backend Tests
###############################################################################

run_backend_tests() {
    print_header "Running Backend Tests"

    if [ ! -d "$BACKEND_DIR" ]; then
        print_error "Backend directory not found: $BACKEND_DIR"
        return 1
    fi

    cd "$BACKEND_DIR"

    # Check if virtual environment exists
    if [ ! -d "venv" ] && [ "$CI_MODE" = false ]; then
        print_warning "Virtual environment not found. Creating..."
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
    elif [ -d "venv" ]; then
        source venv/bin/activate
    fi

    # Build pytest command
    PYTEST_CMD="pytest"

    # Test type
    case $TEST_TYPE in
        unit)
            PYTEST_CMD="$PYTEST_CMD tests/unit"
            ;;
        integration)
            PYTEST_CMD="$PYTEST_CMD tests/integration"
            ;;
        performance)
            PYTEST_CMD="$PYTEST_CMD tests/performance -m performance"
            ;;
        all)
            PYTEST_CMD="$PYTEST_CMD tests"
            ;;
    esac

    # Add coverage if requested
    if [ "$WITH_COVERAGE" = true ]; then
        PYTEST_CMD="$PYTEST_CMD --cov=app --cov-report=term-missing --cov-report=html --cov-report=xml"
    fi

    # Add parallel execution if requested
    if [ "$PARALLEL" = true ]; then
        PYTEST_CMD="$PYTEST_CMD -n auto"
    fi

    # Quick mode (skip slow tests)
    if [ "$QUICK_MODE" = true ]; then
        PYTEST_CMD="$PYTEST_CMD -m 'not slow'"
    fi

    # Watch mode
    if [ "$WATCH_MODE" = true ]; then
        print_info "Running in watch mode (press Ctrl+C to stop)..."
        ptw -- -v
        return $?
    fi

    # Add verbose output
    PYTEST_CMD="$PYTEST_CMD -v"

    # Run tests
    print_info "Running: $PYTEST_CMD"
    echo ""

    if $PYTEST_CMD; then
        print_success "Backend tests passed"
        BACKEND_RESULT=0
    else
        print_error "Backend tests failed"
        BACKEND_RESULT=1
    fi

    # Display coverage report location
    if [ "$WITH_COVERAGE" = true ] && [ -d "htmlcov" ]; then
        echo ""
        print_info "Coverage report available at: $BACKEND_DIR/htmlcov/index.html"
    fi

    return $BACKEND_RESULT
}

###############################################################################
# Frontend Tests
###############################################################################

run_frontend_tests() {
    print_header "Running Frontend Tests"

    if [ ! -d "$FRONTEND_DIR" ]; then
        print_error "Frontend directory not found: $FRONTEND_DIR"
        return 1
    fi

    cd "$FRONTEND_DIR"

    # Check if node_modules exists
    if [ ! -d "node_modules" ] && [ "$CI_MODE" = false ]; then
        print_warning "Node modules not found. Installing..."
        npm install
    fi

    # Build test command
    TEST_CMD="npm run test --"

    # Add coverage if requested
    if [ "$WITH_COVERAGE" = true ]; then
        TEST_CMD="$TEST_CMD --coverage"
    fi

    # Watch mode
    if [ "$WATCH_MODE" = true ]; then
        print_info "Running in watch mode (press Ctrl+C to stop)..."
        npm run test
        return $?
    fi

    # Run tests
    print_info "Running: $TEST_CMD"
    echo ""

    if $TEST_CMD; then
        print_success "Frontend tests passed"
        FRONTEND_RESULT=0
    else
        print_error "Frontend tests failed"
        FRONTEND_RESULT=1
    fi

    # Display coverage report location
    if [ "$WITH_COVERAGE" = true ] && [ -d "coverage" ]; then
        echo ""
        print_info "Coverage report available at: $FRONTEND_DIR/coverage/index.html"
    fi

    return $FRONTEND_RESULT
}

###############################################################################
# Main Execution
###############################################################################

print_header "FarmFactory Test Suite"

# Start time
START_TIME=$(date +%s)

# Run backend tests
if [ "$RUN_BACKEND" = true ]; then
    run_backend_tests
    BACKEND_RESULT=$?
    echo ""
fi

# Run frontend tests
if [ "$RUN_FRONTEND" = true ]; then
    run_frontend_tests
    FRONTEND_RESULT=$?
    echo ""
fi

# End time
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

# Summary
print_header "Test Summary"

if [ "$RUN_BACKEND" = true ]; then
    if [ $BACKEND_RESULT -eq 0 ]; then
        print_success "Backend: PASSED"
    else
        print_error "Backend: FAILED"
    fi
fi

if [ "$RUN_FRONTEND" = true ]; then
    if [ $FRONTEND_RESULT -eq 0 ]; then
        print_success "Frontend: PASSED"
    else
        print_error "Frontend: FAILED"
    fi
fi

echo ""
print_info "Total duration: ${DURATION}s"

# Exit with appropriate code
if [ $BACKEND_RESULT -ne 0 ] || [ $FRONTEND_RESULT -ne 0 ]; then
    echo ""
    print_error "Some tests failed!"
    exit 1
else
    echo ""
    print_success "All tests passed!"
    exit 0
fi
