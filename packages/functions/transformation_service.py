import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from firebase_functions import https_fn, options
from transformation_engine_v2 import transform_raw_post
from data_contracts import Listing, Attribute

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use same global CORS config as other functions
CORS_CONFIG = options.CorsOptions(
    cors_origins=["*"],
    cors_methods=["get", "post"]
)

@https_fn.on_request(cors=CORS_CONFIG, memory=1024, timeout_sec=300)
def transform_property_post(req: https_fn.Request) -> https_fn.Response:
    """
    Transform raw Vietnamese rental property post into structured data
    
    Accepts POST requests with JSON body:
    {
        "raw_text": "string",
        "source": "string (optional)",
        "metadata": "object (optional)"
    }
    
    Returns structured listing data or error details
    """
    start_time = datetime.utcnow()
    
    try:
        # Only accept POST requests
        if req.method != "POST":
            return https_fn.Response(
                json.dumps({"error": "Method not allowed"}),
                status=405,
                headers={"Content-Type": "application/json"}
            )
        
        # Parse request body
        try:
            request_data = req.get_json(force=True)
        except Exception:
            return https_fn.Response(
                json.dumps({"error": "Invalid JSON in request body"}),
                status=400,
                headers={"Content-Type": "application/json"}
            )
        
        # Validate required fields
        raw_text = request_data.get("raw_text")
        if not raw_text or len(raw_text.strip()) < 10:
            return https_fn.Response(
                json.dumps({"error": "Raw text must contain at least 10 characters"}),
                status=400,
                headers={"Content-Type": "application/json"}
            )
        
        source = request_data.get("source")
        metadata = request_data.get("metadata", {})
        
        logger.info(f"Processing transformation request for {len(raw_text)} characters of text")
        
        # Call transformation engine
        source_url = metadata.get('source_url', 'api-request') if metadata else 'api-request'
        result = transform_raw_post(raw_text, source_url)
        
        if not result:
            return https_fn.Response(
                json.dumps({"error": "Transformation failed - no result returned"}),
                status=500,
                headers={"Content-Type": "application/json"}
            )
        
        # Calculate processing time
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        logger.info(f"Transformation completed successfully in {processing_time:.2f}ms")
        
        response_data = {
            "success": True,
            "data": {
                "listing": result.model_dump() if hasattr(result, 'model_dump') else result,
                "status": "pending_review",
                "source": source,
                "metadata": metadata
            },
            "processing_time_ms": processing_time
        }
        
        return https_fn.Response(
            json.dumps(response_data),
            status=200,
            headers={"Content-Type": "application/json"}
        )
        
    except Exception as e:
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        error_msg = f"Transformation failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        error_response = {
            "success": False,
            "error": error_msg,
            "processing_time_ms": processing_time
        }
        
        return https_fn.Response(
            json.dumps(error_response),
            status=500,
            headers={"Content-Type": "application/json"}
        )

@https_fn.on_request(cors=CORS_CONFIG)
def health_check(req: https_fn.Request) -> https_fn.Response:
    """Health check endpoint for monitoring"""
    health_data = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "property-transformation-service"
    }
    
    return https_fn.Response(
        json.dumps(health_data),
        status=200,
        headers={"Content-Type": "application/json"}
    )
