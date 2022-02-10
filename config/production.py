from config.default import *

SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(os.path.join(BASE_DIR, 'pybo.db'))
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = b'\x12\xc8\x13\xed\x15q\n\xeex\xb7\xd0\x87\xc4\n\xfb\xe0'