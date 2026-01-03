import pandas as pd


class Range:
    def __init__(self, start, end, inclusive=(True, True)):
        """
        Represents a range of value from start to end.
        :param start: lower bound of the range
        :param end: upper bound of the range
        :param inclusive: bool or tuple of bool (start_inclusive, end_inclusive) representing whether the bounds are
            inclusive or not
        """
        if start > end:
            raise ValueError("start must be less than or equal to end")
        self.start = start
        self.end = end

        if isinstance(inclusive, bool):
            self.inclusive = (inclusive, inclusive)
        elif isinstance(inclusive, tuple) and len(inclusive) == 2:
            self.inclusive = tuple(inclusive)
        else:
            raise ValueError("inclusive must be a bool or a tuple of two bools")

    def __contains__(self, item):
        if self.inclusive[0]:
            start_check = item >= self.start
        else:
            start_check = item > self.start

        if self.inclusive[1]:
            end_check = item <= self.end
        else:
            end_check = item < self.end

        return start_check and end_check

    def complement(self):
        """
        Get the complement of the range.

        Returns:
            A list of Range objects representing the complement of the current range.
        """
        # TODO 10/05/2025 Improve : avoid returning empty range ]-inf, -inf[ and ]inf, inf[
        start_inclusive = self.inclusive[0]
        end_inclusive = self.inclusive[1]
        return [Range(float('-inf'), self.start, inclusive=(False, not start_inclusive)),
                Range(self.end, float('inf'), inclusive=(not end_inclusive, False))]

    def is_compatible_with_type(self, type):
        """
        Check if the range is compatible with the given data type.
        :param type: data type to check compatibility with
        :return: True if compatible, False otherwise
        """
        if isinstance(self.start, type):
            return True

        if pd.api.types.is_numeric_dtype(type):
            return pd.api.types.is_numeric_dtype(type(self.start))

        if pd.api.types.is_datetime64_any_dtype(type):
            return isinstance(self.start, pd.Timestamp) and isinstance(self.end, pd.Timestamp)

        if isinstance(type, pd.CategoricalDtype) or pd.api.types.is_object_dtype(type):
            return isinstance(self.start, type) and isinstance(self.end, type)

        return False

    def __repr__(self):
        l_bracket = "[" if self.inclusive[0] else "("
        r_bracket = "]" if self.inclusive[1] else ")"
        return f"{l_bracket}{self.start}, {self.end}{r_bracket}"
