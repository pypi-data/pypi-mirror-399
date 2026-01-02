# llamaindex-primordia

Track LlamaIndex costs.

```bash
pip install llamaindex-primordia
```

```python
from llamaindex_primordia import PrimordiaCallback
from llama_index.core import Settings

Settings.callback_manager.add_handler(PrimordiaCallback("my-agent"))
```
