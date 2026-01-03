import plotly.graph_objects as go
import numpy as np

def plot_probability_distribution(y_true, y_scores, thresholds):
    """
    Plots the predicted probability distribution for each class using Plotly.
    """
    classes = np.unique(y_true)
    fig = go.Figure()

    if y_scores.ndim == 1 or y_scores.shape[1] == 2:
        # For binary classification
        pos_prob = y_scores[:, 1] if y_scores.ndim > 1 else y_scores
        fig.add_trace(go.Histogram(
            x=pos_prob[y_true==0],
            name='Class 0',
            opacity=0.5
        ))
        fig.add_trace(go.Histogram(
            x=pos_prob[y_true==1],
            name='Class 1',
            opacity=0.5
        ))
        # Add the optimal threshold line
        threshold_value = thresholds if np.isscalar(thresholds) else thresholds[1]
        fig.add_vline(x=threshold_value, line=dict(color='red', dash='dash'), name='Optimal Threshold')
        
        fig.update_layout(
            xaxis_title='Predicted Probability for Positive Class',
            yaxis_title='Frequency',
            title='Predicted Score Distribution'
        )
    else:
        # For multiclass classification
        for k, cls in enumerate(classes):
            fig.add_trace(go.Histogram(
                x=y_scores[:, k],
                name=f'Class {cls}',
                opacity=0.5
            ))
            fig.add_vline(x=thresholds[k], line=dict(color='red', dash='dash'), name='Optimal Threshold')
            fig.update_layout(
                title=f'Class {cls} Probability Distribution'
            )
    
    fig.show()