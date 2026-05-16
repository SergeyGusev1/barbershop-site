from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

from database import get_db, init_db, Category, Service, AdminUser

SECRET_KEY = "placeforbeauty-secret-2024-xK9mN3pQ"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
app = FastAPI(title="Place for Beauty API", docs_url=None, redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LoginRequest(BaseModel):
    username: str
    password: str


class ServiceCreate(BaseModel):
    category_id: int
    name: str
    price: str
    price_prefix: Optional[str] = ""
    description: Optional[str] = ""
    is_active: Optional[bool] = True
    order: Optional[int] = 0


class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[str] = None
    price_prefix: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    order: Optional[int] = None
    category_id: Optional[int] = None


class CategoryCreate(BaseModel):
    name: str
    slug: str
    icon: Optional[str] = "✨"
    order: Optional[int] = 0


def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str, db: Session):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.query(AdminUser).filter(AdminUser.username == username).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_user(authorization: str = None, db: Session = Depends(get_db)):
    from fastapi import Header
    return None


@app.on_event("startup")
async def startup():
    init_db()


@app.get("/api/services")
def get_services(db: Session = Depends(get_db)):
    categories = db.query(Category).order_by(Category.order).all()
    result = []
    for cat in categories:
        services = db.query(Service).filter(
            Service.category_id == cat.id,
            Service.is_active == True
        ).order_by(Service.order).all()
        result.append({
            "id": cat.id,
            "name": cat.name,
            "slug": cat.slug,
            "icon": cat.icon,
            "services": [
                {
                    "id": s.id,
                    "name": s.name,
                    "price": s.price,
                    "price_prefix": s.price_prefix,
                    "description": s.description,
                }
                for s in services
            ]
        })
    return result


@app.post("/api/admin/login")
def admin_login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(AdminUser).filter(AdminUser.username == req.username).first()
    if not user or not pwd_context.verify(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    token = create_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


def auth_required(authorization: str, db: Session):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.split(" ", 1)[1]
    return verify_token(token, db)


@app.get("/api/admin/categories")
def admin_get_categories(authorization: str = None, db: Session = Depends(get_db)):
    from fastapi import Header
    return db.query(Category).order_by(Category.order).all()


@app.post("/api/admin/categories")
def admin_create_category(
    data: CategoryCreate,
    authorization: str = None,
    db: Session = Depends(get_db)
):
    cat = Category(name=data.name, slug=data.slug, icon=data.icon, order=data.order)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return {"id": cat.id, "name": cat.name}


@app.get("/api/admin/services")
def admin_get_services(authorization: str = None, db: Session = Depends(get_db)):
    categories = db.query(Category).order_by(Category.order).all()
    result = []
    for cat in categories:
        services = db.query(Service).filter(
            Service.category_id == cat.id
        ).order_by(Service.order).all()
        result.append({
            "id": cat.id,
            "name": cat.name,
            "slug": cat.slug,
            "icon": cat.icon,
            "services": [
                {
                    "id": s.id,
                    "name": s.name,
                    "price": s.price,
                    "price_prefix": s.price_prefix,
                    "description": s.description,
                    "is_active": s.is_active,
                    "order": s.order,
                    "category_id": s.category_id,
                }
                for s in services
            ]
        })
    return result


@app.post("/api/admin/services")
def admin_create_service(data: ServiceCreate, db: Session = Depends(get_db)):
    s = Service(**data.dict())
    db.add(s)
    db.commit()
    db.refresh(s)
    return {"id": s.id, "name": s.name}


@app.put("/api/admin/services/{service_id}")
def admin_update_service(service_id: int, data: ServiceUpdate, db: Session = Depends(get_db)):
    s = db.query(Service).filter(Service.id == service_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Service not found")
    for field, value in data.dict(exclude_none=True).items():
        setattr(s, field, value)
    db.commit()
    return {"ok": True}


@app.delete("/api/admin/services/{service_id}")
def admin_delete_service(service_id: int, db: Session = Depends(get_db)):
    s = db.query(Service).filter(Service.id == service_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Service not found")
    db.delete(s)
    db.commit()
    return {"ok": True}


@app.put("/api/admin/categories/{cat_id}")
def admin_update_category(cat_id: int, data: CategoryCreate, db: Session = Depends(get_db)):
    cat = db.query(Category).filter(Category.id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Not found")
    cat.name = data.name
    cat.icon = data.icon
    cat.order = data.order
    db.commit()
    return {"ok": True}


@app.delete("/api/admin/categories/{cat_id}")
def admin_delete_category(cat_id: int, db: Session = Depends(get_db)):
    cat = db.query(Category).filter(Category.id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(cat)
    db.commit()
    return {"ok": True}


app.mount("/", StaticFiles(directory="static", html=True), name="static")
