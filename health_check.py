import logging
import os

logger = logging.getLogger(__name__)

# Health check endpoint (optional, helps prevent sleep on Render)
def get_health_check_app():
    try:
        from flask import Flask
        app = Flask(__name__)
        
        @app.route('/health', methods=['GET'])
        def health():
            return {'status': 'ok'}, 200
        
        return app
    except ImportError:
        logger.warning("Flask not installed, health check disabled")
        return None
