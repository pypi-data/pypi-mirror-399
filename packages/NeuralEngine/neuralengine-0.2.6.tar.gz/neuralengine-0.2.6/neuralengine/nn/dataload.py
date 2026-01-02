import neuralengine.config as cf
from ..tensor import Tensor


class DataLoader:
    """Data loader for batching and shuffling data."""
    def __init__(self, x, y, dtype=None, batch_size: int = 32, shuffle: bool = True, seed: int = None):
        """
        @param dataset: Dataset to load (list, array, etc.).
        @param dtype: Data type for the dataset.
        @param batch_size: Number of samples per batch.
        @param shuffle: Whether to shuffle the data at the start of each epoch.
        @param seed: Seed for random number generator to ensure reproducibility.
        """
        self.x = Tensor(x, dtype=dtype)
        self.y = Tensor(y, dtype=dtype)
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.num_samples = self.x.shape[0]
        self.num_batches = (self.num_samples + batch_size - 1) // batch_size
        self.indices = cf.nu.arange(self.num_samples)
        self.rng = cf.nu.random.RandomState(seed)

    def __len__(self) -> int:
        """Returns the number of batches."""
        return self.num_batches
    
    def __getitem__(self, index: int | slice) -> tuple[Tensor, Tensor]:
        """Gets a batch of data by index. Override for custom behavior."""
        return self.x[index], self.y[index]

    def __iter__(self) -> 'DataLoader':
        """Returns an iterator over the batches."""
        self.current_batch = 0
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