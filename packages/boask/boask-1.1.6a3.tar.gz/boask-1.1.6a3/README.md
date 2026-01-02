<h1 align="center">Boask</h1>
<div align="center"><img src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iOTYiIGhlaWdodD0iMzgiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGc+PHRleHQgZmlsbD0iI2U2ZTZlNiIgeD0iMCIgeT0iMjEiIGZvbnQtc2l6ZT0iMjQiIGZvbnQtZmFtaWx5PSJKb3N0Ij5Cb2FzazwvdGV4dD48dGV4dCBmaWxsPSIjYmJiYmJiIiB4PSIwIiB5PSIzNSIgZm9udC1zaXplPSIxMiIgZm9udC1mYW1pbHk9Ikpvc3QiIGZvbnQtc3R5bGU9Iml0YWxpYyI+UHVyZSBQeXRob248L3RleHQ+PC9nPjwvc3ZnPg==" alt="Boask Logo" /><br>
Pure Python website engine. <br>
Zero external dependencies.<br>
Real JSX-style templates without React.
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
3. Unlike flask, it uses built in python libaries only! It uses built-in libs, and some python file libs that are using only built in functions!
4. No "{{ url_for('static', filename='css/main.css') }}" (example), we use /static/css/main.css for example!

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

# Secret Message

## *shhhhh the tsx templates are a lie they are jsx templates but who cares bruh.*
