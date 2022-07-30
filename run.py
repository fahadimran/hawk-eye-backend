from app import app, sock, create_app

app, sock = create_app(app, sock)

if __name__ == '__main__':
    app.run()
