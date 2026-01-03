from ..tensor import Tensor, array
from ..utils import *


class Metric:
    """Base class for all metrics."""
    def __init__(self):
        self.metric_val: dict[str, float] = {}
        self.count: int = 0

    def __call__(self, z, y, *args, **kwargs) -> 'Metric':
        """Calls the metric compute method with the provided predictions and targets.
        @param z: Predictions (logits or outputs of the model).
        @param y: Ground truth labels or targets.
        """
        z = z if isinstance(z, Tensor) else tensor(z)
        y = y if isinstance(y, Tensor) else tensor(y)
        metric = self.compute(z, y, *args, **kwargs)

        if not isinstance(metric, dict):
            raise ValueError("Metric compute method must return a dictionary.")
        
        metric = {k: v.data.mean() for k, v in metric.items()}
        self.metric_val = {k: self.metric_val.get(k, 0) + v for k, v in metric.items()}
        self.count += 1
        return self
    
    def __getitem__(self, key: str) -> float:
        """Allows access to individual metric values by key."""
        return self.metric_val.get(key, None)

    def __repr__(self) -> str:
        """Returns a string representation of the metric with its value if computed."""
        if self.count > 0:
            metric_str = ""
            for key, value in self.metric_val.items():
                metric_str += f"{key}: {(value / self.count):.4f}, "
            return metric_str[:-2]  # Remove trailing comma and space
        else:
            return "No metric computed yet."
        
    def reset(self) -> None:
        """Resets the accumulated metric values and count."""
        self.metric_val = {}
        self.count = 0
        
    @no_grad
    def compute(self, z, y, *args, **kwargs) -> dict[str, Tensor]:
        """Computes the metric given predictions and targets. To be implemented by subclasses."""
        raise NotImplementedError("compute() must be implemented in subclasses")


class RMSE(Metric):
    """Root Mean Squared Error metric."""
    def __init__(self):
        super().__init__()

    @no_grad
    def compute(self, z, y):
        # mse = 1/N Σ (z - y)²
        mse = mean((z - y) ** 2, axis=-1)
        # rmse = √(mse)
        rmse = sqrt(mse)
        return {"RMSE": rmse}
    

class R2(Metric):
    """R2 Score metric."""
    def __init__(self, eps: float = 1e-7):
        """
        @param eps: Small value for numerical stability
        """
        super().__init__()
        self.eps = eps

    @no_grad
    def compute(self, z, y):
        # ss_total = Σ (y - μ_y)²
        ss_total = sum((y - mean(y, axis=-1, keepdims=True)) ** 2, axis=-1)
        # ss_residual = Σ (z - y)²
        ss_residual = sum((z - y) ** 2, axis=-1)
        # R² = 1 - (ss_residual / ss_total)
        r2 = 1 - (ss_residual / where(ss_total != 0, ss_total, self.eps))
        return {"R2 Score": r2}


class ClassificationMetrics(Metric):
    """Classification metrics: Accuracy, Precision, Recall, F1 Score, Confusion Matrix."""
    def __init__(self, num_classes: int = None, acc: bool = True, prec: bool = False, rec: bool = False, f1: bool = False, eps: float = 1e-7):
        """
        @param num_classes: Number of classes for classification tasks.
        @param acc: Whether to compute accuracy.
        @param prec: Whether to compute precision.
        @param rec: Whether to compute recall.
        @param f1: Whether to compute F1 score.
        @param eps: Small value for numerical stability
        """
        super().__init__()
        self.num_classes = num_classes
        self.acc = acc
        self.prec = prec
        self.rec = rec
        self.f1 = f1
        self.eps = eps

    @no_grad
    def compute(self, z, y):
        if self.num_classes is None:
            self.num_classes = y.shape[-1]
        # Convert logits to class indices and one-hot encode
        z_idx = argmax(z, axis=-1)
        z_onehot = one_hot(z_idx, self.num_classes)

        cm = y.transpose() @ z_onehot # Confusion matrix
        d_indices = array(range(self.num_classes)) # Diagonal elements
        TP = cm[d_indices, d_indices] # True Positives
        FP = sum(cm, axis=0) - TP # False Positives
        FN = sum(cm, axis=1) - TP # False Negatives

        metrics = {}
        if self.acc:
            # Accuracy = Σ TP / Σ total samples
            denominator = sum(cm, axis=None)
            metrics["Accuracy"] = sum(TP, axis=None) / where(denominator > 0, denominator, self.eps)
        def prec():
            # Precision = TP / (TP + FP)
            denominator = TP + FP
            return TP / where(denominator > 0, denominator, self.eps)
        if self.prec: metrics["Precision"] = prec()
        def rec():
            # Recall = TP / (TP + FN)
            denominator = TP + FN
            return TP / where(denominator > 0, denominator, self.eps)
        if self.rec: metrics["Recall"] = rec()
        if self.f1:
            # F1 = 2 * Precision * Recall / (Precision + Recall)
            p, r = prec(), rec()
            denominator = p + r
            metrics["F1 Score"] = 2 * p * r / where(denominator > 0, denominator, self.eps)
        return metrics


class Perplexity(Metric):
    """Perplexity metric for generative models."""
    def __init__(self, eps: float = 1e-7):
        """
        @param eps: Small value for numerical stability
        """
        super().__init__()
        self.eps = eps

    @no_grad
    def compute(self, z, y):
        # Perplexity = exp(-1/N Σ log(p(y|x)))
        z = clip(z, self.eps, 1 - self.eps)
        log_likelihood = -sum(y * log(z), axis=-1)
        perplexity = exp(mean(log_likelihood, axis=-1))
        return {"Perplexity": perplexity}