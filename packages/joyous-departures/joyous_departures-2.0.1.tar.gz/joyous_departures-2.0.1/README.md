# Joyous Departures

Generate warm, heartfelt goodbye messages for email templates.

## Installation

```bash
pip install joyous-departures
# or
uv pip install joyous-departures
```

## Usage

```python
import asyncio
from joyous_departures import generate_goodbye

async def main():
    # Basic usage
    message = await generate_goodbye()
    print(message)  # "Wishing you a joyous day, Good Soul ❤️"

    # With custom name
    message = await generate_goodbye(template_args={"name": "Alice"})
    print(message)  # "May your path be filled with joy, Alice 🌻"

    # Without emojis
    message = await generate_goodbye(use_emojis=False)
    print(message)  # "Wishing you a joyous day, Good Soul"

asyncio.run(main())
```

## Synchronous Usage

```python
from joyous_departures import generate_goodbye_sync

message = generate_goodbye_sync(template_args={"name": "Alice"})
print(message)
```

## License

MIT

