
#-------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------

def filter_nan(s,o):
        """
        this functions removed the data  from simulated and observed data
        whereever the observed data contains nan

        this is used by all other functions, otherwise they will produce nan as
        output
        """
        import numpy as np
        data = np.array([s,o])
        data = np.transpose(data)
        data = data[~np.isnan(data).any(1)]
        return data[:,0],data[:,1]

#-------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------

def no_nans(A1, A2):
    ''' returns the mask of nans for 2 arrays'''
    import numpy as np
    mask = ~np.isnan(A1) & ~np.isnan(A2)
    return mask

#-------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------

def RMSE_fun(s,o):
        """
        Root Mean Squared Error
        input:
                s: simulated
                o: observed
        output:
                rmses: root mean squared error
        """
        import numpy as np
        s,o = filter_nan(s,o)
        return np.sqrt(np.mean((s-o)**2))

#-------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------

def R2_fun(s,o):
    """
    R^2 or Correlation coefficient^0.5
    input:
            s: simulated
            o: observed
    output:
            R^2
    """
    import numpy as np
    from scipy import stats

    o=np.array(o)
    s=np.array(s)

    if ((o == o[0]).all())|((s == s[0]).all()):
        r2_o_d_=np.nan
    else:
        m_o_d = no_nans(np.array(o),np.array(s))
        if len(np.array(o)[m_o_d])==0 | len(np.array(s)[m_o_d])==0:
            r2_o_d_ = np.nan
        else:
            stats_o_d = stats.linregress(np.array(o)[m_o_d],np.array(s)[m_o_d])
            # slope_o_d = stats_o_d[0];
            # int_o_d = stats_o_d[1];
            r2_o_d_ = stats_o_d[2]**2

    return r2_o_d_

#-------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------

def KT_fun(s,o):
    import scipy.stats
    """
    Kendalls Tao
    input:
        s: simulated
        o: observed
    output:
        tau: Kendalls Tao
        p-value
    """
    s,o = filter_nan(s,o)
    tao = scipy.stats.stats.kendalltau(s, o)[0]
    pvalue = scipy.stats.stats.kendalltau(s, o)[1]
    return tao

#-------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------

def BIAS_fun(s, o):
    '''
    returns the mean bias of the simulated data in relation ot the observations

    input:
        s: simulated
        o: observed
    output:
        bias
    '''
    import numpy as np
    s,o = filter_nan(s,o)

    dif = s-o
    bias = np.mean(dif)
    return bias

#-------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------

def ABS_BIAS_fun(s, o):
    '''
    returns the mean absolute difference (bias) between the simulated data in relation ot the observtion
    input:
        s: simulated
        o: observed
    output:
        abs_bias: the mean of the absolute difference between simulations and observation
    '''
    import numpy as np
    s,o = filter_nan(s,o)

    dif = np.absolute(s-o)
    abs_bias = np.mean(dif)
    return abs_bias

#-------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------

def get_summary_stats(s,o):
  '''
  returns summary statistics:
  * mbe: bias
  * mae: absolute bias
  * rmse: root mean square error
  * r2: correlation coefficient
  * kt: Kendalls Tau

  inputs:
  - s: simulated data
  - o: in situ observations
  '''
  import sklearn.metrics as metrics
  import numpy as np
  s,o = filter_nan(s,o)
  mbe = BIAS_fun(s,o)
  mae = ABS_BIAS_fun(s, o)
  rmse = RMSE_fun(s,o) #mse**(0.5)
  r2 = R2_fun(s,o)
  kt = KT_fun(s,o)
  return [mbe, mae, rmse, r2, kt]
