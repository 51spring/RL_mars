"""Static plot FC stock dispersion with paired depths; not daily SWC uncertainty."""
import math
import statistics


def summarize_fc_plots(values,thickness_cm):
    if len(values)<2 or not thickness_cm or any(len(row)!=len(thickness_cm) for row in values):
        raise ValueError('At least two complete aligned plot rows required')
    if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or not 0<=v<=100 for row in values for v in row):
        raise ValueError('Complete finite volumetric FC percent required')
    if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or v<=0 for v in thickness_cm):
        raise ValueError('Positive finite layer thickness required')
    weights=[d*.1 for d in thickness_cm]
    stocks=[math.fsum(v*w for v,w in zip(row,weights)) for row in values]
    means=[statistics.fmean(row[j] for row in values) for j in range(len(weights))]
    covariance=[[math.fsum((r[i]-means[i])*(r[j]-means[j]) for r in values)/(len(values)-1)
        for j in range(len(weights))] for i in range(len(weights))]
    variance=math.fsum(weights[i]*weights[j]*covariance[i][j] for i in range(len(weights)) for j in range(len(weights)))
    return dict(n=len(values),plot_fc_storage_mm=stocks,mean_fc_storage_mm=statistics.fmean(stocks),
        sample_sd_fc_storage_mm=statistics.stdev(stocks),
        conditional_se_fc_mean_mm=statistics.stdev(stocks)/math.sqrt(len(values)),
        depth_covariance_percent_squared=covariance,covariance_stock_variance_mm2=variance,
        variance_if_depths_independent_mm2=math.fsum(weights[j]**2*covariance[j][j] for j in range(len(weights))),
        daily_swc_uncertainty_available=False,model_residual_uncertainty_available=False)
