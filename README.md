# CropGuard

CropGuard is a cautious crop-health assistant that follows the same pattern as the Weekend Wizard project but uses crop knowledge, local tools, and grounded guidance.

## Version 1

- Uses a targeted route for prevention and non-diagnosis questions.
- Validates crop and symptom inputs before searching the knowledge base.
- Searches known disease patterns in the crop JSON files.
- Uses weather only as context, not as a stand-alone diagnosis.
- Produces a hedged answer grounded in the returned tool results.

## Project layout

- `cropguard/knowledge/` contains crop knowledge in JSON.
- `cropguard/mcp_server/tools/` contains tool implementations.
- `cropguard/agent/` contains the router, guard logic, and CLI loop.
- `tests/` contains the regression checks.

## Example usage

```bash
python -m cropguard.agent.agent_cropguard --crop tomato --location Nashik "My tomato leaves have dark rings with yellow edges"
```
