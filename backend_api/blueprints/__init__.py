# blueprints/__init__.py

# Import the blueprint definitions
from .convo_bp import convo_bp
from .prompt_generation import mistral_bp

# Import all route modules to register them with their blueprints
# This ensures that when the blueprints are imported, all routes are registered

# Import your conversation routes
from . import fetch_history
from . import fetch_full_convo
from . import update_history
from . import prompt_generation # your existing route file
# Import any other route files you have for convo_bp

# Import your mistral routes (if they're in separate files)
# from . import your_mistral_route_files

# Make blueprints available when importing from this package
__all__ = ['convo_bp', 'mistral_bp']