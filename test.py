import redis

# Replace these variables with your Redis endpoint, port, username, and password
redis_endpoint = "redis-12591.c322.us-east-1-2.ec2.cloud.redislabs.com"
redis_port = 12591
redis_username = "default"
redis_password = "10zJ88wy76QuGvxNCxM3cQDhgiTclOHT"

try:
    # Connect to Redis with authentication
    r = redis.StrictRedis(
        host=redis_endpoint,
        port=redis_port,
        username=redis_username,
        password=redis_password,
        decode_responses=True
    )

    # Test connection by setting and getting a key
    r.set("test_key", "test_value")
    print("Value for test_key:", r.get("test_key"))

    # If connection is successful, no errors will be raised
    print("Connection to Redis successful")
except Exception as e:
    print("Error connecting to Redis:", e)
