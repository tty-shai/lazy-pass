from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Template
from cryptography.fernet import Fernet
import sqlite3, os

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

def get_cipher():
    return Fernet(open(".key", "rb").read())

def db():
    return sqlite3.connect("secrets.db")

@app.get("/", response_class=HTMLResponse)
def dashboard():
    html = """
    <html><body style="background:#111;color:#eee;font-family:sans-serif">
    <h2>SecretVault</h2>
    <form action="/add" method="post">
      <select name="type">
        <option>API</option><option>Password</option><option>Token</option>
      </select>
      <input name="name" placeholder="Название">
      <input name="value" placeholder="Содержимое">
      <button>Сохранить</button>
    </form>
    <hr>
    {% for s in secrets %}
      <div>
        <b>[{{s[1]}}]</b> {{s[2]}}
        <input type="password" value="{{s[3]}}" readonly>
      </div>
    {% endfor %}
    </body></html>
    """
    c = get_cipher()
    con = db()
    data = [
        (r[0], r[1], r[2], c.decrypt(r[3]).decode())
        for r in con.execute("SELECT * FROM secrets").fetchall()
    ]
    con.close()
    return Template(html).render(secrets=data)

@app.post("/add")
def add(type: str = Form(), name: str = Form(), value: str = Form()):
    c = get_cipher()
    con = db()
    con.execute("INSERT INTO secrets (type,name,value) VALUES (?,?,?)",
                (type, name, c.encrypt(value.encode())))
    con.commit(); con.close()
    return RedirectResponse("/", status_code=303)


1231