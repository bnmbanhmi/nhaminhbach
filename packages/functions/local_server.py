"""
Local Development Server for nhaminhbach Backend
Wraps Firebase Functions for local testing
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS

# Set environment to development
os.environ['ENVIRONMENT'] = 'development'

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def home():
    return jsonify({
        "message": "nhaminhbach Backend API - Local Demo",
        "status": "running",
        "endpoints": {
            "GET /": "This help message",
            "GET /api/listings": "Get all listings",
            "POST /api/scrape": "Trigger scraping (requires authentication)",
            "POST /api/transform": "Trigger transformation (requires authentication)"
        }
    })

@app.route('/api/listings', methods=['GET'])
def get_listings():
    """
    Mock endpoint for getting listings
    In production, this would connect to Cloud SQL
    """
    return jsonify({
        "listings": [
            {
                "id": 1,
                "title": "Nhà 3 tầng đẹp tại Quận 1",
                "price": 15000000000,
                "area": 80,
                "district": "Quận 1",
                "status": "available"
            },
            {
                "id": 2,
                "title": "Căn hộ chung cư 2PN",
                "price": 3500000000,
                "area": 65,
                "district": "Quận 3",
                "status": "available"
            },
            {
                "id": 3,
                "title": "Biệt thự mini Quận 7",
                "price": 25000000000,
                "area": 150,
                "district": "Quận 7",
                "status": "sold"
            }
        ],
        "total": 3,
        "demo_mode": True
    })

@app.route('/api/scrape', methods=['POST'])
def trigger_scrape():
    """
    Mock endpoint for triggering scraping
    """
    return jsonify({
        "message": "Scraping triggered (demo mode)",
        "status": "queued",
        "job_id": "demo-123456"
    })

@app.route('/api/transform', methods=['POST'])
def trigger_transform():
    """
    Mock endpoint for triggering transformation
    """
    return jsonify({
        "message": "Transformation triggered (demo mode)",
        "status": "processing",
        "job_id": "demo-789012"
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": os.popen('date').read().strip()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"\n{'='*60}")
    print(f"🚀 nhaminhbach Backend - Local Demo Server")
    print(f"{'='*60}")
    print(f"📍 Server running at: http://localhost:{port}")
    print(f"📋 API Documentation: http://localhost:{port}/")
    print(f"🏥 Health Check: http://localhost:{port}/health")
    print(f"{'='*60}\n")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True
    )
