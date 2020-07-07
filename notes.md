the idea for now is to bind mount the owner python packages to the container system python packages folder, and maybe thats enough for imports not to fail.

if not here is some usful info about packages and versions:

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