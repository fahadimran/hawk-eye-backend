from app import db, app, sock, create_app

app, sock = create_app(app, sock)

with app.app_context():
    db.create_all()
