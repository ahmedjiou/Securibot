# Application entry point
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)

# Configure CORS with specific settings
CORS(app, 
     origins=["http://localhost:9002"],  # Your frontend URL
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# Import and register blueprints
try:
    from blueprints.prompt_generation import mistral_bp
    from blueprints.convo_bp import convo_bp
    
    app.register_blueprint(mistral_bp)
    app.register_blueprint(convo_bp)
    
    print("Blueprints registered successfully!")
    
    # Debug: Print all registered routes
    print("Registered routes:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.rule} -> {rule.methods}")
        
except Exception as e:
    print(f"Error registering blueprints: {e}")

# Add a simple test route to verify the app is working
@app.route('/test', methods=['GET', 'OPTIONS'])
def test_route():
    return jsonify({"message": "Flask app is working!"}), 200

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)