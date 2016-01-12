# -*- coding:utf-8 -*-

import os


basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    MAIL_SERVER = 'smtp.yeah.net'
    MAIL_PORT = 25
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FLASKY_MAIL_SUBJECT_PREFIX = '[CQUPT Training System]'
    FLASKY_MAIL_SENDER = 'CQUPT-TS Admin <slowlight@yeah.net>'
    FLASKY_ADMIN = 'slowlight@yeah.net'

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    #SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
    #    'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@localhost/test'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    assert SQLALCHEMY_DATABASE_URI


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}