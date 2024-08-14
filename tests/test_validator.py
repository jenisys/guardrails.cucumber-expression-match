from cucumber_expression_match import CucumberExpressionMatch
from cucumber_expression_match import ParameterType
from guardrails import Guard, OnFailAction
from guardrails.errors import ValidationError
from guardrails.guard import ValidationOutcome
from guardrails.validator_base import PassResult, FailResult
import pytest


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
        ("I buy 2 melons", "CASE: Unexpected fruit"),
        ("I buy -10 apples", "CASE: Negative number"),
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

    @staticmethod
    def assert_parse_is_ok(result, input_text):
        assert isinstance(result, ValidationOutcome) is True
        assert result.validated_output == input_text
        assert result.validation_passed is True
        assert result.error is None

    @pytest.mark.parametrize("good_text", [
        "I buy 0 apples",
        "I buy 1 apple",
        "I buy 1 banana",
        "I buy 2 bananas",
        "I buy 1 orange",
        "I buy 3 oranges",
    ])
    def test_parse_on_success(self, good_text):
        positive_number = ParameterType("positive_number", regexp=r"\d+", type=int)
        guard = Guard().use(CucumberExpressionMatch,
            expression=self.EXPRESSION,
            parameter_types=[positive_number],
            on_fail=OnFailAction.EXCEPTION
        )
        result = guard.parse(good_text)
        self.assert_parse_is_ok(result, good_text)

    @pytest.mark.parametrize("bad_text, reason", [
        ("I buy 2 melons", "CASE: Unexpected fruit"),
        ("I buy -10 apples", "CASE: Negative number"),
    ])
    def test_parse_on_failure(self, bad_text, reason):
        positive_number = ParameterType("positive_number", regexp=r"\d+", type=int)
        guard = Guard().use(CucumberExpressionMatch,
            expression=self.EXPRESSION,
            parameter_types=[positive_number],
            on_fail=OnFailAction.EXCEPTION
        )
        with pytest.raises(ValidationError) as exc_info:
            _result = guard.parse(bad_text)
        expected = f"Validation failed for field with errors: Result must match: {self.EXPRESSION}"
        assert str(exc_info.value) == expected
