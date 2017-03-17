import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or '!I&Love#China%'
    SSL_DISABLE = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_RECORD_QUERIES = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:LocK&KeY1314@localhost:3306/dexcode'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    POSTS_PER_PAGE = 8
    COMMENTS_PER_POST = 15

    @staticmethod
    def init_app(app):
        pass
