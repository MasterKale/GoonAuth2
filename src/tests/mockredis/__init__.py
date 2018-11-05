#############
# mock-redis-py v2.9.3
#
# Manually patched with https://github.com/locationlabs/mockredis/pull/124 because otherwise we
# have to fight with bytestrings during testing
#############

from mockredis.client import MockRedis, mock_redis_client, mock_strict_redis_client

__all__ = ["MockRedis", "mock_redis_client", "mock_strict_redis_client"]
