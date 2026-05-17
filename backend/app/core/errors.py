from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

def register_error_handlers(app):

    @app.exception_handler(404)
    async def not_found(request: Request, exc):
        return JSONResponse(
            status_code=404,
            content={"error": "Not found", "detail": "The requested resource does not exist"}
        )

    @app.exception_handler(405)
    async def method_not_allowed(request: Request, exc):
        return JSONResponse(
            status_code=405,
            content={"error": "Method not allowed"}
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        errors = []
        for e in exc.errors():
            errors.append({
                "field": " -> ".join(str(x) for x in e["loc"]),
                "message": e["msg"]
            })
        return JSONResponse(
            status_code=422,
            content={"error": "Validation failed", "details": errors}
        )

    @app.exception_handler(Exception)
    async def unhandled_exception(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "detail": str(exc)}
        )