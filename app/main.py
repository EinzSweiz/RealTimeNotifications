from fastapi import FastAPI
from app.presentation.websocket.websocket_service import websocket_router
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from app.presentation.websocket.websocket_manager import ws_manager
from prometheus_fastapi_instrumentator import Instrumentator
import asyncio
from app.infastructure.kafka_producer import KafkaProducerService
import logging

kafka_producer = KafkaProducerService()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle event: Start and cleanup resources."""
    print("🚀 FastAPI Application is starting...")
    logger.info("🚀 FastAPI Application is starting...")

    task = asyncio.create_task(ws_manager.start_redis_listener())
    print("📡 Redis listener started!")
    logger.info("📡 Redis listener started!")
    print("🚀 Starting Kafka Producer...")
    await kafka_producer.start()

    yield  # Run the application

    print("🛑 FastAPI Application is shutting down...")
    logger.info("🛑 FastAPI Application is shutting down...")
    await kafka_producer.stop()
    
    # Cleanup task on shutdown
    task.cancel()

app = FastAPI(lifespan=lifespan)

# ✅ CORS Configuration (Adjust for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Register Routers
app.include_router(websocket_router)

Instrumentator().instrument(app).expose(app=app)