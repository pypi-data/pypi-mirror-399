# Pretty Little Summary

**Automatic structured summaries of Python objects - DataFrames, arrays, models, and more.**

Pretty Little Summary automatically generates clean, structured summaries of Python objects. It's perfect for Jupyter notebooks, data exploration, debugging, and understanding complex objects at a glance.

## Features

- 🎯 **Single function API**: Just call `pls.describe(obj)`
- 📊 **40+ type adapters**: pandas, numpy, matplotlib, sklearn, pytorch, polars, and more
- 📜 **History tracking**: Captures Jupyter notebook code context
- 🔌 **Extensible**: Register custom adapters for your types
- 🛡️ **Zero required dependencies**: Works with just Python stdlib
- ⚡ **Fast**: Deterministic summaries with no network calls

## Installation

```bash
pip install pretty-little-summary
```

## Quick Start

```python
import pretty_little_summary as pls
import pandas as pd

# Create a DataFrame
df = pd.DataFrame({
    'product': ['Widget', 'Gadget', 'Doohickey'],
    'price': [19.99, 29.99, 39.99],
    'quantity': [100, 50, 75]
})

# Get a structured summary
result = pls.describe(df)

print(result.content)
# Output: "pandas.DataFrame | Shape: (3, 3) | Columns: product, price, quantity"

print(result.meta)
# Output: {'object_type': 'pandas.DataFrame', 'shape': (3, 3),
#          'columns': ['product', 'price', 'quantity'], ...}
```

## Supported Types

Pretty Little Summary includes adapters for:

**Data Structures:**
- pandas (DataFrame, Series)
- polars (DataFrame, LazyFrame)
- numpy (ndarray)
- PyArrow (Table)
- xarray (Dataset, DataArray)

**Visualization:**
- matplotlib (Figure, Axes)
- altair (Chart)
- plotly (Figure)
- seaborn (Axes)
- bokeh (Figure)

**Machine Learning:**
- scikit-learn (models, pipelines)
- PyTorch (Tensor, Module)
- TensorFlow (Tensor, Model)
- JAX (Array)

**Other:**
- Built-in types (list, dict, set, etc.)
- datetime objects
- Pydantic models
- NetworkX graphs
- Regular expressions
- File handles
- And more!

## Usage Examples

### Basic Types

```python
import pretty_little_summary as pls

# Lists
result = pls.describe([1, 2, 3, 4, 5])
print(result.content)
# "list | Length: 5 | Type: int"

# Dictionaries
result = pls.describe({'name': 'Alice', 'age': 30})
print(result.content)
# "dict | Keys: 2 | Types: str -> int, str -> str"
```

### Data Science Objects

```python
import numpy as np
import pretty_little_summary as pls

# NumPy arrays
arr = np.random.rand(100, 50)
result = pls.describe(arr)
print(result.content)
# "numpy.ndarray | Shape: (100, 50) | dtype: float64"
```

### Jupyter Integration

In Jupyter notebooks, Pretty Little Summary automatically captures the code history:

```python
import pandas as pd
import pretty_little_summary as pls

df = pd.read_csv('data.csv')
df_clean = df.dropna()
df_filtered = df_clean[df_clean['value'] > 100]

result = pls.describe(df_filtered)
print(result.history)
# ['df = pd.read_csv(\'data.csv\')',
#  'df_clean = df.dropna()',
#  'df_filtered = df_clean[df_clean[\'value\'] > 100]']
```

## Optional Dependencies

Pretty Little Summary has **zero required dependencies**. It works out of the box with Python's standard library.

For specialized type support, install the corresponding library:

```bash
# Data science
pip install pretty-little-summary[pandas]
pip install pretty-little-summary[data]  # pandas + polars

# Visualization
pip install pretty-little-summary[viz]  # matplotlib + altair

# Machine learning
pip install pretty-little-summary[ml]  # scikit-learn + pytorch

# Everything
pip install pretty-little-summary[all]
```

## API Reference

### `describe(obj, name=None)`

Generate a structured summary of any Python object.

**Args:**
- `obj`: Any Python object to analyze
- `name` (optional): Variable name for history filtering (auto-detected in Jupyter)

**Returns:**
- `Description` object with:
  - `content` (str): Human-readable summary
  - `meta` (dict): Structured metadata
  - `history` (list[str] | None): Code history if in Jupyter

### `list_available_adapters()`

List all currently registered adapters.

**Returns:**
- list[str]: Names of available adapters

```python
import pretty_little_summary as pls

adapters = pls.list_available_adapters()
print(adapters)
# ['PrimitiveAdapter', 'CollectionsAdapter', 'PandasAdapter', ...]
```

## How It Works

1. **Type Detection**: Automatically selects the best adapter for your object type
2. **Metadata Extraction**: Gathers relevant information (shape, columns, dtypes, etc.)
3. **Summary Generation**: Creates a clean, structured summary
4. **History Capture**: In Jupyter, tracks how the object was created

## Custom Adapters

You can register custom adapters for your own types:

```python
from pretty_little_summary.adapters._base import AdapterRegistry
from pretty_little_summary.core import MetaDescription

class MyCustomAdapter:
    @staticmethod
    def can_handle(obj):
        return isinstance(obj, MyCustomType)

    @staticmethod
    def extract_metadata(obj):
        return {
            "object_type": "MyCustomType",
            "adapter_used": "MyCustomAdapter",
            "custom_field": obj.some_property,
        }

AdapterRegistry.register(MyCustomAdapter)
```

## Why Pretty Little Summary?

- **Debug faster**: Quickly understand what's in your variables
- **Document better**: Auto-generate object descriptions for notebooks
- **Share knowledge**: Help teammates understand complex data structures
- **Explore confidently**: Get instant insights into unfamiliar objects

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Links

- PyPI: https://pypi.org/project/pretty-little-summary/
- GitHub: https://github.com/yourusername/pretty-little-summary
