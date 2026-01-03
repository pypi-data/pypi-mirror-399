import os
import pickle as pkl
import neuralengine.config as cf
from ..tensor import Tensor, NoGrad
from ..utils import concat
from .layers import Layer, Mode, Flatten, LSTM
from .optim import Optimizer
from .loss import Loss
from .dataload import DataLoader


class Model:
    """A class to build and train a neural network model.
    Allows for defining the model architecture, optimizer, loss function, and metrics.
    The model can be trained and evaluated.
    """
    def __init__(self, input_size: tuple | int, optimizer: Optimizer = None, loss: Loss = None, metrics=()):
        """
        @param input_size: Tuple or int, shape of input data samples (int if 1D).
        @param optimizer: Optimizer instance.
        @param loss: Loss instance.
        @param metrics: List/tuple of Metric or Loss instances.
        """
        self.input_size = input_size

        if not isinstance(optimizer, Optimizer):
            raise ValueError("optimizer must be an instance of Optimizer class")
        self.optimizer = optimizer

        if not isinstance(loss, Loss):
            raise ValueError("loss must be an instance of Loss class")
        self.loss = loss

        self.metrics = metrics if isinstance(metrics, (list, tuple)) else (metrics,)


    def __call__(self, *layers: Layer) -> None:
        """Allows the model to be called with layers to build the model.
        @param layers: Variable number of Layer instances to add to the model.
        """
        self.build(*layers)


    def build(self, *layers: Layer) -> None:
        """Builds the model by adding layers.
        @param layers: Variable number of Layer instances to add to the model.
        """
        self.parameters, prevLayer = {}, None
        for i, layer in enumerate(layers):

            if not isinstance(layer, Layer):
                raise ValueError("All layers must be instances of Layer class")
            
            # If stacking LSTM layers, update input size and output selection
            if isinstance(layer, LSTM) and isinstance(prevLayer, LSTM):
                out_size = prevLayer.out_size
                if prevLayer.attention:
                    if prevLayer.enc_size: out_size += prevLayer.enc_size
                    else: out_size += prevLayer.out_size
                if prevLayer.bidirectional: out_size *= 2
                self.input_size = (*prevLayer.in_size[:-1], out_size)
                prevLayer.return_seq = True
                if not 0 in prevLayer.use_output:
                    if prevLayer.return_state: prevLayer.use_output = (0, 1, 2)
                    else: prevLayer.use_output = (0,)
            prevLayer = layer

            if layer.in_size is None:
                layer.in_size = self.input_size
            self.input_size = layer.out_size if hasattr(layer, 'out_size') else self.input_size
            if isinstance(layer, Flatten):
                self.input_size = int(cf.np.prod(self.input_size))

            self.parameters[f"layer_{i}"] = layer.parameters() # Collect parameters from the layer
            
        self.layers = layers
        self.optimizer.parameters = [p for params in self.parameters.values() for p in params]


    @classmethod
    def load_model(cls, filepath: str) -> 'Model':
        """Loads the model from a file.
        @param filepath: Path to the file from which the model will be loaded.
        @return: Loaded Model instance.
        """
        filepath = filepath if filepath.endswith('.pkl') else filepath + '.pkl'
        with open(filepath, 'rb') as file:
            model = pkl.load(file)

        if not isinstance(model, cls):
            raise ValueError("Loaded object is not a Model instance")

        device = cf.get_device()
        for layer in model.layers:
            layer.to(device)
        return model


    def load_params(self, filepath: str) -> None:
        """Loads the model parameters from a file.
        @param filepath: Path to the file from which model parameters will be loaded.
        """
        filepath = filepath if filepath.endswith('.pkl') else filepath + '.pkl'
        with open(filepath, 'rb') as file:
            params = pkl.load(file)

        device = cf.get_device()
        for i in range(len(self.layers)):
            layer_old = self.parameters.get(f"layer_{i}", [])
            layer_new = params.get(f"layer_{i}", [])

            if len(layer_old) != len(layer_new): 
                print(f"Skipping layer_{i} parameter load due to mismatch.")
                continue

            for p_old, p_new in zip(layer_old, layer_new):
                if p_old.shape != p_new.shape:
                    print(f"Skipping parameter load due to mismatch: {p_old.shape} vs {p_new.shape}")
                    continue 
                p_old.data = p_new.to(device).data.copy() # Load parameter weights


    def save(self, filename: str, weights_only: bool = False) -> None:
        """Saves the model or model parameters to a file.
        @param filename: Name of the file where model will be saved.
        @param weights_only: If True, saves only weights; else saves entire model structure.
        """
        filename = filename if filename.endswith('.pkl') else filename + '.pkl'
        filepath = os.path.join(os.getcwd(), filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True) # Ensure directory exists

        with open(filepath, 'wb') as file:
            if weights_only: pkl.dump(self.parameters, file)
            else: pkl.dump(self, file)


    def train(self, dataloader: DataLoader, epochs: int = 10, ckpt_interval: int = None) -> None:
        """Trains the model on data.
        @param dataloader: DataLoader instance providing training data.
        @param epochs: Number of epochs to train
        @param ckpt_interval: Interval (in epochs) to save checkpoints
        """
        if not isinstance(dataloader, DataLoader):
            raise ValueError("dataloader must be an instance of DataLoader class")

        for layer in self.layers:
            layer.mode = Mode.TRAIN

        for i in range(epochs):

            for batch in dataloader:
                x, y = batch

                # Forward pass
                for layer in self.layers:
                    x = layer(x)
                    # For stacked LSTM, pass outputs accordingly
                    if isinstance(layer, LSTM): x = x[layer.use_output[0]]
                    
                loss = self.loss(x, y) # Compute loss
                loss.backward() # Backward pass

                # Compute metrics
                for metric in self.metrics:
                    metric(x, y)

                # Update parameters
                self.optimizer.step()
                self.optimizer.reset_grad() # Reset gradients

                print(dataloader, f'Epoch {i + 1}/{epochs}', sep=', ', end='', flush=True) # Show progress bar

            output_strs = [f": (Loss) {self.loss}", *self.metrics]

            # Save checkpoint
            if ckpt_interval and (i + 1) % ckpt_interval == 0:
                self.save(f"checkpoints/model_epoch_{i + 1}.pkl", weights_only=True)
                output_strs.append("Checkpoint saved")
            print(*output_strs, sep=', ', flush=True) # Print epoch summary

            # Reset loss and metrics for next epoch
            self.loss.reset()
            for metric in self.metrics: metric.reset()


    def eval(self, dataloader: DataLoader) -> Tensor:
        """Evaluates the model on data.
        @param dataloader: DataLoader instance providing evaluation data.
        @return: Output tensor after evaluation
        """
        if not isinstance(dataloader, DataLoader):
            raise ValueError("dataloader must be an instance of DataLoader class")

        for layer in self.layers:
            layer.mode = Mode.EVAL

        z = []
        for batch in dataloader:
            x, y = batch

            # Forward pass
            with NoGrad():
                for layer in self.layers:
                    x = layer(x)
                    # For stacked LSTM, pass outputs accordingly
                    if isinstance(layer, LSTM): x = x[layer.use_output[0]]

                z.append(x) # Accumulate outputs
                self.loss(x, y) # Compute loss

            # Compute metrics
            for metric in self.metrics:
                metric(x, y)

            print(dataloader, 'Evaluation', sep=', ', end='', flush=True) # Show progress bar

        print(f": (Loss) {self.loss}", *self.metrics, sep=', ', flush=True) # Print evaluation summary
        return concat(*z, axis=0)