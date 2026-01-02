import sys

from uv_build import *

message = """
heise plz don't typosquat your own readers.

if you're here from the article, the command you're looking for is:

```
uv add pydantic fastapi
```

thx bye
"""

def build_wheel(*args, **kwargs):
    print(message)
    sys.exit(1)