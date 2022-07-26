import sys, os
sys.path.append(os.getcwd())
from typing import Tuple, NamedTuple
from statistics_functions.functions import *
from scipy.stats import f
import pandas as pd

class FactorialAnovaStatistics(NamedTuple):
    sum_sq: float
    df: int
    statistic: float
    pvalue: float

class OneWayAnovaStatistics(NamedTuple):
    statistic: float
    pvalue: float

def one_way_anova(*args: list) -> OneWayAnovaStatistics:
    """
    Return statistic value of the "one way anova" and it's pvalue

    Info:
    -----
    ANOVA: Analysis of Variance.

    One way anova compare all passed groups to each other and:
    * H0 says: there is no difference between this groups (M1 = M2 = ... = Mn)
    * H1 says: at least one group of data has different sample mean

    We assume that the variance of our data can be explained by two things:
    * Variability between the groups
    * Variability within the groups

    If SSB much greater than SSW, then probably at least 2 mean values are different from each other.
    To find out, how likely is that, we calculate the p-value, using F value.

    Interpretation:
    ---------------
    Lets assume, we repeating our experiment many times when H0 is TRUE.
    It means, that all our sample means ARE EQUAL. It's like we getting 3 samples from 1 population.
    So, our SSB tends to 0, because we assume, if we have H0, there is no difference between sample means.
    SSW is the total value of difference within the group, it's like the correction to our computation.
    This means, that in most cases, if H0 is TRUE, the F value will be very small.

    Here we have F distribution. This distribution not like the normal distribution, 
    it has asymmetry, skewed to the left (positive skew) (Sometimes max value is close to 0). If we get large F value, we may reject the null hypothesis.
    To reject the null hypothesis, we calculate the p-value.

    Steps:
    ------
    1. Find sum of squares between groups
    2. Find sum of squares within groups
    3. Calculate the "F" value

    Formula:
    --------
    `F = (SSB / df_ssb) / (SSW / df_ssw)`

    -----
    Args:
    sample_1, sample_2, ... ,sample_n: (list) Samples of data to compare

    Return:
    statistic: (float) statistic F value
    pvalue: (float) pvalue for statistic
    """
    ssb, df_ssb = SSB(args)
    ssw, df_ssw = SSW(args)

    ssb_div = ssb / df_ssb
    ssw_div = ssw / df_ssw

    f_val = ssb_div / ssw_div
    p_val = f.sf(f_val, df_ssb, df_ssw)
    
    return OneWayAnovaStatistics(f_val, p_val)

def TSS(vector: list) -> float:
    """
    Return total sum of squares

    Info:
    -----
    This value shows, how high is the variability of our data, without dividing data into groups.
    It's like variance, but we are not going to divide by "NO".

    Formula:
    --------
    `TSS = Σ( (yi - Y)^2 )`
        
        where
            yi: item in vector,
            Y: vector mean value

    `df = NO - 1`

        where
            df: Degrees of freedom
            NO: Number observations

    Steps:
    ------
    1. Calculate one general mean of all groups
    2. For each item in vector calculate the squared difference between this item and the general mean
    3. Sum this difference values

    -----
    Args:
        vector (list): 1D vector.

    -------
    Return:
        tss: float
            The calculated total sum of squares
        df: int
            The degrees of freedom
    """
    Y = np.mean(vector)
    return np.sum([(yi - Y)**2 for yi in vector])

def SSB(groups: list) -> Tuple[float, int]:
    """Return the sum of squares between groups and ddof

    Info:
    -----
    The SSB (sum of squares between groups) means, how in total 
    the mean of group (m) deviates from its general mean (X).

    If there is a big difference between mean in group and the general mean, 
    we can assume, that there is an difference between groups and we 
    may reject the null hypothesis. Otherwise if SSB is a small value, then we
    may assume, that there is not much difference between mean in groups. 

    Formula:
    --------
    `SSB = NO * (m - X)`

        where
            NO: Number observations
            m: Mean within the group
            X: General mean of all groups

    `df = number_of_groups - 1`

    -----
    Args:
        groups (list): Groups of our data observations

    Return:
        ssb: float
            The calculated sum of squares between the groups
        df: int
            The degrees of freedom
    """
    X = mean(flatten(groups))
    df = len(groups) - 1
    ssb = sum([len(group) * (mean(group) - X)**2 for group in groups])
    return (ssb, df)

def SSW(groups: list) -> Tuple[float, int]:
    """Return the sum of squares within groups and ddof

    Info:
    -----
    The SSW (sum of squares within groups) shows, how much 
    an items in the groups deviates from its mean in group.
    If SSW is a small value, then the data within the groups doesn't deviates much
    from it's mean. Otherwise there is big variance in the groups.

    If SSW is small and SSB is large, there is a chance to get rid of the H0 hypothesis.

    Formula:
    --------
    `SSW = Σ(TSS(group_i))`

        where
            TSS: Total sum of squares for each group
            group_i: Specific group

    `df = Σ(NO_i - 1)`
        
        where
            NO_i: Number observations in group

    -----
    Args:
        groups (list): Groups of our data observations

    Return:
        ssw: float
            The calculated sum of squares within the groups
        df: int
            The degrees of freedom
    """
    df = sum([len(group)-1 for group in groups])
    ssw = sum([TSS(group) for group in groups])
    return (ssw, df)

def two_way_anova(data: pd.DataFrame, features: list, target: str) -> FactorialAnovaStatistics:
    """Return the f statistic of data and its pvalue

    Info:
    -----
    A two-way ANOVA (“analysis of variance”) is used to determine whether
    or not there is a statistically significant difference between the means 
    of three or more independent groups that have been split on two variables 
    (sometimes called “factors”).

    Steps:
    ------
    1. Calculate the mean of all values (grand mean)
    2. Calculate Sum of Squares for first factor (feature):
        Calculate the mean for all first feature group.
        All means substract from the grand mean.
        Sum all squared differences.
    3. Calculate Sum of Squares for second factor (feature):
        The same process - as in step 2.
    4. Calculate Sum of Squares Within (Error)

    -----
    Args:
        data (pd.DataFrame): DataFrame with data to compare
        features (list): the features to compare

    Returns:
        Tuple[float, float]: F statistic and p value
    """
    # 1. Find the sum of squares for each feature
    statistic, ss_ssb, df_ssb = SSB_pd(data, features, target)

    # 2. Find the sum of squares within (SSW) (Error)
    statistic, ss_ssw, df_ssw = SSW_pd(statistic, data, features, target)

    # 3. Calculate total sum of squares
    ss_total = TSS(data["expr"].values)

    # 4. Calculate Sum of Squares Interaction
    statistic, ss_interaction, df_interaction = interaction(statistic, ss_total, ss_ssb, df_ssb, ss_ssw, features)
    
    # 5. Calculate F values
    ms_ssb = [ssb_i / df_ssb_i for ssb_i, df_ssb_i in zip(ss_ssb, df_ssb)]
    ms_ssw = ss_ssw / df_ssw
    ms_interaction = ss_interaction / df_interaction
    f_features = [i / ms_ssw for i in ms_ssb]
    f_interaction = ms_interaction / ms_ssw
    print(f_features)
    print(f_interaction)

    # 6. Pvalue
    p_features = [f.sf(f_feature, df_ssb, df_ssw) for f_feature in f_features]
    p_interaction = f.sf(f_interaction, df_ssb, df_ssw)
    print(p_features)
    print(p_interaction)
    
    # Take all together
    statistic = pd.DataFrame(statistic)
    print("[INFO] The difference between group mean and gen mean")
    print(statistic)

def SSW_pd(statistic: dict, data: pd.DataFrame, features: list, target: str):
    groupped = data.groupby(features)
    ss_resid_list = []
    df_resid = 0
    for _, groupped_df in groupped:
        values = groupped_df[target]
        group_mean = np.mean(values)
        ss = np.sum([(vi - group_mean)**2 for vi in values])
        ss_resid_list.append(ss)
        df_resid += groupped_df.shape[0] - 1
    ss_resid = sum(ss_resid_list)
    statistic["feature"].append("residual")
    statistic["sum_sq"].append(ss_resid)
    statistic['df'].append(df_resid)
    
    return statistic, ss_resid, df_resid

def SSB_pd(data: pd.DataFrame, features: list, target: str):
    statistic = {"feature": [], "sum_sq": [], "df": []}
    ssb_features = []
    df_ssb = []
    grand_mean = np.mean(data["expr"].values)
    # For each feature... [age, dose]
    for feature in features:
        feature_means = [] # add up the means for each group of feature
        feature_group = data.groupby(feature) # group by feature (age)
        # For each group with feature find the mean...
        for _, feature_df in feature_group:
            values = feature_df[target]
            feature_mean = np.mean(values)
            feature_means.append(feature_mean)
        # Calculate the sum of squared difference 
        # between the group mean and the gen mean
        n = feature_df.shape[0]
        sum_of_squares = np.sum([n * (fm - grand_mean)**2 for fm in feature_means])
        statistic['feature'].append(feature)
        statistic['sum_sq'].append(sum_of_squares)
        statistic['df'].append(len(features)-1)
        ssb_features.append(sum_of_squares)
        df_ssb.append(data[feature].nunique()-1)
        
    return statistic, ssb_features, df_ssb

def interaction(statistic, total, ssb, df_ssb, ssw, features):
    ss_interaction = total - np.sum(ssb) - ssw
    df = np.cumprod(df_ssb)[-1]
    statistic["feature"].append(":".join([*features]))
    statistic["sum_sq"].append(ss_interaction)
    statistic["df"].append(df)
    return statistic, ss_interaction, df
