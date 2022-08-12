from fastapi import FastAPI
from app.routers import auth, user, product, cart, order
app = FastAPI()

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(product.router)
app.include_router(cart.router)
app.include_router(order.router)


@app.get("/")
def root():
    return {"message": "reached root"}
