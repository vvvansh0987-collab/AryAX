"""Elasticsearch integration for audit logging and analytics"""

from elasticsearch import Elasticsearch
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime

from src.config import settings

logger = logging.getLogger(__name__)

es_client: Optional[Elasticsearch] = None


async def init_elasticsearch():
    """Initialize Elasticsearch connection"""
    global es_client
    try:
        es_client = Elasticsearch(settings.elasticsearch_hosts)
        # Test connection
        info = es_client.info()
        logger.info(f"Elasticsearch connected: {info['version']['number']}")
    except Exception as e:
        logger.error(f"Failed to connect to Elasticsearch: {e}")
        raise


async def close_elasticsearch():
    """Close Elasticsearch connection"""
    global es_client
    if es_client:
        es_client.close()
        logger.info("Elasticsearch connection closed")


def get_elasticsearch() -> Elasticsearch:
    """Get Elasticsearch client"""
    if not es_client:
        raise RuntimeError("Elasticsearch not initialized")
    return es_client


async def index_audit_log(
    org_id: str,
    user_id: str,
    event_type: str,
    resource: str,
    action: str,
    result: str,
    ip_address: str,
    user_agent: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> bool:
    """Index audit log event"""
    try:
        es = get_elasticsearch()
        index_name = f"{settings.elasticsearch_index_prefix}-audit-logs-{datetime.now().strftime('%Y.%m.%d')}"
        
        doc = {
            "org_id": org_id,
            "user_id": user_id,
            "event_type": event_type,
            "resource": resource,
            "action": action,
            "result": result,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        es.index(index=index_name, document=doc)
        return True
    except Exception as e:
        logger.error(f"Failed to index audit log: {e}")
        return False


async def search_audit_logs(
    org_id: str,
    event_type: Optional[str] = None,
    user_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """Search audit logs"""
    try:
        es = get_elasticsearch()
        
        query: Dict[str, Any] = {
            "bool": {
                "must": [
                    {"term": {"org_id": org_id}}
                ]
            }
        }
        
        if event_type:
            query["bool"]["must"].append({"term": {"event_type": event_type}})
        
        if user_id:
            query["bool"]["must"].append({"term": {"user_id": user_id}})
        
        if start_date or end_date:
            range_query = {}
            if start_date:
                range_query["gte"] = start_date
            if end_date:
                range_query["lte"] = end_date
            query["bool"]["must"].append({"range": {"timestamp": range_query}})
        
        results = es.search(
            index=f"{settings.elasticsearch_index_prefix}-audit-logs-*",
            query=query,
            size=limit,
            sort=[{"timestamp": {"order": "desc"}}],
        )
        
        return [hit["_source"] for hit in results["hits"]["hits"]]
    except Exception as e:
        logger.error(f"Failed to search audit logs: {e}")
        return []


async def index_analytics(
    org_id: str,
    metric_type: str,
    metric_name: str,
    value: float,
    tags: Optional[Dict[str, str]] = None,
) -> bool:
    """Index analytics metric"""
    try:
        es = get_elasticsearch()
        index_name = f"{settings.elasticsearch_index_prefix}-analytics-{datetime.now().strftime('%Y.%m.%d')}"
        
        doc = {
            "org_id": org_id,
            "metric_type": metric_type,
            "metric_name": metric_name,
            "value": value,
            "tags": tags or {},
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        es.index(index=index_name, document=doc)
        return True
    except Exception as e:
        logger.error(f"Failed to index analytics: {e}")
        return False


async def get_analytics_summary(
    org_id: str,
    metric_type: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Dict[str, Any]:
    """Get analytics summary"""
    try:
        es = get_elasticsearch()
        
        query: Dict[str, Any] = {
            "bool": {
                "must": [
                    {"term": {"org_id": org_id}},
                    {"term": {"metric_type": metric_type}},
                ]
            }
        }
        
        if start_date or end_date:
            range_query = {}
            if start_date:
                range_query["gte"] = start_date
            if end_date:
                range_query["lte"] = end_date
            query["bool"]["must"].append({"range": {"timestamp": range_query}})
        
        results = es.search(
            index=f"{settings.elasticsearch_index_prefix}-analytics-*",
            query=query,
            aggs={
                "stats": {
                    "stats": {"field": "value"}
                }
            },
            size=0,
        )
        
        stats = results["aggregations"]["stats"]
        return {
            "count": stats["count"],
            "min": stats["min"],
            "max": stats["max"],
            "avg": stats["avg"],
            "sum": stats["sum"],
        }
    except Exception as e:
        logger.error(f"Failed to get analytics summary: {e}")
        return {}
