import os

env_config = os.environ.get("ENV_CONFIG")
print(env_config)

if env_config == "development":
    from .development import *
elif env_config == "test":
    from .ci import *
else:
    from .production import *
