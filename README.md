python-ubi-config
==================

A Python library for reading UBI configurations
Usage Example
-------------
When there is `DEFAULT_UBI_REPO` set, user can load the config by passing the config file
name to `get_loader().load()`

```python
from ubi_config import get_loader

config = get_loader().load('rhel-8-for-x86_64-appstream')
# config has been validated and is now a Python object with relevant properties
package_whitelist = config.packages.whitelist
print package_whitelist
```
Or, get all config files from the repo:
```python

from ubi_config import get_loader

configs = get_loader().load_all()
# returns a list of UbiConfig objects
```
Or, user can also load the config from local file:
```python
from ubi_config import get_loader

config = get_loader(local=True).load('/path/to/rhel-8-for-x86_64-appstream.yaml')
```

License
-------
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

