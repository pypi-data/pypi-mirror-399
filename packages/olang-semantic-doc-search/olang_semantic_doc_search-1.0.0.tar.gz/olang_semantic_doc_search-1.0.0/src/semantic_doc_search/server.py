# src/semantic_doc_search/server.py
import os
import sys
import logging
from flask import Flask, request, jsonify
from .core import SemanticDocSearch

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max payload
    
    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({
            "status": "healthy",
            "resolver_name": "semantic-doc-search",
            "version": "1.0.0",
            "capabilities": ["vector.search", "vector.insert"],
            "embedding_dimensions": 384,
            "ready": True
        })

    @app.route('/resolve', methods=['POST'])
    def resolve():
        try:
            if not request.is_json:
                return jsonify({"error": {"message": "Content-Type must be application/json"}}), 400
            
            data = request.get_json()
            if not data:  # ✅ FIXED: Added 'data' after 'not'
                return jsonify({"error": {"message": "Invalid JSON payload"}}), 400
            
            action = data.get('action')
            context = data.get('context', {})
            
            if not action:
                return jsonify({"error": {"message": "Missing 'action' field"}}), 400
            
            resolver = SemanticDocSearch(context)
            result = resolver.handle_action(action)
            
            return jsonify({
                "result": result,
                "request_id": data.get('request_id', ''),
                "resolver_name": "semantic-doc-search"
            })
            
        except Exception as e:
            error_msg = f"Resolver execution error: {str(e)}"
            logger.error(error_msg)
            
            return jsonify({
                "error": {"message": error_msg},
                "request_id": data.get('request_id', '') if 'data' in locals() else ''
            }), 500
    
    return app

def main():
    """Entry point for command-line usage."""
    app = create_app()
    host = os.getenv('RESOLVER_HOST', '0.0.0.0')
    port = int(os.getenv('RESOLVER_PORT', 8080))
    
    print(f"🚀 Starting semantic-doc-search resolver on {host}:{port}")
    print(f"   Health check: GET http://{host}:{port}/health")
    print(f"   Resolve endpoint: POST http://{host}:{port}/resolve")
    
    app.run(host=host, port=port, debug=False, threaded=True)

if __name__ == '__main__':
    main()