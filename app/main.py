from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
import os
from dotenv import load_dotenv

app = FastAPI()

BASE_DIR = Path(__file__).parent.resolve()
templates_env = Environment(
    loader=FileSystemLoader(str(BASE_DIR / "templates")),
    autoescape=select_autoescape(['html', 'xml']),
    cache_size=0
)

# Load .env locally, and Read ENV variables in Render
load_dotenv()
app_name = os.environ["APP_NAME"]
app_env = os.environ["APP_ENV"]

# In-memory inventory
items = [
    {"name": "Keyboard", "quantity": 10, "location": "Warehouse A"},
    {"name": "Mouse", "quantity": 2, "location": "Warehouse B"},
]

def render_template(template_name: str, **context):
    template = templates_env.get_template(template_name)
    return template.render(**context)

@app.get("/")
def home(request: Request):
    low_stock_count = len([item for item in items if item["quantity"] < 5])
    html_content = render_template(
        "index.html",
        request=request,
        items=items,
        low_stock_count=low_stock_count,
        app_name=app_name,    # <-- Pass app_name
        app_env=app_env       # <-- Pass app_env
    )
    return HTMLResponse(content=html_content)

@app.get("/add")
def add_page(request: Request):
    html_content = render_template(
        "add.html",
        request=request,
        app_name=app_name,    # <-- Pass app_name
        app_env=app_env       # <-- Pass app_env
    )
    return HTMLResponse(content=html_content)

@app.post("/add")
def add_item(name: str = Form(...), quantity: int = Form(...), location: str = Form(...)):
    items.append({"name": name, "quantity": quantity, "location": location})
    return RedirectResponse("/", status_code=303)