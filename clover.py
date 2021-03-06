
from flask_cors import CORS
from flask_script import Manager

from clover import app


CORS(app, supports_credentials=True)

manager = Manager(app)

if __name__ == '__main__':
    manager.run()
