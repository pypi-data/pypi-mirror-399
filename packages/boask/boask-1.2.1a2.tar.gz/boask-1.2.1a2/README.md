<h1 align="center">Boask</h1>
<div align="center"><img src="https://0xopx.github.io/some-things-lol/boask/logo.svg" alt="Boask Logo" /><br>
Minimal website engine. <br>
</div>

```bash
pip install boask
```
# Quick Start
```python
from boask import route, use, run_server, html_templates

@route("/")
def home(handler):
    return html_templates.render("home.html", title="Boask")

if __name__ == "__main__":
    run_server()
```
# Comparison to Flask
1. Lightweight.
2. No external dependecies.
3. Unlike Flask, it's for beginners, and movers from Flask.
4. No `{{ url_for('static', filename='css/main.css') }}` (example), we use `/static/css/main.css` for example!
# Info
1. Do not install a earlier version than 1.0.4, you can 1.0.0 but that one is not supported! You can't import them! Also, do not install 1.1.4! It had a bug in strict slashes and it did 500 always! I don't know how the 1.1.4 issue happened! Do not install 1.1.5a2 also! It has import error instead of import .error
# Changelog
## Now uses `pyproject.toml` instead of `setup.py`!