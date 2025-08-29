from fastapi import FastAPI
from routers import auth_routes, shop_routes, game_routes
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "https://bingoapp-mocha.vercel.app",
    "https://bingoadmin-9wyy.vercel.app",
    "https://admin.halobingo.com",
    "https://www.halobingo.com",
    "https://corebingo.vercel.app",
    "http://localhost:5175",
    "http://localhost:5174",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "https://gojoapp.vercel.app",
    "https://gojoshop.vercel.app"
    # add other origins if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(shop_routes.router)
app.include_router(game_routes.router)
