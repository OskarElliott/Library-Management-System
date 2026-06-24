# code conventions

deliberate standards for this project. the point is code i can read back and defend
in a viva, written in my own voice. these align with the ib cs course text
(hodder, baumgarten/ganea/turland), chapters b2-b3.

## complexity
- strong a-level / ib student level, not senior-engineer. no metaclasses, deep
  decorator stacks, dependency-injection containers, async unless needed, or
  one-liners that hide several steps.
- boring and idiomatic beats clever. if there's a fancier way, note it as a future
  improvement, don't build it.

## comments
- lowercase, no trailing full stop, casual and short
- e.g. `# bubble sort algorithm` not `# Bubble sort algorithm.`
- comment the why, not the what; skip comments on obvious lines
- no big docstrings, no comments defending design choices, no em-dashes
- a one-line note above a tricky bit is plenty

## naming
- snake_case for functions, methods, variables, and object instances
- PascalCase for classes; a class name is a singular noun for the entity (Book, Loan, Student)
- methods are named as verbs for the action they do (calculate_fine, can_borrow)
- collections are named as the plural of what they hold (active_loans, bank_accounts)
- constants in UPPER_SNAKE_CASE
- refer to class (static) variables through the class name: ClassName.next_id
- simple descriptive names; no single letters except loop counters

## oop and encapsulation
- sketch a uml class diagram before coding the class (name / attributes+types /
  methods+signatures). it's the blueprint and doubles as design evidence.
- one class = one entity with a single responsibility
- constructor is __init__(self, ...); self is the mandatory first parameter and
  prefixes every instance variable and method
- __str__(self) for a readable string form
- keep instance variables private (underscore prefix) where possible; expose them
  through accessor/mutator methods (get_x / set_x) only where outside code needs access
- single underscore _x means internal use; treat underscore-prefixed members as
  private for this course and don't bypass them
- methods are public if outside code calls them; internal helpers are private
- (aware: idiomatic python often uses @property instead of get_/set_ — note as future work)

## scope
- prefer local variables over globals; globals cause side effects and are hard to debug
- pass values in as parameters and return them out rather than reaching for shared state

## sql / db
- direct sqlite3, no orm
- parameterised queries everywhere, never string-concatenated values
- foreign keys enabled per connection (PRAGMA foreign_keys = ON)

## money
- all amounts in PLN
