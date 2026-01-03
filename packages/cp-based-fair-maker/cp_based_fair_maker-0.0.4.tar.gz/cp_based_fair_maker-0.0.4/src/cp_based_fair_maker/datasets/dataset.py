import numpy as np
import pandas as pd

from cp_based_fair_maker.datasets.raw_dataset import RawDataset
from cp_based_fair_maker.utils.dataframe import downcast_dtypes


class Dataset(RawDataset):
    """ Base class for all datasets."""

    def __init__(self, df: pd.DataFrame, label_names, protected_attributes_names,
                 instance_weights_name=None, scores_names=[], unprivileged_protected_attributes=[],
                 privileged_protected_attributes=[]):
        """
        Initialize the Dataset with given attributes.

        :param df: Dataframe containing the dataset.
        :param label_names: Names of the label columns.
        :param protected_attributes_names: Names of the protected attributes (columns).
        :param instance_weights_name: Name of the column with instance weights.
        :param scores_names: Names of the score columns.
        :param unprivileged_protected_attributes: Definitions of unprivileged groups.
        :param privileged_protected_attributes: Definitions of privileged groups.
        """
        if df is None:
            raise ValueError("pandas DataFrame must be provided")
        if df.isna().any().any():
            raise ValueError("NA values are present in the dataset")

        self.df = df.copy()
        self.df.columns = self.df.columns.astype(str).tolist()
        self.df = downcast_dtypes(self.df)
        label_names = list(map(str, label_names))
        protected_attributes_names = list(map(str, protected_attributes_names))

        self.feature_names = [n for n in self.df.columns if n not in label_names
                              and (not scores_names or n not in scores_names)
                              and n != instance_weights_name]
        self.label_names = label_names
        self.features = self.df[self.feature_names].values #.copy()
        self.labels = self.df[self.label_names].values #.copy()
        self.instance_names = self.df.index.astype(str).tolist()

        self.scores_names = scores_names
        if scores_names:
            self.scores = self.df[scores_names].values #.copy()
        else:
            self.scores = self.labels #.copy()

        df_prot = self.df.loc[:, protected_attributes_names]
        self.protected_attributes_names = df_prot.columns.astype(str).tolist()
        self.protected_attributes = df_prot.values #.copy()
        # Infer the privileged and unprivileged values if not provided
        if unprivileged_protected_attributes and privileged_protected_attributes:
            self.unprivileged_protected_attributes = unprivileged_protected_attributes
            self.privileged_protected_attributes = privileged_protected_attributes
        else:
            privileged = []
            unprivileged = []
            if len(unprivileged_protected_attributes) > 0:
                for column in self.protected_attributes_names:
                    uniques = df_prot[column].unique()
                    privileged += [{column: x} for x in uniques if {column: x} not in unprivileged_protected_attributes]
                unprivileged += unprivileged_protected_attributes
            else:
                for column in self.protected_attributes_names:
                    uniques = df_prot[column].unique()
                    unprivileged += [{column: x} for x in uniques if {column: x} not in privileged_protected_attributes]
                privileged += privileged_protected_attributes

            self.unprivileged_protected_attributes = unprivileged
            self.privileged_protected_attributes = privileged

        self.instance_weights_name = instance_weights_name
        if instance_weights_name:
            self.instance_weights = df[instance_weights_name].values #.copy()
        else:
            self.instance_weights = np.ones_like(self.instance_names, dtype=np.float64)

        super(Dataset, self).__init__(df=df, label_names=label_names,
                                      protected_attributes_names=protected_attributes_names,
                                      instance_weights_name=instance_weights_name,
                                      scores_names=scores_names,
                                      unprivileged_protected_attributes=unprivileged_protected_attributes,
                                      privileged_protected_attributes=privileged_protected_attributes)

    def validate(self):
        """Validate the dataset."""
        # Check if label columns exist in the dataframe
        for label in self.label_names:
            if label not in self.df.columns:
                raise ValueError(f"Label column '{label}' not found in the dataframe.")

        # Check if protected attribute columns exist in the dataframe
        for attr in self.protected_attributes_names:
            if attr not in self.df.columns:
                raise ValueError(f"Protected attribute column '{attr}' not found in the dataframe.")

        # Check if instance weights column exists if specified
        if self.instance_weights_name and self.instance_weights_name not in self.df.columns:
            raise ValueError(f"Instance weights column '{self.instance_weights_name}' not found in the dataframe.")
        
        # Check if instance weights are non-negative
        if np.any(self.instance_weights < 0):
            raise ValueError("Instance weights must be non-negative.")

        # Check if score columns exist if specified
        for score in self.scores_names:
            if score not in self.df.columns:
                raise ValueError(f"Score column '{score}' not found in the dataframe.")

        # Check if unprivileged and privileged protected attributes are defined correctly
        for group in self.unprivileged_protected_attributes + self.privileged_protected_attributes:
            if not isinstance(group, dict):
                raise ValueError("Unprivileged protected attributes must be defined as a list of dictionaries.")
            for attr in group.keys():
                if attr not in self.protected_attributes_names:
                    raise ValueError(f"Unprivileged protected attribute '{attr}' not found in the dataframe.")
                if group[attr] not in self.df[attr].unique():
                    raise ValueError(f"Unprivileged protected attribute value '{group[attr]}' for '{attr}' not found in the dataframe.")

    def summary(self):
        """Print summary of dataset."""
        summary = {
            'Number of samples': len(self.df),
            'Number of features': len(self.feature_names),
            'Label distribution': {label: self.df[label].value_counts().to_dict() for label in self.label_names},
            'Protected attributes names': self.protected_attributes_names,
            'Privileged protected attributes': self.privileged_protected_attributes,
            'Unprivileged protected attributes': self.unprivileged_protected_attributes
        }
        return summary

    def save(self, output_file):
        """Save the dataset to an Excel file."""
        self.df.to_excel(output_file, index=False)

    def __str__(self):
        summary = self.summary()
        str = ""
        for key, value in summary.items():
            str += f"{key}: {value}\n"
        return str