# InvenTree MCP Testing Implementation Checklist

This checklist guides the implementation of the test suite as defined in [TEST_STRATEGY.md](./TEST_STRATEGY.md).

## Phase 1: Setup (Estimated: 30 minutes)

- [ ] Create `tests/` directory structure
  ```bash
  mkdir -p tests/{unit,mcp_client,integration}
  touch tests/__init__.py
  touch tests/unit/__init__.py
  touch tests/mcp_client/__init__.py
  touch tests/integration/__init__.py
  ```

- [ ] Update `pyproject.toml` with test dependencies and configuration
  - [ ] Add `[project.optional-dependencies]` dev section
  - [ ] Add `[tool.pytest.ini_options]` section
  - [ ] Add markers: `unit`, `mcp_client`, `integration`

- [ ] Install test dependencies
  ```bash
  uv pip install -e ".[dev]"
  ```

- [ ] Create `tests/conftest.py` with shared fixtures
  - [ ] `mock_inventree_client` fixture
  - [ ] `mcp_server_with_mock_client` fixture
  - [ ] `sample_part_data` fixture
  - [ ] `sample_purchase_order_data` fixture
  - [ ] `inventree_connection_params` fixture
  - [ ] `mcp_server_with_real_client` fixture
  - [ ] `assert_mcp_tool_response` helper function

## Phase 2: Unit Tests (Estimated: 1 hour)

- [ ] Create `tests/unit/test_client.py`
  - [ ] `test_client_initialization`
  - [ ] `test_client_requires_url`
  - [ ] `test_client_requires_token`

- [ ] Create `tests/unit/test_utils.py`
  - [ ] `test_json_serialization`
  - [ ] `test_json_handles_lists`

- [ ] Create `tests/unit/test_validation.py`
  - [ ] Add validation tests as needed

- [ ] Run unit tests to verify setup
  ```bash
  pytest -m "unit" -v
  ```

## Phase 3: MCP Client Tests - System Tool (Estimated: 30 minutes)

- [ ] Create `tests/mcp_client/test_system_tool.py`
  - [ ] `test_system_status_via_mcp`
  - [ ] `test_system_tool_registration`

- [ ] Run to verify MCP testing infrastructure works
  ```bash
  pytest tests/mcp_client/test_system_tool.py -v
  ```

## Phase 4: MCP Client Tests - Part Tool (Estimated: 1 hour)

- [ ] Create `tests/mcp_client/test_part_tool.py`
  - [ ] `test_part_list_via_mcp`
  - [ ] `test_part_get_via_mcp`
  - [ ] `test_part_create_via_mcp`
  - [ ] `test_part_search_via_mcp`
  - [ ] `test_part_tool_registration`

- [ ] Update `mock_inventree_client` fixture with additional part methods
  - [ ] `part_update`
  - [ ] `part_delete`

- [ ] Run part tool tests
  ```bash
  pytest tests/mcp_client/test_part_tool.py -v
  ```

## Phase 5: MCP Client Tests - Stock Tool (Estimated: 45 minutes)

- [ ] Create `tests/mcp_client/test_stock_tool.py`
  - [ ] `test_stock_list_via_mcp`
  - [ ] `test_stock_get_via_mcp`
  - [ ] `test_stock_filter_by_part`

- [ ] Update `mock_inventree_client` fixture with stock methods
  - [ ] `stock_get`

- [ ] Run stock tool tests
  ```bash
  pytest tests/mcp_client/test_stock_tool.py -v
  ```

## Phase 6: MCP Client Tests - Purchase Order Tool (Estimated: 45 minutes)

- [ ] Create `tests/mcp_client/test_purchase_tool.py`
  - [ ] `test_purchase_order_list_via_mcp`
  - [ ] `test_purchase_order_get_via_mcp`
  - [ ] `test_purchase_order_create_via_mcp`

- [ ] Update `mock_inventree_client` fixture with purchase methods
  - [ ] `purchase_order_get`
  - [ ] `purchase_order_create`

- [ ] Run purchase tool tests
  ```bash
  pytest tests/mcp_client/test_purchase_tool.py -v
  ```

## Phase 7: Integration Tests - Setup (Estimated: 1 hour)

- [ ] Set up test InvenTree instance (choose one):
  - [ ] Option A: Local Docker container
  - [ ] Option B: Dedicated test server
  - [ ] Option C: CI/CD test environment

- [ ] Create `.env.test` file with test credentials
  ```
  INVENTREE_URL=http://localhost:8000
  INVENTREE_TOKEN=your-test-token
  ```

- [ ] Verify connection
  ```bash
  export $(cat .env.test | xargs)
  curl -H "Authorization: Token $INVENTREE_TOKEN" $INVENTREE_URL/api/
  ```

## Phase 8: Integration Tests - Implementation (Estimated: 1.5 hours)

- [ ] Create `tests/integration/test_system_integration.py`
  - [ ] `test_system_status_real_api`

- [ ] Create `tests/integration/test_part_integration.py`
  - [ ] `test_part_list_real_api`
  - [ ] `test_part_search_real_api`
  - [ ] `test_part_create_real_api` (skipped by default)

- [ ] Create `tests/integration/test_stock_integration.py`
  - [ ] `test_stock_list_real_api`

- [ ] Create `tests/integration/test_purchase_integration.py`
  - [ ] `test_purchase_order_list_real_api`
  - [ ] `test_purchase_order_create_real_api` (skipped by default)

- [ ] Run integration tests
  ```bash
  export $(cat .env.test | xargs)
  pytest -m "integration" -v
  ```

## Phase 9: CI/CD Setup (Optional, Estimated: 2 hours)

- [ ] Create `.github/workflows/test.yml`
  - [ ] Job: `unit-tests` (runs on every push)
  - [ ] Job: `mcp-client-tests` (runs on every push)
  - [ ] Job: `integration-tests` (runs on PR/main only)

- [ ] Add GitHub secrets
  - [ ] `INVENTREE_TEST_TOKEN`

- [ ] Test CI/CD pipeline
  - [ ] Push to test branch
  - [ ] Verify all jobs pass

## Phase 10: Documentation & Cleanup (Estimated: 30 minutes)

- [ ] Update README.md with testing section (already done ✓)

- [ ] Add test coverage reporting (optional)
  ```bash
  pytest --cov=inventree_mcp --cov-report=html
  ```

- [ ] Review all tests pass
  ```bash
  pytest -v
  ```

- [ ] Document any test environment requirements

- [ ] Add troubleshooting section to TEST_STRATEGY.md if needed

## Verification Checklist

Before marking as complete, verify:

- [ ] All unit tests pass: `pytest -m "unit" -v`
- [ ] All MCP client tests pass: `pytest -m "mcp_client" -v`
- [ ] Integration tests skip gracefully without credentials
- [ ] Integration tests pass with test credentials: `pytest -m "integration" -v`
- [ ] Full suite passes: `pytest -v`
- [ ] Test coverage is reasonable (aim for 70%+)
- [ ] All tests have clear docstrings
- [ ] No hardcoded credentials in test files
- [ ] Tests run in reasonable time:
  - Unit: < 5 seconds total
  - MCP Client: < 15 seconds total
  - Integration: < 60 seconds total

## Estimated Total Time

- **Minimum** (Phases 1-6): ~4-5 hours
- **With Integration** (Phases 1-8): ~7-9 hours
- **Full Implementation** (All phases): ~11-13 hours

## Notes

- Start with unit and MCP client tests (can be done without InvenTree instance)
- Integration tests can be added later when test environment is ready
- Each phase is independently testable
- Can be spread across multiple sessions

## Questions During Implementation?

Refer to:
1. [TEST_STRATEGY.md](./TEST_STRATEGY.md) - Detailed strategy and code examples
2. [FastMCP test utilities](https://github.com/jlowin/fastmcp) - `run_server_async` documentation
3. [pytest-asyncio docs](https://pytest-asyncio.readthedocs.io/) - Async test patterns
