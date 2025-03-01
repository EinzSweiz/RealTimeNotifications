import asyncio
import logging
from redis.asyncio import Redis
from redis.asyncio.cluster import RedisCluster

logger = logging.getLogger(__name__)


class RedisRepository:

    def __init__(self):
        self.redis_cluster = None
        self.redis_pubsub = None

    async def connect_cluster(self):
        if self.redis_cluster:
            return self.redis_cluster
        try:
            self.redis_cluster = RedisCluster(
                startup_nodes=[
                    {"host": "redis-node-0", "port": 7000},
                    {"host": "redis-node-1", "port": 7001},
                    {"host": "redis-node-2", "port": 7002}
                ],
                decode_responses=True
            )
            await self.redis_cluster.initialize()
            logger.info("✅ Connected to Redis Cluster")
            print("✅ Connected to Redis Cluster")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Redis Cluster: {e}")
            print(f"❌ Failed to connect to Redis Cluster: {e}")

    async def connect_pubsub(self):
        if self.redis_pubsub:
            return self.redis_pubsub
        try:
            self.redis_pubsub = Redis(
                host="redis-node-0", port=7000, decode_responses=True
            )
            await self.redis_pubsub.ping()
            logger.info("✅ Connected to Redis (Single Node) for Pub/Sub")
            print("✅ Connected to Redis (Single Node) for Pub/Sub")

        except Exception as e:
            logger.error(f"❌ Failed to connect to Redis for Pub/Sub: {e}")
            print(f"❌ Failed to connect to Redis for Pub/Sub: {e}")
    async def get_redis_cluster(self):
        if not self.redis_cluster:
            await self.connect_cluster()
        return self.redis_cluster
    
    async def get_redis_pubsub(self):
        if not self.redis_pubsub:
            await self.connect_pubsub()
        return self.redis_pubsub
    async def set_cache(self, key: str, value: str, timeout: int  = 3000):
        redis = await self.get_redis_cluster()
        await redis.set(key, value, ex=timeout)
    
    async def get_cache(self, key: str):
        redis = await self.get_redis_cluster()
        return await redis.get(key)

    async def close(self):
        if self.redis_cluster:
            await self.redis_cluster.close()
            logger.info("🔌 Redis Cluster connection closed.")
        
        if self.redis_pubsub:
            await self.redis_pubsub.close()
            logger.info("🔌 Redis Pub/Sub connection closed.")

redis_repository = RedisRepository()