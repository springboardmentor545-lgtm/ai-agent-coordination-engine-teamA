from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.endpoints import router as api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
)

<<<<<<< HEAD
import time
import logging
from starlette.requests import Request

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger.info(f"[START] Request received: {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    process_time = (time.time() - start_time) * 1000
    logger.info(f"[COMPLETED] {request.method} {request.url.path} - Status: {response.status_code} - Took: {process_time:.2f}ms")
    return response

=======
>>>>>>> team/main
# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health")
def health_check():
<<<<<<< HEAD
    return {"status": "ok", "message": "VitalGate AI Backend is running"}
=======
    return {"status": "ok", "message": "CareTriage AI Backend is running"}
>>>>>>> team/main
