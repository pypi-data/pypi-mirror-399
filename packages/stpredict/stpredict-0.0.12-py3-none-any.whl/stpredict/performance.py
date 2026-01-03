import warnings

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import numpy as np
    import warnings
    from sklearn import metrics
    from sklearn.preprocessing import label_binarize
    from math import log

warnings.filterwarnings("once")

# mean absolute scaled error
def mase(true_values, predicted_values, trivial_values):
    prediction_mae = metrics.mean_absolute_error(true_values, predicted_values)
    trivial_mae = metrics.mean_absolute_error(true_values, trivial_values)
    if trivial_mae == 0:
        trivial_mae = 10e-5
    
    return prediction_mae/trivial_mae

# ROC AUC for binary and multiclass classification
def auc(true_values, y_score, labels=None):
    # detecting how many classes the classification problem have
    number_of_classes = len(labels)
    
    
    if number_of_classes == 1 or number_of_classes == 2:    # binary classification
        true_values_binary = np.where(true_values == labels[0], np.full(true_values.shape, 0), np.full(true_values.shape, 1))
        auc = metrics.roc_auc_score(
            y_true=true_values_binary, 
            y_score=y_score[:, 1]
        )

        return auc
    
    else:    # non-binary classification
        # labelize the true_values to be usable in 'precision_recall_curve' from 'sklearn.metrics'
        true_values = label_binarize(true_values, classes=labels)

        auc = 0
        false_positives = dict()
        true_positives = dict()

        for i in range(number_of_classes):
            # Data to plot precision - recall curve
            false_positives[i], true_positives[i], _ = metrics.roc_curve(true_values[:, i], y_score[:, i])
            
            auc += metrics.roc_auc_score(
                y_true=true_values[:, i], 
                y_score=y_score[:, i], 
                multi_class='ovo', 
                labels=labels
            )

        # the final auc value is mean of auc between all classes
        auc /= (i+1)

        return auc

def aupr(true_values, probas_pred, labels):
    # detecting how many classes the classification problem have
    number_of_classes = len(labels)
    
    # multiclass classification
    if number_of_classes > 2:
        # labelize the true_values to be usable in 'precision_recall_curve' from 'sklearn.metrics'
        true_values = label_binarize(true_values, classes=labels)
    
        auc_precision_recall = 0
        precision = dict()
        recall = dict()

        for i in range(number_of_classes):
            # Data to plot precision - recall curve
            precision[i], recall[i], _ = metrics.precision_recall_curve(true_values[:, i], probas_pred[:, i])
            # Use AUC function to calculate the area under the curve of precision recall curve
            auc_precision_recall += metrics.auc(recall[i], precision[i])

        # the final aupr value is mean of aupr between all classes
        auc_precision_recall /= (i+1)
    
        return auc_precision_recall
    
    # binary classification
    else:
        # Data to plot precision - recall curve
        precision, recall, _ = metrics.precision_recall_curve(true_values, probas_pred[:,1], pos_label=labels[1])
        # Use AUC function to calculate the area under the curve of precision recall curve
        auc_precision_recall = metrics.auc(recall, precision)

        return auc_precision_recall

def aic_regression(y_true, y_pred, k):
    # k = number of independent variables to build model
    mse_error = metrics.mean_squared_error(y_true, y_pred)
    aic = 2*k - 2*log(mse_error)
    return aic

def bic_regression(y_true, y_pred, k):
    # k = number of independent variables to build model
    # n = sample size (#observations)
    n = len(y_true)
    mse_error = metrics.mean_squared_error(y_true, y_pred)
    bic = k*log(n) - 2*log(mse_error)
    return bic

# log_loss (in this function, likelihood is defined as cross-entropy loss, and so it's better to use it for classification)
def likelihood(y_true, y_pred, labels):
    return (metrics.log_loss(y_true=y_true, y_pred=y_pred, labels=labels))

def aic_classification(y_true, y_pred, k, labels):
    # k = number of independent variables to build model
    n = len(y_true)
    likelihood_error = likelihood(y_true, y_pred, labels)
    aic = (2*k)/n + (2*likelihood_error)/n
    return aic

def bic_classification(y_true, y_pred, k, labels):
    # k = number of independent variables to build model
    # n = sample size (#observations)
    n = len(y_true)
    likelihood_error = likelihood(y_true, y_pred, labels)
    bic = k*log(n) + 2*likelihood_error
    return bic

# root mean squared error
def rmse(true_values, predicted_values):
    res = np.sqrt(metrics.mean_squared_error(true_values, predicted_values))
    return res.item()

# relative root mean squared error
def rrmse(true_values, predicted_values, eps=1e-12):
    calculated_rmse = rmse(true_values, predicted_values)
    denom = np.abs(np.mean(true_values))
    if denom < eps:
        return float('inf') if calculated_rmse > 0 else 0.0
    res = 100.0 * calculated_rmse / denom
    return res.item()

# weighted mean absolute precentage error
def wmape(true_values, predicted_values, eps=1e-12):
    num = np.sum(np.abs(true_values - predicted_values))
    denom = np.sum(np.abs(true_values))
    if denom < eps:
        return float('inf') if num > 0 else 0.0
    res = 100.0 * num / denom
    return res.item()

# absolute percentage bias
def apb(true_values, predicted_values, eps=1e-12):
    num = np.abs(np.sum(true_values - predicted_values))
    denom = np.sum(np.abs(true_values))
    if denom < eps:
        return float('inf') if num > 0 else 0.0
    res = 100.0 * num / denom
    return res.item()

# willmott's index of agreement
def wi(true_values, predicted_values, eps=1e-12):
    mean_true = np.mean(true_values)

    num = np.sum((predicted_values - true_values) ** 2)
    denom = np.sum((np.abs(predicted_values - mean_true) + np.abs(true_values - mean_true)) ** 2)

    if denom < eps:
        return 1.0 if num < eps else 0.0
    res = 1.0 - (num / denom)
    return res.item()

# skill score (or Nash-Sutcliffe efficiency (ENS))
def ss(true_values, predicted_values, eps=1e-12):
    mean_true = np.mean(true_values)

    num = np.sum((predicted_values - true_values) ** 2)
    denom = np.sum((true_values - mean_true) ** 2)

    if denom < eps:
        return 1.0 if num < eps else float('-inf')
    res = 1.0 - (num / denom)
    return res.item()

# Legates–McCabe index (LM)
def lm(true_values, predicted_values, eps=1e-12):
    mean_true = np.mean(true_values)

    num = np.sum(np.abs(true_values - predicted_values))
    denom = np.sum(np.abs(true_values - mean_true))

    if denom < eps:
        return 1.0 if num < eps else float('-inf')
    res = 1.0 - (num / denom)
    return res.item()

# Kling–Gupta efficiency (KGE)
def kge(true_values, predicted_values, eps=1e-12):
    r = pearson(true_values, predicted_values, eps=eps)
    mean_true = np.mean(true_values)
    mean_pred = np.mean(predicted_values)
    std_true = np.std(true_values, ddof=0)
    std_pred = np.std(predicted_values, ddof=0)

    beta = (mean_pred / mean_true) if np.abs(mean_true) >= eps else np.inf
    gamma = (std_pred / std_true) if std_true >= eps else np.inf
    
    res = 1.0 - np.sqrt((r - 1.0) ** 2 + (beta - 1.0) ** 2 + (gamma - 1.0) ** 2)
    return res.item()

# Pearson correlation coefficient
def pearson(true_values, predicted_values, eps=1e-12):
    true_values_mean = np.mean(true_values)
    predicted_values_mean = np.mean(predicted_values)
    num = np.sum((true_values - true_values_mean) * (predicted_values - predicted_values_mean))
    denom = np.sqrt(np.sum((true_values - true_values_mean) ** 2) * np.sum((predicted_values - predicted_values_mean) ** 2))
    if denom < eps:
        return 0.0
    res = num / denom
    return res.item()

def performance(
        true_values, predicted_values, 
        performance_measures=['MAPE'], trivial_values=[], 
        model_type='regression', num_params=1, 
        labels=None):
    """
    Parameters:
        true_values:    list or array
            ground truth for target values
        
        predicted_values:    list or array
            predicted values for target
        
        performance_measures:    list or array
            a list of performance measures
        
        trivial_values:    list or array
            just use this when want to calculate 'MASE'
        
        model_type:    {'regression' or 'classification'}
            type of model used for solving the problem, just needed when want to calculate 'AIC' or 'BIC'
        
        num_params: int
            number of independent variables to build model, just use it when want to calculate 'AIC' or 'BIC'
        
        labels: list or array
            list of labels for classification problems

    Returns:
        errors:    list
            list of values for errors specified in 'performance_measures'
    """
    
    errors = []

    # converting inputs to arrays
    true_values = np.asarray(true_values, dtype=float)
    predicted_values = np.asarray(predicted_values, dtype=float)
    trivial_values = np.asarray(trivial_values, dtype=float)

    # moving on performance_measures and calculating errors
    for error_type in performance_measures:
        if error_type.lower() == 'mae':
            errors.append(metrics.mean_absolute_error(true_values, predicted_values))
        elif error_type.lower() == 'mape':
            errors.append(metrics.mean_absolute_percentage_error(true_values, predicted_values))
        elif error_type.lower() == 'mse':
            errors.append(metrics.mean_squared_error(true_values, predicted_values))
        elif error_type.lower() == 'rmse':
            errors.append(rmse(true_values, predicted_values))
        elif error_type.lower() == 'rrmse':
            errors.append(rrmse(true_values, predicted_values))
        elif error_type.lower() == 'wmape':
            errors.append(wmape(true_values, predicted_values))
        elif error_type.lower() == 'apb':
            errors.append(apb(true_values, predicted_values))
        elif error_type.lower() == 'wi':
            errors.append(wi(true_values, predicted_values))
        elif error_type.lower() == 'skill_score':
            errors.append(ss(true_values, predicted_values))
        elif error_type.lower() == 'lm':
            errors.append(lm(true_values, predicted_values))
        elif error_type.lower() == 'kge':
            errors.append(kge(true_values, predicted_values))
        elif error_type.lower() == 'pearson_r':
            errors.append(pearson(true_values, predicted_values))
        elif error_type.lower() == 'evs':
            errors.append(metrics.explained_variance_score(true_values, predicted_values))
        elif error_type.lower() == 'r2_score':
            errors.append(metrics.r2_score(true_values, predicted_values))
        elif error_type.lower() == 'mase':
            errors.append(mase(true_values, predicted_values, trivial_values))
        elif error_type.lower() == 'auc':
            errors.append(auc(true_values, predicted_values, labels))
        elif error_type.lower() == 'aupr':
            errors.append(aupr(true_values, predicted_values, labels))
        elif error_type.lower() == 'aic':
            if num_params is None:    # if num_params is None, then None value for AIC will be returned
                errors.append(None)
            else:
                if model_type == 'regression':
                    errors.append(aic_regression(true_values, predicted_values, num_params))
                elif model_type == 'classification':
                    errors.append(aic_classification(true_values, predicted_values, num_params, labels))
        elif error_type.lower() == 'bic':
            if num_params is None:    # if num_params is None, then None value for BIC will be returned
                errors.append(None)
            else:
                if model_type == 'regression':
                    errors.append(bic_regression(true_values, predicted_values, num_params))
                elif model_type == 'classification':
                    errors.append(bic_classification(true_values, predicted_values, num_params, labels))
        elif error_type.lower() == 'likelihood':
            errors.append(likelihood(true_values, predicted_values, labels))

    return errors
