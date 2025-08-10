from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

def create_app():
    app = FastAPI(title="Infosonik App", version="1.0.0")
    
    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    from ..routes import expenses, auth
    app.include_router(expenses.router, prefix="/api")
    app.include_router(auth.router)
    
    return app