import os

print(os.environ.get("ENV_CONFIG"))
if os.environ.get("ENV_CONFIG") == "development":
    from .development import *
else:
    from .production import *
