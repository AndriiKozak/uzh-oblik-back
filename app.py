from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, World1!'

if __name__ == '__main__':
    # Змінено параметри запуску, щоб вказати порт явно
    app.run(host='0.0.0.0', port=5000)
