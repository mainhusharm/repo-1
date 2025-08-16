from journal import create_app, socketio
from flask import jsonify

app = create_app()

@app.route('/health')
def health_check():
    """Health check endpoint for service monitoring."""
    return jsonify({'status': 'healthy', 'service': 'journal_service'}), 200

if __name__ == '__main__':
    try:
        print("Starting Journal Service on port 5000...")
        socketio.run(app, debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"Failed to start Journal Service: {e}")
        raise
