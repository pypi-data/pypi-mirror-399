import math

from cp_based_fair_maker.metrics.dataset_metric import DatasetMetric
from cp_based_fair_maker.utils.range import Range
from cp_based_fair_maker.metrics.constants import FAIR_SCORE_IDEAL, FAIR_SCORE_MIN, FAIR_SCORE_MAX


class FairScore(DatasetMetric):
    """Class for computing fairness scores for datasets."""

    # TODO 10/05/2025 Add support to numeric ranges in groups identification
    #   Add a dict : {columns: [Range]}
    def __init__(self, dataset, protected_attributes=None):
        super(FairScore, self).__init__(dataset, None, [], [])

        if protected_attributes is None:
            protected_attributes = []

        if not isinstance(protected_attributes, list):
            raise ValueError("protected_attributes must be a list")

        # Check if the protected attributes are defined as list of strings or list of lists of strings and if all the
        # attributes are present in the dataset
        for i, attr in enumerate(protected_attributes):
            if isinstance(attr, str):
                if attr not in dataset.df.columns:
                    raise ValueError(f"protected_attributes[{i}] column must be present in the dataset.")
            elif isinstance(attr, list):
                if not all(isinstance(a, str) for a in attr):
                    raise ValueError(f"protected_attributes[{i}] must be a list of strings.")
                if not set(attr).issubset(dataset.df.columns):
                    raise ValueError(f"protected_attributes[{i}] columns must be present in the dataset.")

        self.protected_attributes = protected_attributes # TODO 10/05/2025 Removes duplicates

    def compute(self, **kwargs):
        """
        Compute the fairness score for the dataset.

        Returns:
            float: Fairness score for the dataset.
        """
        fair_score = 0
        scores = []
        for columns in self.protected_attributes:
            c_score = self.column_score(columns)
            fair_score += c_score
            scores.append((columns, c_score / len(self.protected_attributes)))
        return fair_score / len(self.protected_attributes)

    def column_score(self, columns):
        """
        Compute the fairness score for the specified columns.

        Args:
            columns (str or list): Columns to compute the score for.
                Multiple columns can be specified as a list, and then considered as a unique group definition.

        Returns:
            float: Fairness score for the specified columns.
        """
        if isinstance(columns, str):
            columns = [columns]

        # Check if the columns are defined as list of strings
        if not isinstance(columns, list):
            raise ValueError("columns must be a string or a list of strings")
        if not all(isinstance(col, str) for col in columns):
            raise ValueError("columns must be a string or a list of strings")

        # Check if the columns are present in the dataset protected attributes
        if not set(columns).issubset(self.dataset.protected_attributes_names):
            raise ValueError("columns must be present in the dataset protected attributes list")

        # Infer the groups
        combinations_df = self.dataset.df[columns].drop_duplicates().dropna()

        # Number of distinct groups
        v_value = len(combinations_df)
        # Number of instances in the dataset
        t_value = self.dataset.instance_weights.sum()

        total = 0

        # Iterate over all combinations of the columns
        for _, row in combinations_df.iterrows():
            combination = row.to_dict()
            group_size = self.num_instances([combination])

            total += math.fabs(
                (group_size / t_value) - (1 / v_value)
            )

        return total

    def value_range(self):
        return Range(FAIR_SCORE_MIN, FAIR_SCORE_MAX, inclusive=True)

    def ideal(self):
        return FAIR_SCORE_IDEAL

    def use_cases(self):
        return ['classification', 'regression']
