# crewai-primordia

Track your CrewAI costs with machine-readable receipts.

## Install

```bash
pip install crewai-primordia
```

## Usage

```python
from crewai import Crew, Agent, Task
from crewai_primordia import PrimordiaMeter

meter = PrimordiaMeter(agent_id="my-crew")

with meter:
    result = crew.kickoff()

print(f"Cost: ${meter.get_total_usd():.4f}")
```

## Links

- Kernel: https://clearing.kaledge.app
- Docs: https://primordia.dev
