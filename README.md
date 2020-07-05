The idea is beign able to run  `pytest-vnet mytest.py` and have this wrapper load the test to a docker container with mininet, run pytest on it and return its output.

mininet image:

see netvm folder

get installed python packages & locations

```python
from pip._internal.utils.misc import get_installed_distributions
p = get_installed_distributions()
```
get installed python version

```python
import sys
sys.version_info
```

