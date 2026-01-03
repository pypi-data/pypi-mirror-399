<h1 align="center">Boask</h1>
<div align="center"><img src="https://0xopx.github.io/some-things-lol/boask/logo.svg" alt="Boask Logo" /><br>
Pure Python website engine. <br>
Zero external dependencies.<br>
</div>

```bash
pip install boask
```

## Quick Start

```python
from boask import route, use, run_server, html_templates

@route("/")
def home(handler):
    return html_templates.render("home.html", title="Boask")

if __name__ == "__main__":
    run_server()
```

### Comparison to Flask

1. Lightweight.
2. No external dependecies.
3. Unlike Flask, it's for beginners, and movers from Flask.
4. No `{{ url_for('static', filename='css/main.css') }}` (example), we use `/static/css/main.css` for example!

#### Info

1. Do not install a earlier version than 1.0.4, you can 1.0.0 but that one is not supported! You can't import them! Also, do not install 1.1.4! It had a bug in strict slashes and it did 500 always! I don't know how the 1.1.4 issue happened! Do not install 1.1.5a2 also! It has import error instead of import .error

##### Changelog

###### Right now

# New! "app" yeah, like Flask

## To use

```python
from boask import Boask

app = Boask()
```

## And to do it with route (yeah, i added `app.route()`) this example is for HTML templates

```python
from boask import Boask, route, use, run_server, html_templates

app = Boask()

def home(handler):
    return html_templates.render("home.html")
```

Note: Replace `home.html` with your file name (e.g `index.html`)

# New in authentication! Banning!

Usage:

```python
from auth.ban import Ban

# 'handler' is the instance of your HTTP request handler (from BaseHTTPRequestHandler, for example).
response = Ban.ban_user(handler)
```

# Advanced Auth Added!

## Example:

```python
from boask.core import route, use, run_server, Boask
from boask.middleware.advanced_auth import AdvancedAuth
from boask.auth.login import login
from boask.auth.register import register

app = Boask()
auth = AdvancedAuth()

use(auth.middleware)

@route("/register", methods=["POST"])
def do_register(handler):
    return register(handler)

@route("/login", methods=["POST"])
def do_login(handler):
    return login(handler)

@route("/dashboard", methods=["GET"])
@auth.protected
def dashboard(handler):
    return f"Welcome, {handler.user}!"

if __name__ == "__main__":
    run_server(port=8080, host="0.0.0.0")
```

INFO: DO NOT USE 1.1.6 YOU CAN BUT IT HAS A BROKEN README.