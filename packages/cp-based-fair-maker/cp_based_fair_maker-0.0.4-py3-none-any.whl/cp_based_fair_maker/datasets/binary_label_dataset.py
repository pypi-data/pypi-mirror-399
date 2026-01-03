from cp_based_fair_maker.datasets.dataset import Dataset


class BinaryLabelDataset(Dataset):
    """Class for a dataset with binary label."""

    def __init__(self, df, label_names, protected_attributes_names, scores_names=[],
                 favorable_label=1., unfavorable_label=0., **kwargs):
        """
        Initialize the Dataset with given attributes.

        :param df: Dataframe containing the dataset.
        :param label_names: Names of the label columns.
        :param protected_attributes_names: Names of the protected attributes (columns).
        :param instance_weights_name: Name of the column with instance weights.
        :param scores_names: Names of the score columns.
        :param unprivileged_protected_attributes: Definitions of unprivileged groups.
        :param privileged_protected_attributes: Definitions of privileged groups.
        :param favorable_label: Value of the favorable label.
        :param unfavorable_label: Value of the unfavorable label.
        """
        self.favorable_labels = float(favorable_label)
        self.unfavorable_labels = float(unfavorable_label)

        super(BinaryLabelDataset, self).__init__(
            df=df, label_names=label_names, protected_attributes_names=protected_attributes_names, 
            scores_names=scores_names, **kwargs)

    def validate(self):
        """Validate that the dataset contains a binary label."""
        super().validate()

        # Check if the label is binary
        if len(self.label_names) != 1:
            raise ValueError("BinaryLabelDataset only supports single-column labels")

        label = self.label_names[0]
        unique_values = self.df[label].nunique()
        if unique_values > 2: # handle cases when all instances belong to the same class
            raise ValueError(f"Label column '{label}' is not binary; it contains {unique_values} unique values.")

        unique_values = set(self.df[label].unique())
        expected_labels = {self.favorable_labels, self.unfavorable_labels}
        if not unique_values.issubset(expected_labels):
            raise ValueError(
                f"Label column '{label}' contains invalid values: {unique_values}. Expected values are {expected_labels}.")

    def summary(self):
        """Return a summary of the dataset."""
        summary = {
            'Number of samples': len(self.df),
            'Number of features': self.df.shape[1] - len(self.label_names) - len(self.scores_names),
            'Label distribution': self.df[self.label_names[0]].value_counts().to_dict(),
            'Protected attributes': self.protected_attributes_names,
        }
        return summary
