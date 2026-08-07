from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException, RequestValidationError
from .api.v1 import health, auth, users, game, levels, progress, achievements, coins, themes, leaderboard, daily, shop, friends, stats, notifications, admin, cloud, profile, settings, inventory, transactions, sync_queue

from fastapi.middleware.gzip import GZipMiddleware

app = FastAPI(title="Arrow Escape API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    code = "HTTP_ERROR"
    if exc.status_code == 404: code = "NOT_FOUND"
    elif exc.status_code == 401: code = "UNAUTHORIZED"
    elif exc.status_code == 400: code = "BAD_REQUEST"
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": code,
                "message": str(exc.detail)
            }
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request payload format."
            }
        }
    )

app.include_router(health.router, prefix="/api/v1/health", tags=["Health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["User"])
app.include_router(game.router, prefix="/api/v1/game", tags=["Game"])
app.include_router(levels.router, prefix="/api/v1/levels", tags=["Levels"])
app.include_router(progress.router, prefix="/api/v1/progress", tags=["Progress"])
app.include_router(profile.router, prefix="/api/v1/profile", tags=["Profile"])
app.include_router(stats.router, prefix="/api/v1/stats", tags=["Stats"])
app.include_router(settings.router, prefix="/api/v1/settings", tags=["Settings"])
app.include_router(cloud.router, prefix="/api/v1/cloud", tags=["Cloud Sync"])
app.include_router(inventory.router, prefix="/api/v1/inventory", tags=["Inventory"])
app.include_router(transactions.router, prefix="/api/v1/transactions", tags=["Transactions"])
app.include_router(sync_queue.router, prefix="/api/v1/sync", tags=["Sync Status"])
app.include_router(achievements.router, prefix="/api/v1/achievements", tags=["Achievements"])
app.include_router(coins.router, prefix="/api/v1/coins", tags=["Coins"])
app.include_router(themes.router, prefix="/api/v1/themes", tags=["Themes"])
app.include_router(leaderboard.router, prefix="/api/v1/leaderboard", tags=["Leaderboard"])
app.include_router(daily.router, prefix="/api/v1/daily", tags=["Daily Challenges"])
app.include_router(shop.router, prefix="/api/v1/shop", tags=["Shop"])
app.include_router(friends.router, prefix="/api/v1/friends", tags=["Friends"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["Notifications"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])

@app.get("/api/v1/config")
def get_config():
    return {
        "title": "Arrow Escape",
        "total_levels": 50,
        "max_stars": 150,
        "heart_limits": {"max_hearts": 3},
        "star_thresholds": {"three_stars": 0.50, "two_stars": 0.70, "one_star": 0.80},
        "coin_policy": {"three_stars": 1.0, "two_stars": 0.7, "one_star": 0.5, "zero_stars": 0.0}
    }
