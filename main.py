from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional
from loguru import logger
from config import host
from config import port
from config import show_server_errors
import uvicorn
import unalix
import re
import sys

app = FastAPI(
    docs_url=None,
    title="Unalix-web",
    description="source code: https://github.com/AmanoTeam/unalix-web-fastapi.",
    version="2.0",
)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"))

logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:HH:mm:ss}</green> | {level} | <level>{message}</level>",
)


async def check_url(url: str):
    if re.match(r"^https?://", url):
        the_url = url
    else:
        the_url = "http://" + url
    return the_url


@app.on_event("startup")
async def app_startup_actions():
    logger.info("app started.")


@app.on_event("shutdown")
async def app_shutdown_actions():
    logger.info("app stopped.")


@app.get("/docs", include_in_schema=False)
async def docs_route_func():
    return get_swagger_ui_html(openapi_url=app.openapi_url, title=app.title + " docs")


@app.get("/", include_in_schema=False)
async def home(request: Request):
    return templates.TemplateResponse("index.html", context={"request": request})


@app.api_route("/api", methods=["POST", "GET"])
async def api(
    request: Request,
    method: Optional[str] = None,
    url: Optional[str] = None,
    output: Optional[str] = None,
):
    if url:
        old_url = await check_url(url)
    else:
        return RedirectResponse("/docs")

    if not output:
        output = "html"

    if not method:
        method = "unshort"

    if not output in ["json", "html", "redirect"]:
        raise HTTPException(
            status_code=400,
            detail="invalid output type, the supported output types are json or html or redirect.",
        )

    if not method in ["clear", "unshort"]:
        raise HTTPException(
            status_code=400,
            detail="invalid method type, the supported method types are clear or unshort.",
        )

    try:
        if method == "unshort":
            new_url = unalix.unshort_url(old_url, parse_documents=True)
        elif method == "clear":
            new_url = unalix.clear_url(old_url)
    except unalix.exceptions.ConnectError as exception:
        new_url = exception.url
    except Exception as exception:
        if output == "html":
            return templates.TemplateResponse(
                "error.html", context={"request": request, "exception": str(exception)}
            )
        if output == "json":
            return {"exception": str(exception)}

        if output == "redirect":
            raise HTTPException(status_code=500)

    if output == "html":
        return templates.TemplateResponse(
            "success.html", context={"request": request, "new_url": new_url}
        )

    if output == "json":
        return {"new_url": new_url}

    if output == "redirect":
        return RedirectResponse(new_url)


async def get_error_message(error):
    errortype = type(error).__name__
    if errortype != "HTTPException":
        the_error = error
    else:
        the_error = error.detail
    return the_error


@app.exception_handler(400)
async def not_found_error_handle(request: Request, the_error: HTTPException):
    errortype = type(the_error).__name__
    the_error_name = await get_error_message(error=the_error)
    return templates.TemplateResponse(
        "error.html",
        context={
            "request": request,
            "exception": f"400 {errortype}: {the_error_name}",
        },
    )


@app.exception_handler(404)
async def not_found_error_handle(request: Request, the_error: HTTPException):
    return templates.TemplateResponse(
        "error.html", context={"request": request, "exception": "404: not found"}
    )


if show_server_errors:

    @app.exception_handler(500)
    async def internal_server_error(request: Request, the_error: HTTPException):
        errortype = type(the_error).__name__
        the_error_name = await get_error_message(error=the_error)
        return templates.TemplateResponse(
            "error.html",
            context={
                "request": request,
                "exception": f"server_error: {errortype}: {the_error_name}",
            },
        )


else:
    pass

if __name__ == "__main__":
    uvicorn.run(app=app, host=host, port=port)
