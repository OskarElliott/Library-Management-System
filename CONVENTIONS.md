# code conventions

deliberate standards for this project. the point is code i can read back and defend
in a viva, written in my own voice.

## complexity
- strong a-level / ib student level, not senior-engineer. no metaclasses, deep
  decorator stacks, dependency-injection containers, async unless needed, or
  one-liners that hide several steps.
- boring and idiomatic beats clever. if there's a fancier way, note it as a future
  improvement, don't build it.

## COMMENT STYLE (past AI output failed here — enforce this):
- lowercase, no trailing full stop, casual and short. e.g. `# bubble sort algorithm` not `# Bubble sort algorithm.`
- minimal comments; comment the why, not the what; skip obvious lines
- no big docstrings, no comments defending architecture choices, no em-dashes
- a one-line note above a function only if it isn't obvious; brief notes above genuinely tricky lines only
- default to few or no comments so I add the explanatory layer myself; prefer code I type over big blocks to paste

## naming
- simple, descriptive names; no single letters except loop counters
- snake_case for functions and variables, PascalCase for classes

## sql / db
- direct sqlite3, no orm
- parameterised queries everywhere, never string-concatenated values
- foreign keys enabled per connection (PRAGMA foreign_keys = ON)

## money
- all amounts in PLN
