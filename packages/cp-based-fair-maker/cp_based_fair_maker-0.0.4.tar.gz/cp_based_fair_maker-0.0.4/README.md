# cp-based-fair-maker

## Description

This is a library for creating fair ML datasets using Constraint Programming (CP). It suggests a way to create fair
datasets by solving a constraint satisfaction problem (CSP) using CP and various fairness metrics. The library is based
on the [Google OR-Tools](https://developers.google.com/optimization) CP solver.

## Glossary

1. **Protected attribute**: An attribute/feature that divides the population into groups that we want to be fair to. For
   example, *race* or *gender* can be protected attributes.
2. **Privileged group**: Considering a protected attribute, the groups that have historically been advantaged or have had more opportunities.
3. **Unprivileged group**: Considering a protected attribute, the groups that have historically been disadvantaged or have had fewer opportunities.
4. **Instance**: A row in the dataset.
5. **Feature**: A column in the dataset.
6. **Instance weight**: A weight assigned to each instance in the dataset. It can be seen as the number of times an instance is repeated in the dataset.
7. **Label column**: The column that represents the class labels of the instances.
7. **Score columns**: Columns that represent the confidence scores of the instances for each class label.
8. **Fairness metric**: A metric that measures the fairness of the dataset. 
9. **Fairness threshold**: A threshold value for a fairness metric. The fairness metric value is compared to this threshold to determine if the dataset is fair or not.


## Install from source

If you want to install the package from the source code, you can clone the repository and install it using pip:

```bash
pip install build setuptools wheel
python -m build
pip install dist/cp_based_fair_maker-<version>.whl
```

Here `<version>` should be replaced with the actual version number of the package.
