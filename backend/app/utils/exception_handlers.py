from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.schemas.enums import ALLOWED_ASSIGNEES, ALLOWED_CATEGORIES, ALLOWED_PRIORITIES
from app.schemas.task import InvalidEnumValueException


async def invalid_enum_value_handler(request: Request, exc: InvalidEnumValueException):
    return JSONResponse(
        status_code=400,
        content={
            "error": "invalid_enum_value",
            "field": exc.field,
            "received": exc.received,
            "allowed": exc.allowed
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    for err in exc.errors():
        # Check if custom exception is attached
        ctx = err.get("ctx", {})
        if "error" in ctx and isinstance(ctx["error"], InvalidEnumValueException):
            custom_exc = ctx["error"]
            return JSONResponse(
                status_code=400,
                content={
                    "error": "invalid_enum_value",
                    "field": custom_exc.field,
                    "received": custom_exc.received,
                    "allowed": custom_exc.allowed
                }
            )

        # Also inspect field names if standard pydantic error caught enum mismatch
        loc = err.get("loc", [])
        field_name = loc[-1] if loc else ""
        if field_name == "assignee_id":
            input_val = err.get("input")
            return JSONResponse(
                status_code=400,
                content={
                    "error": "invalid_enum_value",
                    "field": "assignee_id",
                    "received": input_val,
                    "allowed": ALLOWED_ASSIGNEES
                }
            )
        elif field_name == "category":
            input_val = err.get("input")
            return JSONResponse(
                status_code=400,
                content={
                    "error": "invalid_enum_value",
                    "field": "category",
                    "received": input_val,
                    "allowed": ALLOWED_CATEGORIES
                }
            )
        elif field_name == "priority":
            input_val = err.get("input")
            return JSONResponse(
                status_code=400,
                content={
                    "error": "invalid_enum_value",
                    "field": "priority",
                    "received": input_val,
                    "allowed": ALLOWED_PRIORITIES
                }
            )

    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )
