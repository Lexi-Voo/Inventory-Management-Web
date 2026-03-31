from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from sqlalchemy.orm import Session
from .models import SessionLocal, Item, init_db

app = FastAPI()

BASE_DIR = Path(__file__).parent.resolve()

templates_env = Environment(
    loader=FileSystemLoader(str(BASE_DIR / "templates")),
    autoescape=select_autoescape(['html', 'xml']),
    cache_size=0
)

# Init DB
init_db()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def render_template(template_name: str, **context):
    template = templates_env.get_template(template_name)
    return template.render(**context)

# READ
@app.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    items = db.query(Item).all()
    low_stock_count = len([i for i in items if i.quantity < 5])

    return HTMLResponse(render_template(
        "index.html",
        request=request,
        items=items,
        low_stock_count=low_stock_count
    ))

# CREATE
@app.get("/add")
def add_page(request: Request):
    return HTMLResponse(render_template("add.html", request=request))

@app.post("/add")
def add_item(name: str = Form(...), quantity: int = Form(...), location: str = Form(...), db: Session = Depends(get_db)):
    new_item = Item(name=name, quantity=quantity, location=location)
    db.add(new_item)
    db.commit()
    return RedirectResponse("/", status_code=303)

# UPDATE
@app.get("/edit/{item_id}")
def edit_page(request: Request, item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    return HTMLResponse(render_template("edit.html", request=request, item=item))

@app.post("/edit/{item_id}")
def update_item(item_id: int, name: str = Form(...), quantity: int = Form(...), location: str = Form(...), db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if item:
        item.name = name
        item.quantity = quantity
        item.location = location
        db.commit()
    return RedirectResponse("/", status_code=303)

# DELETE
@app.post("/delete/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if item:
        db.delete(item)
        db.commit()
    return RedirectResponse("/", status_code=303)