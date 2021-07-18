import os

class Config:
    SECRET_KEY = 'e333d26c49ed1559e65e98354fd55e88'
    #SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    #SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:H1344@post@localhost/CJNO'
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:password@localhost/kanapka'

    GOOGLEMAPS_KEY = 'AIzaSyBme2g3oyAqgYskmcxJxts70PAdaB2qFcg'
    ACCESS_CODE = 'b4a767ed'
    SESSION_TYPE = 'filesystem'    
    SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
