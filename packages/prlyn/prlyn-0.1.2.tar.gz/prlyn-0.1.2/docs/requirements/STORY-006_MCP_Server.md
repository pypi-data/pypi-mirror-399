# STORY-006: MCP Server & Deployment

## Description
Implement the MCP Server interface and ensure `uvx` compatibility for zero-install execution.

## Acceptance Criteria
- [ ] **MCP Server Implementation**:
    - [ ] Exposes `analyze_prompt` tool/resource.
    - [ ] Implements MCP protocol standard.
- [ ] **uvx Compatibility**:
    - [ ] `pyproject.toml` correctly configured for `uv` and `uvx`.
    - [ ] Executable entry point works via `uvx plint`.
- [ ] **CI/CD**:
    - [ ] Build workflow verifies `uvx` run.

## Technical Notes
- See REQ-001 Change 10.
- Usage: `uvx plint analyze "my prompt"` or connect via Claude Desktop.
