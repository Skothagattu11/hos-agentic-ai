# Unused Files (nouse)

This folder contains files that were part of the development process but are not currently used in the active implementation.

## Files in this folder:

### `main_api_wrapper.py`
- **Purpose**: Windows Unicode wrapper for main_api.py
- **Status**: Not needed - Unicode issues resolved in main files
- **Safe to delete**: Yes

### `user_profile_mcp.py`
- **Purpose**: Alternative MCP implementation for user profile retrieval
- **Status**: Not used - `user_profile.py` is the active implementation
- **Safe to delete**: Yes, but keep for reference if MCP integration is needed later

### `memory_manager_supabase.py`
- **Purpose**: Alternative Supabase-specific memory manager
- **Status**: Not used - `memory_manager.py` with connection_factory handles both PostgreSQL and Supabase
- **Safe to delete**: Yes, functionality is covered by main memory manager

### `metric_analysis_agent.py`
- **Purpose**: Separate agent for metric analysis
- **Status**: Not used - functionality integrated into other agents
- **Safe to delete**: Yes

## Notes:
- These files were moved here during codebase cleanup on 2024-01-01
- They represent alternative implementations or deprecated approaches
- The active codebase uses the files in the main directory and health_agents/ folder
- If you need to restore any functionality, these files can serve as reference