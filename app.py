from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uuid
from datetime import datetime
from auth import hash_password, verify_password, create_token
from db import admins_table, tickets_table
from boto3.dynamodb.conditions import Key

app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")


# ========================
# Login Page
# ========================
@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    res = admins_table.get_item(Key={"username": username})
    user = res.get("Item")

    if not user or not verify_password(password, user["password_hash"]):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Invalid credentials"
        })

    response = RedirectResponse("/dashboard", status_code=302)
    response.set_cookie("admin", create_token(username))
    return response


# ========================
# Dashboard
# ========================
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    scan = tickets_table.scan()
    tickets = scan.get("Items", [])
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "tickets": tickets
    })


# ========================
# Create Ticket
# ========================
@app.get("/tickets/new", response_class=HTMLResponse)
def new_ticket_page(request: Request):
    return templates.TemplateResponse("create_ticket.html", {"request": request})


@app.post("/tickets/create")
def create_ticket(name: str = Form(...), level: str = Form(...), duration: int = Form(...)):
    ticket_id = str(uuid.uuid4())

    item = {
        "ticket_id": ticket_id,
        "name": name,
        "level": level,
        "issued_at": datetime.utcnow().isoformat(),
        "duration_minutes": duration,
        "status": "active"
    }

    tickets_table.put_item(Item=item)

    return RedirectResponse("/dashboard", status_code=302)