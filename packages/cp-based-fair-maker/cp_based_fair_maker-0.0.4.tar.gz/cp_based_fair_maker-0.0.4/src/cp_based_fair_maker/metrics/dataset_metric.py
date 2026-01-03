import pandas as pd

from cp_based_fair_maker.datasets.dataset import Dataset
from cp_based_fair_maker.metrics.raw_metric import RawMetric
from cp_based_fair_maker.utils.operations import difference, ratio
from cp_based_fair_maker.utils.range import Range


class DatasetMetric(RawMetric):
    """Class for Dataset class metrics computation."""

    def __init__(self, dataset: Dataset, predictions=None, privileged_groups=None, unprivileged_groups=None):
        """
        Args:
        :param dataset: Dataset to compute metrics for.
        :param predictions: DataFrame containing predictions. Should have the same indexes as the original dataset.df,
            and the columns defined in dataset.scores_names and dataset.label_names.
        :param privileged_groups: List of dictionaries where each dictionary represents a privileged group and has the
            following format: {attr: value} where each attr is in dataset.protected_attributes_names and each value is
            either one, list, tuple or set of elements in dataset.privileged_protected_attributes or a compatible Range.
        :param unprivileged_groups: List of dictionaries where each dictionary represents an unprivileged group and has
            the same format as privileged_groups, dataset.unprivileged_protected_attributes replacing
            dataset.privileged_protected_attributes.

        :raises ValueError: If any of the required conditions are not met.
        """
        if not isinstance(dataset, Dataset):
            raise ValueError("dataset must be an instance of Dataset")

        super(DatasetMetric, self).__init__(dataset)

        if predictions is not None:
            # Validate the predictions structure
            self._validate_predictions_structure(dataset, predictions)

        self.dataset = dataset
        self.predictions = predictions

        # Validate the privileged and unprivileged groups
        self._validate_groups(dataset, privileged_groups, unprivileged_groups)
        # Infer the complementary group if not provided
        if privileged_groups is None:
            privileged_groups = self._infer_complementary_group(unprivileged_groups)
        elif unprivileged_groups is None:
            unprivileged_groups = self._infer_complementary_group(privileged_groups)
        self.privileged_groups = privileged_groups
        self.unprivileged_groups = unprivileged_groups

    @staticmethod
    def _validate_predictions_structure(dataset, predictions):
        """
        Validate the predictions dataframe against the dataset.

        Args:
            dataset (Dataset): The original dataset.
            predictions (pd.DataFrame): The predictions dataset to validate.

        Raises:
            ValueError: If the predictions dataset does not match the expected structure.
        """
        # Check number of rows
        if len(predictions) != len(dataset.df):
            raise ValueError("The predictions dataset must have the same number of rows as the original dataset.")
        # Check indexes
        if not predictions.index.equals(dataset.df.index):
            raise ValueError("The predictions dataset must have the same index as the original dataset.")
        # Check columns
        required_columns = set(dataset.scores_names + dataset.label_names)
        if not required_columns.issubset(predictions.columns):
            missing_columns = list(set(required_columns).difference(set(predictions.columns)))
            raise ValueError(f"The predictions dataset is missing the following columns: {missing_columns}.")

    @staticmethod
    def _validate_groups(dataset, privileged_groups, unprivileged_groups):
        """
        Validate the privileged and unprivileged groups.

        Args:
            dataset (Dataset): The original dataset.
            privileged_groups (list of dict): List of privileged groups.
            unprivileged_groups (list of dict): List of unprivileged groups.

        Raises:
            ValueError: If the groups do not match the dataset's protected attributes and values.
        """
        # Check if at least one group is defined
        if privileged_groups is None and unprivileged_groups is None:
            raise ValueError("At least one of privileged_groups or unprivileged_groups must be defined.")

        if privileged_groups is not None:
            # Validate privileged groups
            DatasetMetric._validate_group_definition(dataset, privileged_groups, "privileged_group")
        if unprivileged_groups is not None:
            # Validate unprivileged groups
            DatasetMetric._validate_group_definition(dataset, unprivileged_groups, "unprivileged_group")

    def _infer_complementary_group(self, known_group):
        """
        Infer the complementary group based on the known group.

        Args:
            known_group (list of dict): Known group to infer the complementary group from.

        Returns:
            list of dict: Inferred complementary group.
        """
        if not known_group:
            raise ValueError("Non-empty known_group must be provided to infer the complementary group.")
        # Create a mask for the dataset
        mask = self.build_groups_mask(known_group)

        complement_df = self.dataset.df.loc[~mask, self.dataset.protected_attributes_names]
        if complement_df.empty:
            raise ValueError("The complementary group is empty. Please check the provided group.")

        # TODO 10/05/2025 For Ranges, do not use what the complementary provides as it contains all distinct values
        #  that do not suits the range. Instead, build the complementary range
        unique_combinations = complement_df.drop_duplicates().to_dict(orient='records')
        return unique_combinations

    @staticmethod
    def _validate_group_definition(dataset, groups, group_type="group"):
        """
        Validate the group definitions.
        Args:
            dataset (Dataset): The original dataset.
            groups (list of dict): List of groups to validate.
            group_type (str): Type of the group ("privileged_group" or "unprivileged_group").
        """
        for i, group in enumerate(groups):
            # Check if the group is a dictionary
            if not isinstance(group, dict):
                raise ValueError(f"{group_type}[{i}] must be a dictionary.")

            # Check if the group is defined with appropriate keys (protected attributes)
            if not all(attr in dataset.protected_attributes_names for attr in group.keys()):
                raise ValueError(f"{group_type} must contain attributes from the dataset's protected attributes.")

            # Check if the values in the groups are valid
            for attr, value in group.items():
                column_values = dataset.df[attr].dropna().unique()

                if isinstance(value, (str, int, float, bool, dataset.df[attr].dtype.type)):
                    if value not in column_values:
                        raise ValueError(f"Value '{value}' for attribute '{attr}' in {group_type}[{i}] is not valid.")
                elif isinstance(value, (list, set, tuple)):
                    if not any(val in column_values for val in value):
                        raise ValueError(f"Values '{value}' for attribute '{attr}' in {group_type}[{i}] are not valid, "
                                         f"none of them are present in the dataset.")
                elif isinstance(value, Range):
                    column_type = dataset.df[attr].dtype.type
                    if not value.is_compatible_with_type(column_type):
                        raise ValueError(
                            f"Range '{value}' for attribute '{attr}' in {group_type}[{i}] is not compatible "
                            f"with the column type '{column_type}'.")

    def num_instances(self, group):
        """
        Calculate the number of instances in the dataset that belong to the specified group.

        Args:
            group (list of dict): Group to calculate instances for.

        Returns:
            int: Number of instances belonging to the group.
        """
        # Filter the dataset for instances that match the group
        mask = self.build_groups_mask(group)
        weights = self.dataset.instance_weights * mask.astype(int)

        # Sum the instance weights for the matching group
        return weights.sum()

    def difference(self):
        """
        Calculate the difference in a metric between unprivileged and privileged groups.

        Returns:
            float: Difference in the metric between unprivileged and privileged groups.
        """
        return difference(self.compute, self.privileged_groups, self.unprivileged_groups)

    def ratio(self):
        """
        Calculate the ratio of a metric between unprivileged and privileged groups.

        Returns:
            float: Ratio of the metric between unprivileged and privileged groups.
        """
        return ratio(self.compute, self.privileged_groups, self.unprivileged_groups)

    def compute(self, group=None):
        raise NotImplementedError

    def value_range(self):
        raise NotImplementedError

    def ideal(self):
        raise NotImplementedError

    def use_cases(self):
        raise NotImplementedError

    def build_groups_mask(self, group_def):
        """
        Build a mask for the dataset based on the group definition.

        Args:
            group_def (list of dict): Group definition.

        Returns:
            pd.Series: Boolean mask where True represents instances belonging to the group.
        """
        mask = pd.Series(False, index=self.dataset.df.index)
        for group in group_def:
            mask |= self._get_mask(self.dataset.df, group)
        return mask

    @staticmethod
    def _get_mask(df, group_criteria):
        """
        Build a mask for the provided dataframe based on criteria.

        Args:
            df (pd.DataFrame): DataFrame to filter.
            group_criteria (dict): Criteria for filtering.
                Each key is a column name and the value is the value to match.
                If the value is a Range, it checks if the column value is within the range.
                If the value is a list, set, or tuple, it checks if the column value is in the list.

        Returns:
            pd.Series: Boolean mask where True represents instances matching the criteria.
        """
        mask = pd.Series(True, index=df.index)
        for attr, val in group_criteria.items():
            if isinstance(val, Range):
                mask &= df[attr].apply(lambda x: x in val)
            elif isinstance(val, (list, set, tuple)):
                mask &= df[attr].isin(val)
            else:
                mask &= df[attr] == val
        return mask
