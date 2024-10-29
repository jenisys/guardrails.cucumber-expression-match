# -*- coding: UTF-8 -*-
# SPDX-License-Identifier: MIT
# COPYRIGHT: (c) 2024-now jenisys
#   CreatedBy: jenisys
#   Created:   2024-06-22
# SEE: https://spdx.org/licenses/MIT.html
"""
This module provides a ``CucumberExpressionMatch`` class,
a simple validator of [cucumber-expressions] for [guardrails].

[cucumber-expressions]: https://github.com/cucumber/cucumber-expressions
[guardrails]: https://github.com/guardrails-ai/guardrails
"""
# BASED ON: https://github.com/guardrails-ai/validator-template

from typing import Any, Callable, Dict, List, Optional
from cucumber_expressions.expression import CucumberExpression
from cucumber_expressions.parameter_type import ParameterType
from cucumber_expressions.parameter_type_registry import ParameterTypeRegistry
from guardrails import OnFailAction
from guardrails.validator_base import (
    FailResult,
    PassResult,
    ValidationResult,
    Validator,
    register_validator,
)
import rstr
import pytest


# -----------------------------------------------------------------------------
# PACKAGE METADATA
# -----------------------------------------------------------------------------
__version__ = "0.3.0"
__license__ = "MIT"


# -----------------------------------------------------------------------------
# GUARDRAILS VALIDATOR
# -----------------------------------------------------------------------------
@register_validator(name="guardrails/cucumber_expression_match", data_type="string")
class CucumberExpressionMatch(Validator):
    r"""
    # Overview

    | Developed by        | jenisys        |
    |---------------------|----------------|
    | Date of development | 2024-06-22     |
    | Last updated        | 2024-10-30     |
    | Validator type      | rule-following |
    | License             | MIT            |
    | Input/Output        | Output         |

    # Description

    This [guardrails] validator provides support for [cucumber-expressions],
    a simpler, more readable "regular expression" dialect with the following features:

    * Supports built-in `parameter_type`(s) for common types, like: `{int}`, `{float}`, ...
    * Supports user-defined `parameter_type`(s) with own `regular expressions`,
      type conversion and transformation
    * Supports alternative text, like: `apple/orange` (matches: `apple` or `orange`)
    * Support optional text, like: `apple(s)` (matches: `apple`, `apples`)

    This validator is similar to [regex_match],
    but often easier to use because:

    * [cucumber-expressions] are often more readable
      (especially for people that are less familiar with `regular expressions`)
    * less error-prone, because a readable placeholder(s) are used for the complex regular expression.

    SEE ALSO:

    * [cucumber-expressions]
    * [guardrails]

    [cucumber-expressions]: https://github.com/cucumber/cucumber-expressions
    [guardrails]: https://github.com/guardrails-ai/guardrails
    [regex_match]: https://github.com/guardrails-ai/regex_match

    ## Intended Use

    Check if text follows a specified schema (described by this cucumber-expression).

    ## Requirements

    * Dependencies:
        - guardrails-ai>=0.5.15
        - cucumber-expressions>=17.1.0
        - rstr>=3.2.2

    * Dev Dependencies:
        - pytest
        - pyright
        - ruff
        - codespell


    # Installation

    ```bash
    $ guardrails hub install hub://guardrails/cucumber_expression_match
    ```

    # Usage Examples

    ## Validating string output via Python

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
    """  # noqa

    def __init__(
        self,
        expression: str,
        parameter_types: Optional[List[ParameterType]] = None,
        on_fail: Optional[Callable] = None,
    ):
        """Initializes a new instance of the CucumberExpressionMatch class.

        **Key Properties**

            | Property                      | Description                                             |
            | ----------------------------- | ------------------------------------------------------- |
            | Name for `format` attribute   | `jenisys/guardrails.cucumber_expression_match`          |
            | Supported data types          | `string`                                                |
            | Programmatic fix              | Generate a string that matches this cucumber-expression |

        Args:
            expression (str): Cucumber expression to use (as string).
            parameter_types (Optional[List[ParameterType]]): Parameter types to use (optional).
            on_fail`** *(str, Callable)*: The policy to enact when a validator fails.
        """
        parameter_types = parameter_types or []
        super().__init__(on_fail=on_fail)
        self._expression = expression
        self._parameter_type_registry = ParameterTypeRegistry()
        for parameter_type in parameter_types:
            self._parameter_type_registry.define_parameter_type(parameter_type)

    def validate(self, value: Any, metadata: Optional[Dict] = {}) -> ValidationResult:
        """Validates that {fill in how you validator interacts with the passed value}.

        Args:
            value (Any): The value to validate.
            metadata (Dict): The metadata to validate against.

        Returns:
            ValidationResult: The validation result (PassResult or FailResult).
        """
        this_expression = CucumberExpression(self._expression,
                                             self._parameter_type_registry)
        matched = this_expression.match(value)
        if matched is None:
            fix_string = rstr.xeger(this_expression.regexp)
            return FailResult(
                error_message=f"Result must match: {self._expression}",
                fix_value=fix_string,
            )

        # -- VALIDATION-PASSED: "value" matches this cucumber-expression.
        return PassResult()


# -----------------------------------------------------------------------------
# TEST SUITE
# -----------------------------------------------------------------------------
# RUN TESTS WITH: pytest -rP ./cucumber_expression_match.py
class TestCucumberExpressionMatch:
    EXPRESSION = "I buy {positive_number} apple(s)/banana(s)/orange(s)"

    @pytest.mark.parametrize("good_text", [
        "I buy 0 apples",
        "I buy 1 apple",
        "I buy 1 banana",
        "I buy 2 bananas",
        "I buy 1 orange",
        "I buy 3 oranges",
    ])
    def test_validate_on_success(self, good_text):
        positive_number = ParameterType("positive_number", regexp=r"\d+", type=int)
        validator = CucumberExpressionMatch(self.EXPRESSION,
                                            parameter_types=[positive_number],
                                            on_fail=OnFailAction.EXCEPTION)
        result = validator.validate(good_text)
        assert isinstance(result, PassResult) is True

    @pytest.mark.parametrize("bad_text, reason", [
        ("I buy 2 melons", "Unexpected fruit"),
        ("I buy -10 apples", "Negative number"),
    ])
    def test_validate_on_failure(self, bad_text, reason):
        positive_number = ParameterType("positive_number", regexp=r"\d+", type=int)
        validator = CucumberExpressionMatch(self.EXPRESSION,
                                            parameter_types=[positive_number],
                                            on_fail=OnFailAction.EXCEPTION)
        result = validator.validate(bad_text)
        assert isinstance(result, FailResult) is True
        assert result.error_message == f"Result must match: {self.EXPRESSION}"
        print(f"fix_value: {result.fix_value};")
