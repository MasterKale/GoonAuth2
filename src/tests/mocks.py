from mockredis import mock_strict_redis_client

redis_db = mock_strict_redis_client(
    host='0.0.0.0',
    port=6379,
    db=0,
    decode_responses=True,
)
