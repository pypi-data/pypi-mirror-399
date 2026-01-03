import neuralengine.config as cf
from ..tensor import Tensor


class DataLoader:
    """Data loader class for batching and shuffling data."""
    def __init__(self, x, y, dtype=None, batch_size: int = 32, shuffle: bool = True, seed: int = None, bar: int = 30):
        """
        @param x: Input data (array-like).
        @param y: Target data (array-like).
        @param dtype: Data type for the dataset.
        @param batch_size: Number of samples per batch.
        @param shuffle: Whether to shuffle the data at the start of each epoch.
        @param seed: Seed for random number generator to ensure reproducibility.
        @param bar: Length of the progress bar.
        """
        self.x = Tensor(x, dtype=dtype)
        self.y = Tensor(y, dtype=dtype)
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.current_batch = 0
        self.num_samples = self.x.shape[0]
        self.num_batches = (self.num_samples + batch_size - 1) // batch_size
        self.indices = cf.nu.arange(self.num_samples) # Indices for shuffling
        self.rng = cf.nu.random.RandomState(seed) # Random number generator
        self.bar = bar

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
        filled = int(self.bar * self.current_batch // self.num_batches) # Filled length of the bar
        progress = '█' * filled + '-' * (self.bar - filled) # Progress bar string
        return f"\r|{progress}| {percent:.0f}%"