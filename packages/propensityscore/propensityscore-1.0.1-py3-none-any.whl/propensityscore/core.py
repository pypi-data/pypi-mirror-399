from statsmodels.api import Logit as PrettyLogit
from scipy.stats import ttest_ind as ttest
from sklearn.linear_model import LogisticRegression as FastLogit
from joblib import Parallel, delayed
from numpy import dot, nan, linspace, delete, argmin, argpartition, all as allfunc, sum as npsum, any as anyfunc
from pandas import Series, concat, DataFrame, notna, NA
import warnings

class PropensityScore:
    """
    This initializes the object that will enable calculation of the propensity score.
    The main purpose here is to cut down the data and run some initial checks, like
    testing for singularity, and collecting binary variables. If the user
    would not like to test any variables, leave test_vars blank. If testing higher order terms
    is not desired, then additionally set this to False. A constant will be checked-for and added
    if not detected in the data. Variables can be standardized, if wanted.

    Parameters
    ----------
    outcome : str
        This should be the name of the binary variable to predict.
    test_vars : list
        A list of the variables to test.
    df : DataFrame
        The pandas DataFrame that contains all of the data.
    main_vars : str or list, optional
        Variables to always have included in the propensity score. The default is None.
    test_second_order : Boolean, optional
        If True, then test all (included) squared and interaction terms of the fit model.
    standardize : Boolean, optional
        If True, then continuous variables will be standarized by (x-mean(x))/2*std(x).
        which keeps the standard deviation in line with binary variables (that are split
        50/50). Binary variables are unchanged. Standardization is not required but
        recommended for faster convergence if testing many variables in the propensity score.
        Default is False.

    Raises
    ------
    ValueError
        If variables are improperly defined, this prints out warnings.

    Methods
    -------
    fit
        The main function to fit the propensity score. Returns the final model and logodds.

    trim
        A simple function to trim the propensity score optimally.

    match
        A tool to match controls to the treatment values based on logodds.

    stratify
        A tool to recursively split the sample into strata, based on logodds.
    """

    def __init__(self, outcome, df, test_vars=None, main_vars=None, test_second_order=True,
                 standardize = False):

        # double checking some inputs
        if type(outcome)!=str:
            raise ValueError('y must be a string variable name in the DataFrame.')
        if test_vars and type(test_vars)!=list:
            raise ValueError('test_vars must be a list of variables in DataFrame.')
        if main_vars and type(main_vars)!=list:
            raise ValueError('main_vars must be a list of variables in DataFrame.')

        # making combinations of covariates to assess.
        if main_vars and test_vars:
            covs = main_vars + test_vars
            if anyfunc([x in test_vars for x in main_vars]) or anyfunc([x in main_vars for x in test_vars]):
                raise ValueError('Cannot have same variable in test and init vars.')
            if len(covs)>len(set(covs)):
                raise ValueError('Repeated variable names in namespace.')
        elif main_vars:
            covs = main_vars
            if test_second_order:
                warnings.warn('No linear terms will be tested. Second order terms will still be checked.')
            else:
                warnings.warn('Model will be fit with only main_vars.')
        elif test_vars:
            covs = test_vars
        else:
            raise ValueError('You must initialize or test some set of variables.')

        if outcome in covs:
            raise ValueError('Outcome variable cannot be in covariates.')

        data = df.loc[:,[outcome]+covs].copy()
        lendatorig = len(data)

        # =====================================================================
        # Eliminating Missing Values and Checking Singularity
        # =====================================================================
        data = data.dropna()
        if len(data)<lendatorig:
            warnings.warn('{} Missing Values in Data. Dropping These Values. '\
                          'Original Axis Labels Consistent.'.format(lendatorig-len(data)))

        vars_singular = []
        vars_binary = []
        for cc in covs:
            if allfunc(data.loc[:,cc]==data.loc[:,cc].iloc[0]):
                if data.loc[:,cc].iloc[0] == 0:
                    raise ValueError('{} has no variation.')
                vars_singular.append(cc)
            elif len(data.loc[:,cc].unique())==2:
                if set(data.loc[:,cc].unique()) == {0,1}:
                    vars_binary.append(cc)


        if len(vars_singular)>1:
            raise ValueError('The following are singular: {}'.format(', '.join(vars_singular)))
        elif len(vars_singular)==1:
            self.constant = vars_singular[0]
        else:
            if 'Constant' in data.columns:
                warnings.warn('Variable "Constant" will be overwritten with vector of 1s')
            data.loc[:,'Constant'] = 1
            self.constant = 'Constant'
            if not main_vars:
                main_vars = ['Constant']
            else:
                main_vars = ['Constant'] + main_vars

        # A helper function to standardize the variables
        def std_variable(series_var):
            return (series_var-series_var.mean())/(2*series_var.std())

        if standardize:
            stdvars = [ii for ii in covs if ii not in [self.constant]+vars_singular+vars_binary]
            if stdvars:
                data.loc[:,stdvars] = data.loc[:,stdvars].apply(std_variable,axis=0)

        self.outcome = outcome
        self.vars_binary = vars_binary
        self.test_vars = test_vars
        self.main_vars = main_vars
        self.data = data
        self.trimmed = False
        self.test_second_order = test_second_order


    def fit(self, cutoff_ord1 = 1, cutoff_ord2 = 2.71, exclude_vars_ord2 = None,
            parallel = True, verbose=True, **kwargs):
        """
        The primary function which calculates the propensity score. You must select the cutoffs
        for the first and second order terms. The process proceeds as follows:

            1. First order terms are tested sequentially such that each contributes
            at least cutoff_ord1 to the log-likelihood ratio. At each iteration, the term
            that contributes the most is selected, until no more terms can be chosen.

            2. All feasible second order terms (squared and all interactions) are
            generated from the chosen first order terms.

            3. Step (1) is repeated for the second order terms with
            cutoff_ord2 as the criteria.

        Each iteration will run in parallel unless otherwise specified. A special case is when
        the model has no tested variables. If this is the case, the fitting will bypass the
        testing procedue entirely. If test_second_order is still True, however, second order combinations
        of the initialized variables will be tested.

        Parameters
        ----------
        cutoff_ord1 : Numeric, optional
            The log gain cutoff for first order covariates. The default is 1.
        cutoff_ord2 : Numeric, optional
            The log gain cutoff for second order covariates. The default is 2.71.
        exclude_vars_ord2 : List, optional
            An optional list of the first order variables that will not have second order terms generated.
            Can be useful if you do not want certain interactions or second order terms.
            Infeasible terms will be dropped automatically.
        parallel : Boolean, optional
            This specifies if the selection at each step runs in parallel.
            Paralellization is done using joblib. Recommended unless not feasible on machine.
            Default is True.
        verbose : Boolean, optional
            If true, will display all text about variable selection and LLR contribution,
            along with the final model results. Default is True.
        **kwargs : Optional
            Propscore uses scikit-learn logistic regression under the hood. You can pass
            arguments to this function here, if wanted. For example, if you standardize
            your variables, you can pass solver='sag'. All options are valid, except
            verbosity. See all options here
            https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html

        Raises
        ------
        ValueError
            If variables are improperly defined, this prints out warnings.

        Returns
        -------
        self.propscore : Series
            This is the propensity score as calculated by self.model.fittedvalues.
            This may not match dimension of data due to dropped missing values,
            but index will align properly.
        self.logodds : Series
            The linearized propensity score. Will be the same dimension as propscore.
        self.model : sm.Logit.fit() model
            This is the raw model on the final set of variables from Statsmodels.
        """

        # collecting kwargs for the scikit-learn solver, otherwise using defaults.
        if kwargs and not self.test_vars and not self.test_second_order:
            warnings.warn('Specified kwargs will not be utilized since no tests are done')
        penalty = kwargs.get('penalty','l2')
        dual = kwargs.get('dual',False)
        tol = kwargs.get('tol',0.0001)
        C = kwargs.get('C',1.0)
        fit_intercept = kwargs.get('fit_intercept',False) # an intercept is added in __init__
        intercept_scaling = kwargs.get('intercept_scaling',1)
        class_weight = kwargs.get('class_weight',None)
        random_state = kwargs.get('random_state',None)
        solver = kwargs.get('solver','lbfgs')
        max_iter = kwargs.get('max_iter',100)
        warm_start = kwargs.get('warm_start',False)
        n_jobs = kwargs.get('n_jobs',None)
        l1_ratio = kwargs.get('l1_ratio',None)

        # =====================================================================
        # A helper function to get the best variable in a group.
        # =====================================================================
        def best_in_group(new,old,ll,parallel,mod):
            ''' A function to return the best LLR improvement given a group of new/old vars '''

            # define the logit function
            def run_logit(v):
                try:
                    mod.fit(self.data.loc[:,old+[v]],self.data.loc[:,self.outcome])
                except:
                    raise ValueError('The following tested covariate combination failed to converge, likely singular: '\
                                     '{}'.format(', '.join(old+[v])))
                logprob = mod.predict_log_proba(self.data.loc[:,old+[v]])
                return (dot(1-self.data.loc[:,self.outcome],logprob[:,0])+
                        dot(self.data.loc[:,self.outcome],logprob[:,1]))

            # running it in parallel or not
            if parallel and len(new)>1:
                list_llf = Parallel(n_jobs=-1)(delayed(run_logit)(v) for v in new)
            else:
                list_llf = []
                for v in new:
                    list_llf.append(run_logit(v))
            val = max(list_llf)
            idx = list_llf.index(val)
            return new[idx],2*(val-ll),val

        # =====================================================================
        # The iterative fitting function
        # =====================================================================

        # quick sanity check on potentially excluded second order vars.
        if exclude_vars_ord2 and self.test_second_order and type(exclude_vars_ord2)!=list:
            raise ValueError('Excluded vars should be specified as a list.')

        # the first case is just run a model on the baseline included variables and no further testing.
        if not self.test_vars and not self.test_second_order:
            self.model = PrettyLogit(self.data.loc[:,self.outcome],
                                     self.data.loc[:,self.main_vars]).fit(disp=False)
            self.logodds = self.model.fittedvalues.rename('logodds')
            self.propscore = Series(self.model.predict(),index=self.logodds.index,name='propscore')
            self.linear_terms = self.main_vars
            self.nonlinear_terms = []
            if verbose:
                print(self.model.summary())

            return

        mod = FastLogit(penalty=penalty,dual=dual,tol=tol,C=C,fit_intercept=fit_intercept,
                        intercept_scaling=intercept_scaling,class_weight=class_weight,
                        random_state=random_state,solver=solver,max_iter=max_iter,
                        warm_start=warm_start,n_jobs=n_jobs,l1_ratio=l1_ratio)

        y  = self.outcome
        x0 = self.main_vars.copy()

        # the first model run, outside of any loop: it's the baseline ll
        mod.fit(self.data.loc[:,x0],self.data.loc[:,y])
        logprob = mod.predict_log_proba(self.data.loc[:,x0])
        ll0 = (dot(1-self.data.loc[:,y],logprob[:,0])+
                dot(self.data.loc[:,y],logprob[:,1]))

        # now we proceed depending on if we have variables to test.
        if self.test_vars:
            x1 = self.test_vars.copy()
            # =====================================================================
            # First do all the linear variables
            # =====================================================================
            stop = False
            while not stop:
                best_x, best_llr, ll1 = best_in_group(new=x1,old=x0,ll=ll0,parallel=parallel,mod=mod)
                if best_llr>cutoff_ord1:
                    if verbose:
                        print('Adding Linear Term: {}; LLR: {}'.format(
                            best_x,round(best_llr,2)))
                    x0.append(best_x)
                    x1.remove(best_x)
                    ll0 = ll1
                    if len(x1)==0:
                        stop = True
                else:
                    stop = True

            if len(x0)==len(self.main_vars):
                warnings.warn('No linear terms selected. Lower the threshold, or include using main_vars')

        self.linear_terms = x0 # confusing notation I used here, but all variables selected are just x0

        # =====================================================================
        # Done here if not testing second order terms
        # =====================================================================
        if not self.test_second_order:
            self.model = PrettyLogit(self.data.loc[:,self.outcome],
                                     self.data.loc[:,x0]).fit(disp=False)
            self.logodds = self.model.fittedvalues.rename('logodds')
            self.propscore = Series(self.model.predict(),index=self.logodds.index,name='propscore')
            self.nonlinear_terms = []
            if verbose:
                print(self.model.summary())
            return

        # =====================================================================
        # Generating second order terms
        # =====================================================================
        ord2_vars = []
        dropped_vars = []
        # no need to include explicitly excluded variables and the constant.
        if exclude_vars_ord2:
            xlist = [ii for ii in x0 if ii!=self.constant and ii not in exclude_vars_ord2]
        else:
            xlist = [ii for ii in x0 if ii!=self.constant]

        newvars = {}
        for idx,cc in enumerate(xlist):
            # for all variables generate the interaction terms
            if idx<len(xlist): # only interactions if more that one variable
                for jj in xlist[idx+1:]:
                     testvar = self.data.loc[:,cc]*self.data.loc[:,jj]
                     if (not testvar.equals(self.data.loc[:,cc]) and
                         not testvar.equals(self.data.loc[:,jj]) and
                         not allfunc(testvar==testvar.iloc[0])):
                             #self.data.loc[:,'X'.join([cc,jj])] = testvar.values
                             newvars['X'.join([cc,jj])] = testvar
                             ord2_vars.append('X'.join([cc,jj]))
                     else:
                         dropped_vars.append('X'.join([cc,jj]))

            # for continuous variables, generate squared term
            if cc not in self.vars_binary:
                #self.data.loc[:,'{}_sq'.format(cc)] = (self.data.loc[:,cc]**2).values
                newvars['{}_sq'.format(cc)] = (self.data.loc[:,cc]**2)
                ord2_vars.append('{}_sq'.format(cc))
            else:
                dropped_vars.append('{}_sq'.format(cc))

        if newvars:
            runagain = [x for x in ord2_vars if x in self.data]
            if runagain:
                self.data = self.data.drop(runagain,axis=1)
            self.data = self.data.join(concat(newvars,axis=1))
        else:
            warnings.warn('No second order terms to check.')
            self.model = PrettyLogit(self.data.loc[:,self.outcome],
                                     self.data.loc[:,x0]).fit(disp=False)
            self.logodds = self.model.fittedvalues.rename('logodds')
            self.propscore = Series(self.model.predict(),index=self.logodds.index,name='propscore')
            if verbose:
                print(self.model.summary())
            return

        if dropped_vars:
            self.infeasible_vars = dropped_vars
            if verbose:
                print('While generating nonlinear terms, the following vars are '\
                      'singular and excluded: {}'.format(', '.join(dropped_vars)))

        self.test_vars_ord2 = ord2_vars

        # =====================================================================
        # Doing Analysis for Second Order Terms
        # =====================================================================
        # doing the loop again
        stop = False
        x1 = ord2_vars.copy()
        x0 = x0.copy()

        while not stop:
            best_x, best_llr, ll1 = best_in_group(new=x1,old=x0,ll=ll0,parallel=parallel,mod=mod)
            if best_llr>cutoff_ord2:
                if verbose:
                    print('Adding Nonlinear Term: {}; LLR: {}'.format(
                        best_x,round(best_llr,2)))
                x0.append(best_x)
                x1.remove(best_x)
                ll0 = ll1
                if len(x1)==0:
                    stop = True
            else:
                stop = True

        self.nonlinear_terms = [ii for ii in x0 if ii not in self.linear_terms]

        if not self.nonlinear_terms:
            warnings.warn('No nonlinear terms selected. Lower the threshold, or include directly.')

        # running the model and storing the propensity score (Pretty Statsmodels Version)
        self.model = PrettyLogit(self.data.loc[:,self.outcome],
                                 self.data.loc[:,x0]).fit(disp=False)
        self.logodds = self.model.fittedvalues.rename('logodds')
        self.propscore = Series(self.model.predict(),index=self.logodds.index,name='propscore')

        if verbose:
            print(self.model.summary())

        return

    def trim(self):
        """
        A function to trim the propensity score. Will return the trimmed values as a series.
        Calculation is based on optimal trimming rule specified in Imbens + Rudin Causal Inference Text.

        Parameters
        ----------
        None

        Raises
        ------
        None

        Returns
        -------
        self.propscore_trim : Series
            The trimmed propensity score values. This is the primary returned object.
        self.trim_range : tuple
            The result of calculating the optimal trim min and max propensity score values.
        self.in_trim : Series (True/False)
            An array where True means that the propensity score falls within the
            trim min/max range.
        self.logodds_trim : Series
            The trimmed logodds.
        """
        def calc_trim(propscore):
            ''' A static method to calculate the trimmed version '''
            y = 1/(propscore*(1-propscore))

            # if this condition, then done.
            if y.max() <= (2/y.count())*(y.sum()):
                return 0,1

            # loop through all these ratios, and check this condition.
            alpha = 0
            y = y.sort_values(ascending=False)
            for gamma in y:
                lhs_estimand = (gamma/y.count())*(y.le(gamma).sum())
                rhs_estimand = (2/y.count())*((y.le(gamma)*y).sum())
                if lhs_estimand < rhs_estimand:
                    alpha = .5-((.25-(1/gamma))**.5)
                    break

            return alpha,1-alpha

        self.trim_range = calc_trim(self.propscore)
        self.in_trim = (self.propscore.ge(self.trim_range[0]) &
                        self.propscore.le(self.trim_range[1])).rename('in_trim')
        self.propscore_trim = self.propscore[self.in_trim]
        self.logodds_trim = self.logodds[self.in_trim]
        self.trimmed = True
        print('Trimmed {} Obs; stored in propscore_trim'.format(self.in_trim.eq(False).sum()))
        return self.propscore_trim

    def stratify(self, t_strata=1, n_min='auto'):
        """
        This function calculates the strata. t_strata is the criteria for the t-statistic
        for logodds in each strata (if it exceeds this value, a new split is made.)
        See the details for how to specify n_min, which includes information about the
        number of treated and control units in each strata, and the minimum units in the
        strata overall. If observations are deemed too out-of-balance to be put in a strata
        the strata will result in a missing observation. This is not the same as trimming,
        as it is merely excluding control units with propensity scores too low or treated units
        with propensity scores too high to have matching units in the same strata.

        Parameters
        ----------
        t_strata : Numeric, optional
            The cutoff for the t-statistic for the calculated strata. The default is 1.
        n_min : {'strata':int1,'treatment_control':int2} or 'auto'
            The minimum number of units in each strata or treated/control individuals in strata.
            The default is 'auto' in which case the number per strata is the number of covariates
            tested in the propensity score (just linear ones) + 2 (or K+2)
            while the minimum number of treated and control individuals per strata is 3.
            If not auto, the input needs to be a dictionary that explicitly specifies:
            {'strata':int1,'treatment_control':int2}

        Raises
        ------
        ValueError
            If variables are improperly defined, this prints out warnings.

        Returns
        -------
        self.strata : Series
            The calculated strata. Missing propensity scores and values outside of
            min of treated group or max of control group are coded as NaN.
        """
        if n_min == 'auto':
            n_min_strata = len(self.linear_terms)+2 # + self.nonlinear_terms
            n_min_tc = 3
        else:
            if type(n_min)!=dict:
                raise ValueError('n_min must be "auto" or a dictionary specifying'\
                                 '"treatment_control" and "strata", the minimum number of'\
                                 'observations in the respective groups as keys.')
            elif ('treatment_control' not in n_min) or ('strata' not in n_min):
                raise ValueError('Must specify both "strata" (e.g. K+2) '\
                                    'and "treatment_control" (e.g. 3)')
            n_min_strata = n_min['strata']
            n_min_tc = n_min['treatment_control']

        self.n_min_strata = n_min_strata
        self.n_min_tc = n_min_tc
        self.t_strata = t_strata

        # =====================================================================
        # Getting the Data In Place For The Recursion
        # =====================================================================
        df = self.data.loc[:,[self.outcome]].join(self.logodds)
        minmax = df.groupby(self.outcome)['logodds'].agg(['max','min'])

        # assigning missing logodds first, where no strata live
        df.loc[~(df.logodds.ge(minmax.loc[1,'min']) & df.logodds.le(minmax.loc[0,'max'])),
               'logodds'] = nan

        def recurse_split(low,high,strat):

            # do this every time, replace the outer df with the "current" strata
            df.loc[df.logodds.between(low,high,inclusive='both'),'strata'] = strat

            samp = df.loc[df.logodds.between(low,high,inclusive='both'),:]
            t_test = abs(ttest(samp.loc[samp.loc[:,self.outcome].eq(1),'logodds'],
                           samp.loc[samp.loc[:,self.outcome].eq(0),'logodds'],
                           nan_policy='omit').statistic)
            mid = samp.logodds.median()
            n = samp.assign(gemid = samp.logodds.ge(mid)).groupby(
                [self.outcome,'gemid'])['logodds'].count()

            # the stopping criteria
            if t_test>t_strata and min(n)>n_min_tc and min(n.groupby('gemid').sum())>n_min_strata:
                # because of the way the recursion is done, need to get next closest value to median
                lowermax = samp.loc[samp.logodds.lt(mid),'logodds'].max()
                recurse_split(low,lowermax,strat+'1')
                recurse_split(mid,high,strat+'2')

        # run the recursive algorithm
        recurse_split(df.logodds.min(),df.logodds.max(),'0')

        # create dictionary mapping these ugly strata codes to real numbers
        liststrat = sorted(list(df.strata.dropna().unique()))
        self.strata = df.strata.map(dict(zip(liststrat,range(len(liststrat)))))

        print('Sample Split Into {} Strata'.format(len(liststrat)))
        return self.strata


    def match(self, n_matches=1, replacement=True, match_covs = None, parallel = True, trim = False,
              match_order='descending', caliper=None, **kwargs):
        """
        This function calculates matches. It can either do general matching where all
        values are used or a hybrid version where you specify a set of covariates
        (should be categorical in nature) where the matching is taken to be the values
        with the closest logodds squared difference such that those covariates ALSO match.
        Matching can be done with or without replacement. The output is DataFrame where
        the index is the same as the treated individuals and the columns are the match number.
        Each value then is the corresponding _index_ of the control group unit.

        Parameters
        ----------
        n_matches : int, optional
            The number of matches to do. Default is 1.
        replacement : bool, optional
            Whether to do matching with or without replacement. Note that if matching
            is done without replacement, then the ordering is such that the treated
            individuals with the _largest_ propensity scores are matched first.
        match_covs : List, Series, or DataFrame, optional
            Matches will be done such that there are EXACT matches with these covariates.
            This is a "hybrid" matching model. Please note, if user provides a list,
            then the data must be part of the original propensity score calculation,
            otherwise the function will not know where to look for data. Otherwise, if a
            Series/DataFrame is given, then the index must match the original data.
        parallel : bool, optional
            If True, will excecute matching with replacement or hybrid matching in parallel.
            Matching without replacement cannot be done in parallel.
        trim : bool, optional
            If True, will do the matching on the optimally-trimmed sample (defined by the trim function).
        match_order : str, optional
            This option only matters for matching without replacement since the order of matches can affect
            the available matches for other units. The options are:
            - 'descending': matches will be made from highest to lowest propensity score in the treated group.
            - 'ascending': matches will be made from lowest to highest propensity score in the treated group.
            - 'original': matches will be done in the order that they are in the existing dataset.
            The default is 'descending'. This is recommended since large propensity score units are the hardest to match.
        caliper : float or int, optional
            If specified, this is the maximum distance for matches.
            The following are options for caliper that can be specified as kwargs:

            - caliper_partial : bool, optional
                If True and if only m-i matches are found for a particular unit, then this outputs a partial list.
                This option is most relevant for matching without replacement, since partial matches being freed up
                for other units could become an issue. It is less relevant for matching with replacement.
                The default is False.

            - caliper_param : str, optional values are 'logodds' or 'propscore'
                Do the caliper comparison with the log-odds ratio (the default). Other option is propensity score.

        Raises
        ------
        ValueError
            If variables are improperly defined, this prints out warnings.

        Returns
        -------
        self.matches :
            A DataFrame with the index matching the treated unit index where
            each value is the corresponding index of a control unit.
        """

        if caliper and (type(caliper)!=float and type(caliper)!=int):
            raise ValueError('Caliper must be a float or integer value. See documentation for options.')
        elif caliper and caliper<0:
            raise ValueError('Caliper must a positive number.')
        elif caliper and caliper > 0:
            caliper_partial = kwargs.get('caliper_partial', False)
            caliper_param = kwargs.get('caliper_param', 'logodds')
            test_kwargs = [x for x in kwargs.keys() if x not in ['caliper_partial','caliper_param']]
            if len(test_kwargs)>0:
                raise ValueError('The only valid extra options are caliper_partial and caliper_param.')
            if type(caliper_partial)!=bool:
                raise ValueError('caliper_partial must be True or False')
            if caliper_param not in ['logodds','propscore']:
                raise ValueError('caliper_param is "logodds" or "propscore"')
            print('Matching with caliper = {} {} units. '\
                  'Partial matches {} allowed. See documentation for options.'.format(caliper,
                    'log-odd' if caliper_param=='logodds' else 'propensity score',
                    'are' if caliper_partial else 'not'))
        else:
            caliper = None
            caliper_param = None # placeholder
            caliper_partial = None # placeholder

        # =====================================================================
        # Getting the data in place for the matching
        # =====================================================================
        # getting the propensity scores
        if not self.trimmed and trim:
            self.trim()
        if trim:
            samp = self.logodds_trim.to_frame().dropna().join(self.propscore_trim)
            samp = samp.rename({'logodds_trim':'logodds','propscore_trim':'propscore'},axis=1)
        else:
            samp = self.logodds.to_frame().join(self.propscore)

        # getting treatment and control group
        samp = samp.join(self.data.loc[:,self.outcome])
        samp = samp.rename({self.outcome:'y'},axis=1)

        if type(match_covs)!=type(None) and type(match_covs)==list:
            if not allfunc([ii in self.data.columns for ii in match_covs]):
                raise ValueError('If providing a list for hybrid matching, these '\
                                 'variables must be in the original propensity score '\
                                 'calculation. Otherwise, please provide a Series/DataFrame.')
            samp = samp.join(self.data.loc[:,match_covs])
            samp.loc[:,'_ngroup'] = samp.groupby(match_covs).ngroup()
        elif type(match_covs)!=type(None):
            # edits to the series just in case it doesn't have a name
            if type(match_covs)==Series:
                if not match_covs.name:
                    match_covs.name = 'covariate_to_match'
                match_covs = match_covs.to_frame()
            # now do this for series and dataframes.
            samp = samp.join(match_covs)
            match_covs = list(match_covs.columns)
            samp.loc[:,'_ngroup'] = samp.groupby(match_covs).ngroup()

        # get all the control group and treated group in the right order, leave them in pandas for now.
        # control group always sorted descending, and this is the only time we have to sort.
        control = samp.loc[samp.y.eq(0),:].sort_values('logodds',ascending=False)

        if match_order not in ['original','descending','ascending']:
            raise ValueError('Match order must be "original", "descending", or "ascending".')

        # save it so that we output in the correct order later
        treated = samp.loc[samp.y.eq(1),:]
        origindex = treated.index

        if replacement or match_order=='original':
            pass # no need to change the treated group
        elif match_order == 'descending':
            treated = samp.loc[samp.y.eq(1),:].sort_values('logodds',ascending=False)
        elif match_order == 'ascending':
            treated = samp.loc[samp.y.eq(1),:].sort_values('logodds',ascending=True)

        # =====================================================================
        # Functions for doing the matching
        # =====================================================================
        # a binary search function for finding min of the sorted list
        def binary_search_min(x,Y,low,high):
            ''' Returns the single closest match quickly from sorted list (ties broken randomly) '''
            # stopping criteria -- 1 or 2 items left
            if high == low:
                return low
            elif high-low==1:
                s = (Y[low:high+1]-x)**2
                return low if s[0]<=s[1] else high

            # Find the midpoint, and first condition
            m_i = (high+low)//2
            mid = (Y[m_i]-x)**2
            left = (Y[m_i-1]-x)**2
            right = (Y[m_i+1]-x)**2

            # all potential: << <= <> =< == => >< >= >>; not possible: <>
            if left>mid<right or mid==0:
                return m_i # return the index of the min, min is always 0 (so randomly found it)
            # handle the equality case first since it is a problem of being stuck at plateau
            elif left==mid==right:
                ii=2
                while m_i+ii<=high and m_i-ii>=low:
                    left = (Y[m_i-ii]-x)**2
                    right = (Y[m_i+ii]-x)**2
                    if mid<right or left<mid:
                        return binary_search_min(x,Y,low,m_i) # go left
                    elif left>mid or mid>right:
                        return binary_search_min(x,Y,m_i,high) # go right
                    # all still equal, keep going
                    ii+=1
                # left limit reached, so left == mid
                while m_i+ii<=high:
                    right = (Y[m_i+ii]-x)**2
                    if mid<right:
                        return m_i # can just return the midpoint cuz pointer at left limit
                    elif mid>right:
                        return binary_search_min(x,Y,m_i,high) # go right
                    ii+=1
                #right limit reached, so right == mid
                while m_i-ii>=low:
                    left = (Y[m_i-ii]-x)**2
                    if left<mid:
                        return binary_search_min(x,Y,low,m_i) # go left
                    elif left>mid:
                        return m_i # can just return the midpoint cuz pointer at right end
                    ii+=1
                # you reached the end, therefore the iteration can stop and return midpoint
                return m_i
            # back to the normal cases
            elif left<=mid<=right:
                return binary_search_min(x,Y,low,m_i) # go left
            elif left>=mid>=right:
                return binary_search_min(x,Y,m_i,high) # go right

        def closest_dist_ind(x,Y,nummatch):
            ''' Closest matches, returns [matches] '''
            # call the binary search function for the minimum
            minind = binary_search_min(x,Y,0,len(Y)-1)
            # some easy exists
            if nummatch == 1:
                return [minind]

            possible_combos = [list(range(minind+1-nummatch+ii,minind+1+ii))
                               for ii in range(nummatch)
                               if (minind+1-nummatch+ii>=0 and minind+ii<=len(Y)-1)]
            if len(possible_combos)==1:
                return possible_combos[0]
            return possible_combos[argmin([npsum((Y[ii]-x)**2) for ii in possible_combos])]

        def closest_dist_ind_caliper(x,xcal,Y,Ycal,nummatch,calippartial=caliper_partial,calval=caliper):
            ''' Closest matches, returns [matches] with caliper comparison done '''
            # call the binary search function for the minimum
            minind = binary_search_min(x,Y,0,len(Y)-1)
            # some easy exists
            if nummatch == 1:
                if abs(Ycal[minind]-xcal)<=calval:
                    return [minind]
                return [NA]

            possible_combos = [list(range(minind+1-nummatch+ii,minind+1+ii))
                               for ii in range(nummatch)
                               if (minind+1-nummatch+ii>=0 and minind+ii<=len(Y)-1)]

            if len(possible_combos)==1:
                mininds = possible_combos[0]
            else:
                mininds = possible_combos[argmin([npsum((Y[ii]-x)**2) for ii in possible_combos])]

            # get the potential output, that fills with nans, values that are above caliper
            out = [ii if abs(Ycal[ii]-xcal)<=calval else NA for ii in mininds]
            if calippartial:
                return out
            # if one of the outputs is nan, then return list of nans
            if not allfunc(notna(out)):
                return [NA]*nummatch
            return out


        def closest_dist_val(x,Y,Yind,nummatch):
            ''' Closest matches, returns Yind[matches] '''
            # call the binary search function for the minimum
            minind = binary_search_min(x,Y,0,len(Y)-1)
            # some easy exists
            if nummatch == 1:
                return [Yind[minind]]

            possible_combos = [list(range(minind+1-nummatch+ii,minind+1+ii))
                               for ii in range(nummatch)
                               if (minind+1-nummatch+ii>=0 and minind+ii<=len(Y)-1)]
            if len(possible_combos)==1:
                return list(Yind[possible_combos[0]])
            mininds = possible_combos[argmin([npsum((Y[ii]-x)**2) for ii in possible_combos])]
            return list(Yind[mininds])

        def closest_dist_val_caliper(x,xcal,Y,Ycal,Yind,nummatch,calippartial=caliper_partial,calval=caliper):
            ''' Closest matches, returns Yind[matches] with caliper comparison done '''
            # call the binary search function for the minimum
            minind = binary_search_min(x,Y,0,len(Y)-1)
            # some easy exists
            if nummatch == 1:
                if abs(Ycal[minind]-xcal)<=calval:
                    return [Yind[minind]]
                return [NA]

            possible_combos = [list(range(minind+1-nummatch+ii,minind+1+ii))
                               for ii in range(nummatch)
                               if (minind+1-nummatch+ii>=0 and minind+ii<=len(Y)-1)]

            if len(possible_combos)==1:
                mininds = possible_combos[0]
            else:
                mininds = possible_combos[argmin([npsum((Y[ii]-x)**2) for ii in possible_combos])]

            out = [Yind[ii] if abs(Ycal[ii]-xcal)<=calval else NA for ii in mininds]

            if calippartial:
                return out
            # if one of the outputs is nan, then return list of nans
            if not allfunc(notna(out)):
                return [NA]*nummatch
            return out


        # the matching function for all the treated units, for parallelization
        def closest_with_replacement(treat_lo,cont_lo,nm,par,treat_ps,cont_ps,caliper=caliper,
                                     caliper_partial=caliper_partial,caliper_param=caliper_param):

            treatInd = treat_lo.index
            treatVals = treat_lo.to_numpy() # just care about the values
            contInds = cont_lo.index.to_numpy() # the index values to be added
            contVals = cont_lo.to_numpy() # values, already sorted

            if not caliper:
                # doing the actual matching
                if par:
                    m = Parallel(n_jobs=-1)(
                            delayed(closest_dist_val)(x,contVals,contInds,nm) for x in treatVals)
                else:
                    m = []
                    for x in treatVals:
                        m.append(closest_dist_val(x,contVals,contInds,nm))
                output = DataFrame(data=m,
                                   index=treatInd,
                                   columns=['match_{}'.format(ii) for ii in range(1,n_matches+1)])
                return output

            # deal with the caliper
            if caliper_param == 'logodds':
                treatCal = treatVals
                contCal = contVals
            else:
                treatCal = treat_ps.to_numpy()
                contCal = cont_ps.to_numpy()

            if par:
                m = Parallel(n_jobs=-1)(
                        delayed(closest_dist_val_caliper)(x=treatVals[ii],xcal=treatCal[ii],
                                                          Y=contVals,Ycal=contCal,
                                                          Yind=contInds,nummatch=nm,
                                                          calval=caliper,calippartial=caliper_partial)
                                for ii in range(len(treatVals))
                                )
            else:
                m = []
                for ii in range(len(treatVals)):
                    m.append(closest_dist_val_caliper(x=treatVals[ii],xcal=treatCal[ii],
                                                      Y=contVals,Ycal=contCal,
                                                      Yind=contInds,nummatch=nm,
                                                      calval=caliper,calippartial=caliper_partial))
            output = DataFrame(data=m,
                               index=treatInd,
                               columns=['match_{}'.format(ii) for ii in range(1,n_matches+1)])
            return output

        # the matching function for all the treated units, without replacement, no parallel here.
        def closest_wo_replacement(treat_lo,cont_lo,nm,treat_ps,cont_ps,caliper=caliper,
                                     caliper_partial=caliper_partial,caliper_param=caliper_param):
            if len(treat_lo)*nm>len(cont_lo):
                raise ValueError('Not Enough Controls in all sub-blocks. Please redefine covariates')

            treatInd = treat_lo.index
            treatVals = treat_lo.to_numpy() # just care about the values
            contInds = cont_lo.index.to_numpy() # the index values to be added
            contVals = cont_lo.to_numpy() # values, already sorted

            if not caliper:
                # the loop
                m = []
                for x in treatVals:
                    mtemp = closest_dist_ind(x,contVals,nm)
                    m.append(list(contInds[mtemp]))
                    # getting rid of the matched ones
                    contVals = delete(contVals,mtemp)
                    contInds = delete(contInds,mtemp)
                out = DataFrame(data=m,
                                index=treatInd,
                                columns=['match_{}'.format(ii) for ii in range(1,n_matches+1)])
                return out

            # dealing with the caliper situation
            if caliper_param == 'logodds':
                treatCal = treatVals
                contCal = contVals
            else:
                treatCal = treat_ps.to_numpy()
                contCal = cont_ps.to_numpy()

            m = []
            for ii in range(len(treatVals)):
                mtemp = closest_dist_ind_caliper(x=treatVals[ii],xcal=treatCal[ii],
                                                 Y=contVals,Ycal=contCal,nummatch=nm,
                                                 calippartial=caliper_partial,calval=caliper)
                m.append(list(contInds[mtemp]))
                # getting rid of the matched ones
                contVals = delete(contVals,[ii for ii in mtemp if notna(ii)])
                contInds = delete(contInds,[ii for ii in mtemp if notna(ii)])
                contCal  = delete(contCal, [ii for ii in mtemp if notna(ii)])
            out = DataFrame(data=m,
                            index=treatInd,
                            columns=['match_{}'.format(ii) for ii in range(1,n_matches+1)])
            return out

        # =====================================================================
        # Running match with no hybrid units
        # =====================================================================
        if not match_covs:
            treated_LO = treated.logodds
            control_LO = control.logodds
            treated_PS = treated.propscore
            control_PS = control.propscore
            if replacement:
                matches = closest_with_replacement(treated_LO,control_LO,n_matches,parallel,treated_PS,control_PS)
            else:
                if len(treated)*n_matches>len(control):
                    raise ValueError('Not Enough Controls for {} Matches'.format(n_matches))
                matches = closest_wo_replacement(treated_LO,control_LO,n_matches,treated_PS,control_PS)

        # =====================================================================
        # If doing hybrid approach: need to loop over covariate groups.
        # =====================================================================
        else:
            if replacement:
                if parallel:
                    matches = Parallel(n_jobs=-1)(
                        delayed(closest_with_replacement)(
                            treated.loc[treated._ngroup.eq(group),'logodds'],
                            control.loc[control._ngroup.eq(group),'logodds'],
                            n_matches,True,
                            treated.loc[treated._ngroup.eq(group),'propscore'],
                            control.loc[control._ngroup.eq(group),'propscore']
                            ) for group in treated._ngroup.unique())
                else:
                    matches = []
                    for group in treated._ngroup.unique():
                            matches.append(closest_with_replacement(
                            treated.loc[treated._ngroup.eq(group),'logodds'],
                            control.loc[control._ngroup.eq(group),'logodds'],
                            n_matches,False,
                            treated.loc[treated._ngroup.eq(group),'propscore'],
                            control.loc[control._ngroup.eq(group),'propscore']))
            else:
                if parallel:
                    matches = Parallel(n_jobs=-1)(
                        delayed(closest_wo_replacement)(
                            treated.loc[treated._ngroup.eq(group),'logodds'],
                            control.loc[control._ngroup.eq(group),'logodds'],
                            n_matches,
                            treated.loc[treated._ngroup.eq(group),'propscore'],
                            control.loc[control._ngroup.eq(group),'propscore']
                            ) for group in treated._ngroup.unique())
                else:
                    matches = []
                    for group in treated._ngroup.unique():
                        matches.append(closest_wo_replacement(
                            treated.loc[treated._ngroup.eq(group),'logodds'],
                            control.loc[control._ngroup.eq(group),'logodds'],
                            n_matches,
                            treated.loc[treated._ngroup.eq(group),'propscore'],
                            control.loc[control._ngroup.eq(group),'propscore']))
            matches = concat(matches)

        matches = matches.loc[origindex,:]
        self.matches = matches
        return matches
