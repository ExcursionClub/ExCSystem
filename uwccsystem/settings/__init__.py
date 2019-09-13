import os

env_config = os.environ.get("ENV_CONFIG")
print(env_config)

if env_config == "development":
    from .development import *
elif env_config == "test":
    from .ci import *
elif env_config == "staging":
    from .staging import *
else:
    from .production import *
