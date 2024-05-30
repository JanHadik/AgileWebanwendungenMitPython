import secrets

SECRET_KEY = secrets.token_hex(16)
SQLALCHEMY_DATABASE_URI = "sqlite:///database_flagstravaganza.sqlite"

# Used for password hashing
salt = b'(Y>\x9e\xf3E\xfe\x03\x17\xfb.\xbd\xf8[O\xdd\xb5\xca#\xdfq\x10\xaf\x0e\x94#\xb2<\xdd:\xbe)'
