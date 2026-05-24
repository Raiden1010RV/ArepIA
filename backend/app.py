from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return {"mensaje": "Backend inicial funcionando 🚀"}

@app.route('/api/status')
def status():
    return {"status": "ok"}

if __name__ == '__main__':
    app.run(debug=True)