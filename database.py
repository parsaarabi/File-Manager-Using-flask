from flask import *
from flask_sqlalchemy import *
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
app = Flask(__name__)

# limiter = Limiter(get_remote_address, app=app, strategy="fixed-window")
# limiter = Limiter(get_remote_address, app=app, default_limits=["200 per day", "50 per hour"])
limiter = Limiter(app=app, key_func=get_remote_address, strategy="fixed-window")


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

db = SQLAlchemy(app)

app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text)
    email = db.Column(db.Text)
    password = db.Column(db.Text)
    email_status = db.Column(db.Boolean, default=False, nullable=False)
    email_code_expiration = db.Column(db.Text)
    email_code = db.Column(db.Text)
    def __repr__(self):
        return f'user({self.id}-{self.username}-{self.email}-{self.password}-{self.email_status}-{self.email_code_expiration}-{self.email_code})'

class Files(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.Text)
    name = db.Column(db.Text)
    type = db.Column(db.Text)
    format_ = db.Column(db.Text)
    for_user = db.Column(db.Text)
    for_folder = db.Column(db.Text)
    delete_files_in = db.Column(db.Text)
    time = db.Column(db.Text)
    def __repr__(self):
        return f'files({self.id}-{self.url}-{self.name}-{self.format_}-{self.type}-{self.for_user}-{self.for_folder}-{self.time}-{self.delete_files_in})'

# class Folders(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     for_user = db.Column(db.Text)
#     name = db.Column(db.Text)
#     for_folder = db.Column(db.Text)
#     def __repr__(self):
#         return f'folders({self.id}-{self.for_user}-{self.name}-{self.for_folder})'
