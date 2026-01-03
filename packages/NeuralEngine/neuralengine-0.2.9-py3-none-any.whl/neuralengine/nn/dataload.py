import neuralengine.config as cf
from ..tensor import Tensor
from ..utils import tensor


class DataLoader:
    """Data loader class for batching and shuffling data."""
    def __init__(self, x, y, dtype: tuple[type, type] = (cf.DType.FLOAT32, None), batch_size: int = 32, 
                shuffle: bool = True, random_seed: int = None, bar_size: int = 30):
        """
        @param x: Input data (array-like).
        @param y: Target data (array-like).
        @param dtype: Data types for the dataset.
        @param batch_size: Number of samples per batch.
        @param shuffle: Whether to shuffle the data at the start of each epoch.
        @param random_seed: Seed for random number generator to ensure reproducibility.
        @param bar_size: Length of the progress bar.
        """
        dtype = dtype if isinstance(dtype, (tuple, list)) else (dtype,)
        if any(not isinstance(dt, (type, type(None))) for dt in dtype):
            raise ValueError("dtype must be a type or None")
        
        self.x = tensor(x, dtype=dtype[0])
        self.y = tensor(y, dtype=dtype[-1])
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.current_batch = 0
        self.num_samples = self.x.shape[0]
        self.num_batches = (self.num_samples + batch_size - 1) // batch_size
        self.indices = cf.nu.arange(self.num_samples) # Indices for shuffling
        self.rng = cf.nu.random.RandomState(random_seed) # Random number generator
        self.bar_size = bar_size

    def __len__(self) -> int:
        """Returns the number of batches."""
        return self.num_batches
    
    def __getitem__(self, index: int | slice) -> tuple[Tensor, Tensor]:
        """Gets a batch of data by index. Override for custom behavior."""
        return self.x[index], self.y[index]

    def __iter__(self) -> 'DataLoader':
        """Returns an iterator over the batches."""
        self.current_batch = 0 # Reset batch counter
        if self.shuffle:
            self.rng.shuffle(self.indices)
        return self

    def __next__(self) -> tuple[Tensor, Tensor]:
        """Returns the next batch of data."""
        if self.current_batch < self.num_batches:
            start_idx = self.current_batch * self.batch_size
            end_idx = min(start_idx + self.batch_size, self.num_samples)
            batch_indices = self.indices[start_idx:end_idx]
            batch_data = self[batch_indices]
            self.current_batch += 1
            return batch_data
        else:
            raise StopIteration
        
    def __repr__(self) -> str:
        """String representation showing progress bar."""
        percent = (self.current_batch / self.num_batches) * 100
        filled = int(self.bar_size * self.current_batch // self.num_batches) # Filled length of the bar
        progress = '█' * filled + '-' * (self.bar_size - filled) # Progress bar string
        return f"\r|{progress}| {percent:.0f}%"