# Propensity Score Calculator

Estimate the Propensity Score in Python following [Imbens and Rubin (2015a)](https://doi.org/10.1017/CBO9781139025751.014). The following additional methods are incorporated:

- Strata based on the estimated propensity score [Imbens and Rubin (2015a)](https://doi.org/10.1017/CBO9781139025751.014)

- Suggested Maximum and Minimum values of the propensity score to maintain covariate balance through trimming [Imbens and Rubin (2015b)](https://doi.org/10.1017/CBO9781139025751.017)

- Matching (with/without replacement) based on the estimated propensity score [Imbens and Rubin (2015c)](https://doi.org/10.1017/CBO9781139025751.016)

This package has been constructed with the end-user (likely a social science researcher) in mind. Several notable features that make this package unique:

- Testing for important covariates/features in the propensity score is done in parallel (optional, default is True) which greatly reduces the time required for completion. Testing features is not required to utilize the matching and stratifying methods; see below for information about fitting the propensity score without testing any variables.

- The matching algorithm has been optimized with a recursive-binary search function. This means iteration over the potential controls happens in O(logN) time.  In testing, runtime for matching with replacement for 100k treated units and 500k control units was <5 seconds on my personal laptop with 8 cores. Matching without replacement for the same set was 1.75 minutes.

## New Features in Most Recent Version
- Faster solver for generating matches (see above).
- Addition of caliper so that the user can make sure matches fall within some bandwidth in propensity score or log-odds units.
- A feature that automatically standardizes variables for the user.



## Installation
Use `pip` to install:
```
pip install propensityscore
```

## Description
This package allows one to estimate the propensity score (the probability of being in the treated group) following the general methodology laid out in [Imbens and Rubin (2015a)](https://doi.org/10.1017/CBO9781139025751.014).

Support currently exists for first and second order terms. The method estimates in 3 steps. The first is done by the user, the remaining are done by the code.

### Step 1
Choose which covariates you think are relevant and should always be included in the propensity score equation. These will be in `main_vars` in the code.

### Step 2
Add additional linear terms that will be tested. These are specified by `test_vars`. These will be selected one-by-one according to which gives the largest overall gain in log odds in the propensity score calculation. In each step we take the max such that the gain is greater than a predetermined value (the default is 1). Once no remaining variable gives a gain of at least one, the linear portion terminates.

### Step 3
Quadratic and interaction terms are automatically generated from the `main_vars` and the `test_vars` and these are compared in the same way as the linear terms except the log odds must increase by a separate amount (default is 2.71).

## Tips and Notes
- If one would like to use all of the modules embedded in the propensity score class without testing any variables, feel free to `fit` the model with only `main_vars` and set the `test_second_order=False`. Alternatively, one could test second order combinations of all `main_vars` by setting that argument to `True`. Similarly, it is possible to only test first order variables by specifying them in `test_vars`.
- You must have enough control units to match without replacement, the program will warn you otherwise.
- If you want to employ a hybrid matching strategy (whereby you ensure that a particular covariate is matched on, and then within each set of covariates, the best match is chosen), you can do this by selecting an additional Series or DataFrame with the same index as the original data, and specifying `match_covs` in the matching module. If you specify a list, the values in this list must have been searched over in the original propensity score fit. Please note that you should only do this with categorical data; you cannot do a hybrid matching method with continuous data.

## Example Use
The following is sample code to illustrate the use:

```
from propensityscore import PropensityScore
import sklearn.datasets
import numpy as np
import pandas as pd
X, y = sklearn.datasets.make_classification(n_samples=30000, n_features=3000,
                                            n_informative=100, n_redundant=0, n_repeated=0)

df = pd.DataFrame(X).iloc[:,:100]
df.columns=['x{}'.format(str(ii).zfill(3)) for ii in range(100)]

main_vars = ['x002','x003'] # we think these are important
test_vars = [x for x in df.columns if x not in main_vars]

df.loc[:,'treated'] = y

# take a sample of the treated units and all of the control units (for matching without replacement)
# df = df.loc[df.treated.eq(1),:].sample(1000).append(df.loc[df.treated.eq(0),:])

################################################################################
## Normal Use: Testing Potential Features
################################################################################

# initialize the Class
output = PropensityScore(outcome='treated', df=df, test_vars=test_vars,
                      main_vars=main_vars, test_second_order=True)

# The propensity score values are given in the pandas Series:
# We specify cutoffs of 5 and 1 for first and second order terms (in log-likelihood ratio improvements)
# We additionally exclude higher order terms involving variable x002. The result is stored in output.propscore

# fit the model
output.fit(cutoff_ord1=4,cutoff_ord2=8,exclude_vars_ord2=['x002'])

# to run on all cores in each test in the utilized scikit-learn logit regression, specify:
output.fit(cutoff_ord1=4,cutoff_ord2=8,exclude_vars_ord2=['x002'],n_jobs=-1)


# Alternatively, one could initialize and standardize all non-binary variables with
output = PropensityScore(outcome='treated', df=df, test_vars=test_vars,
                      main_vars=main_vars, test_second_order=True,standardize=True)
output.fit(cutoff_ord1=5,cutoff_ord2=1,exclude_vars_ord2=['x002'],solver='sag') # the sag solver can be faster.


################################################################################
## A Model that tests no variables so that additional tools can be utilized.
################################################################################

# The user may want to estimate a model by testing nothing so that they can still use the matching features.
# This is possible by specifying a list of covariates in main_vars, no test variables, and setting test_second_order=False.
# alternatively, one could test linear but not second order terms, or vice-versa.

model2 = PropensityScore(outcome='treated', df=df, test_vars=None, main_vars=main_vars, test_second_order=False)
model2.fit()

################################################################################
## Matching/Stratifying Modules
################################################################################

# To see the different strata calculated, you can reference where the result will be in output.strata
output.stratify()

# To trim, we can simply run
output.trim()

# Finally, we can match as follows (this specifies two matches for each control unit)
output.match(n_matches=2,replacement=True)

# we can specify an optional caliper in the following way:
output.match(replacement=True,caliper=.01,caliper_param='propscore')
# this will verify that the propensity score is no more than .01 apart between treated and control units.


# Imagine there is a covariate we want to additionally match on (multiple accepted)
cov = pd.Series(np.random.randint(0,4,size=len(df)),index=df.index)
output.match(n_matches=2,replacement=True,match_covs=cov)

```

## References

Imbens, G., & Rubin, D. (2015a). Estimating the Propensity Score. In Causal Inference for Statistics, Social, and Biomedical Sciences: An Introduction (pp. 281-308). Cambridge: Cambridge University Press. doi:10.1017/CBO9781139025751.014

Imbens, G., & Rubin, D. (2015b). Trimming to Improve Balance in Covariate Distributions. In Causal Inference for Statistics, Social, and Biomedical Sciences: An Introduction (pp. 359-374). Cambridge: Cambridge University Press. doi:10.1017/CBO9781139025751.017

Imbens, G., & Rubin, D. (2015c). Matching to Improve Balance in Covariate Distributions. In Causal Inference for Statistics, Social, and Biomedical Sciences: An Introduction (pp. 337-358). Cambridge: Cambridge University Press. doi:10.1017/CBO9781139025751.016
