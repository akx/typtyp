# typtyp

Convert Python types and type annotations to TypeScript type definitions.

## Features

- Convert dataclasses, TypedDict, enums, and Pydantic models to TypeScript
- Support for Python's standard typing primitives
- Rich type support (dates, UUIDs, complex collections, etc.)
- Simple API for declaring types for conversion

## Installation

```bash
pip install typtyp
```

## Usage

```python
from dataclasses import dataclass
from typing import List, Optional
import typtyp

@dataclass
class User:
    name: str
    email: str
    age: Optional[int] = None

@dataclass
class Team:
    name: str
    members: List[User]

# Create a world to collect types
world = typtyp.World()

# Add types to the world
world.add(User)
world.add(Team)

# Generate TypeScript
typescript_code = world.get_typescript()
print(typescript_code)
```

Output (approximately – you would want to run typtyp's output through a formatter of your liking):

```typescript
export interface User {
  name: string;
  email: string;
  age: number | null;
}

export interface Team {
  name: string;
  members: User[];
}
```
