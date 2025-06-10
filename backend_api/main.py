#Application entry point so that we can run it 
# We have to add the blueprints to the app
from flask import Flask
app = Flask(__name__)   # __name__ is the name of the current module    


from blueprints.prompt_generation import mistral_bp
from blueprints.convo_bp import convo_bp



app.register_blueprint(mistral_bp)
app.register_blueprint(convo_bp)




if __name__ == '__main__':
    app.run(debug=True)