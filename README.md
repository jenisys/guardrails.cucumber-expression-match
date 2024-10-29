guardrails.cucumber-expression-match
===============================================================================

| Developed by        | jenisys        |
|---------------------|----------------|
| Date of development | 2024-06-22     |
| Last updated        | 2024-10-30     |
| Validator type      | rule-following |
| License             | MIT            |
| Input/Output        | Output         |


## Description

This [guardrails] validator provides support for [cucumber-expressions],
a simpler, more readable "regular expression" dialect with the following features:

* Supports built-in `parameter_type`(s) for common types, like: `{int}`, `{float}`, ...
* Supports user-defined `parameter_type`(s) with own `regular expressions`,
  type conversion and transformation
* Supports alternative text, like: `apple/orange` (matches: `apple` or `orange`)
* Support optional text, like: `apple(s)` (matches: `apple`, `apples`)

This validator is similar to [regex_match], but often easier to use because:

* [cucumber-expressions] are often more readable
  (especially for people that are less familiar with `regular expressions`)
* less error-prone, because readable placeholders are used instead of complex regular expression.

SEE ALSO:

* [cucumber-expressions]
* [guardrails]

[cucumber-expressions]: https://github.com/cucumber/cucumber-expressions
[guardrails]: https://github.com/guardrails-ai/guardrails
[regex_match]: https://github.com/guardrails-ai/regex_match

### Intended Use

Check if text follows a specified schema (described by this cucumber-expression).

### Requirements

* Dependencies:

  - `guardrails-ai>=0.5.15` (up-to: `0.6.0`)
  - `cucumber-expressions>=17.1.0`
  - `rstr>=3.2.2`

* Development dependencies:

  - `pytest`
  - `pyright`
  - `ruff`
  - `codespell`


## Installation

```bash
$ guardrails hub install hub://guardrails/cucumber_expression_match
```

## Usage Examples

### Validating string output via Python

In this example, we apply the validator to a string output generated by an LLM.

```python
# -- FILE: use_guardrails_cucumber_expression_match.py
from guardrails import Guard, OnFailAction
from guardrails.hub import CucumberExpressionMatch
from cucumber_expressions.parameter_type import ParameterType

# -- SETUP GUARD:
positive_number = ParameterType("positive_number", regexp=r"\d+", type=int)
guard = Guard().use(CucumberExpressionMatch,
    expression="I buy {positive_number} apple(s)/banana(s)/orange(s)",
    parameter_types=[positive_number],
    on_fail=OnFailAction.EXCEPTION
)

# -- VALIDATOR PASSES: Good cases
guard.validate("I buy 0 apples")    # Guardrail passes
guard.validate("I buy 1 apple")     # Guardrail passes
guard.validate("I buy 1 banana")    # Guardrail passes
guard.validate("I buy 2 bananas")   # Guardrail passes
guard.validate("I buy 1 orange")    # Guardrail passes
guard.validate("I buy 3 oranges")   # Guardrail passes

# -- VALIDATOR FAILS: Bad cases
try:
    guard.validate("I buy 2 melons")    # Guardrail fails: Unexpected fruit
    guard.validate("I buy -10 apples")  # Guardrail fails: Negative number
except Exception as e:
    print(e)
```

## More Information

RELATED:

* [parse_type.TypeBuilder]: Compose `parse-functions` and `regular expression` patterns for common use cases
* [TypeBuilder for cucumber-expressions] (as part of: [behave])


[behave]: https://github.com/behave/behave
[parse_type.TypeBuilder]: https://github.com/jenisys/parse_type
[TypeBuilder for cucumber-expressions]: https://github.com/behave/behave/blob/main/behave/cucumber_expression.py#L124
