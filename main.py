from fastapi import FastAPI
from fastapi import Request
from fastapi import __version__ as fastapi_version
from fastapi.exceptions import HTTPException
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette import __version__ as starlette_version
from typing import Optional
from loguru import logger
from platform import python_version
from config import host
from config import port
from config import show_server_errors
from config import app_title
from config import app_description
from config import app_version
import uvicorn
import unalix
import re
import sys

app = FastAPI(
    docs_url=None,
    title=app_title,
    description=app_description,
    version=app_version,
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
    logger.info(
        f"app started.\npython version: {python_version()}\napp version: {app_version}\nunalix version: {unalix.__version__}\nfastapi version: {fastapi_version}\nstarlette version: {starlette_version}\nuvicorn version: {uvicorn.__version__}"
    )


@app.on_event("shutdown")
async def app_shutdown_actions():
    logger.info("app stopped.")


@app.get("/docs", include_in_schema=False)
async def docs_route_func():
    the_openapi_url = app.openapi_url
    the_docs_title = app.title + " docs"
    return get_swagger_ui_html(openapi_url=the_openapi_url, title=the_docs_title)


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
            "exception": f"error 400 {errortype}: {the_error_name}",
        },
    )


@app.exception_handler(404)
async def not_found_error_handle(request: Request, the_error: HTTPException):
    request_path = request.url.path
    return templates.TemplateResponse(
        "error.html", context={"request": request, "exception": f"error 404: page {request_path} is not found"}
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
                "exception": f"internal server error: {errortype}: {the_error_name}",
            },
        )


else:
    pass

if __name__ == "__main__":
    uvicorn.run(app=app, host=host, port=port)
