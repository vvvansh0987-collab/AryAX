#!/usr/bin/env python
"""Development server runner with automatic database initialization"""

import asyncio
import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.database import init_db, close_db
from src.cache import init_redis, close_redis
from src.search import init_elasticsearch, close_elasticsearch

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def initialize_services():
    """Initialize all services"""
    logger.info("Initializing services...")
    try:
        await init_db()
        logger.info("✓ Database initialized")
    except Exception as e:
        logger.error(f"✗ Database initialization failed: {e}")
        raise
    
    try:
        await init_redis()
        logger.info("✓ Redis initialized")
    except Exception as e:
        logger.warning(f"⚠ Redis initialization failed (optional): {e}")
    
    try:
        await init_elasticsearch()
        logger.info("✓ Elasticsearch initialized")
    except Exception as e:
        logger.warning(f"⚠ Elasticsearch initialization failed (optional): {e}")


async def cleanup_services():
    """Cleanup all services"""
    logger.info("Cleaning up services...")
    try:
        await close_db()
        logger.info("✓ Database closed")
    except Exception as e:
        logger.error(f"✗ Database cleanup failed: {e}")
    
    try:
        await close_redis()
        logger.info("✓ Redis closed")
    except Exception as e:
        logger.warning(f"⚠ Redis cleanup failed: {e}")
    
    try:
        await close_elasticsearch()
        logger.info("✓ Elasticsearch closed")
    except Exception as e:
        logger.warning(f"⚠ Elasticsearch cleanup failed: {e}")


async def main():
    """Main entry point"""
    try:
        await initialize_services()
        logger.info("All services initialized successfully!")
        logger.info("Starting development server...")
        logger.info("Visit http://localhost:8000/docs for API documentation")
        
        # Import and run uvicorn
        import uvicorn
        config = uvicorn.Config(
            "src.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
        )
        server = uvicorn.Server(config)
        await server.serve()
    except KeyboardInterrupt:
        logger.info("Shutdown requested")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        await cleanup_services()


if __name__ == "__main__":
    asyncio.run(main())
