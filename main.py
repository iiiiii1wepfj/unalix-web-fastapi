from fastapi import FastAPI
from fastapi import Request
from fastapi import __version__ as fastapi_version
from fastapi.exceptions import HTTPException
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.docs import get_redoc_html
from fastapi.responses import RedirectResponse
from fastapi.responses import ORJSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette import __version__ as starlette_version
import jinja2
import orjson
import aiofiles
import pydantic


try:
    from starlette.middleware.cors import ALL_METHODS
except:
    ALL_METHODS = [
        "POST",
        "GET",
    ]
from typing import Optional
from typing import Literal
from loguru import logger
from platform import python_version
from config import app_host
from config import app_port
from config import show_server_errors
from config import app_title
from config import app_description
from config import log_format
from config import app_version
from config import app_debug_mode
import uvicorn
import unalix
import re
import sys


app = FastAPI(
    docs_url=None,
    redoc_url=None,
    title=app_title,
    description=app_description,
    version=app_version,
    debug=app_debug_mode,
)

templates = Jinja2Templates(
    directory="templates",
)

app.mount(
    "/static",
    StaticFiles(
        directory="static",
    ),
)

logger.add(
    sys.stdout,
    colorize=True,
    format=log_format,
)


output_options = (
    "html",
    "json",
    "redirect",
)

method_optings = (
    "unshort",
    "clear",
)
methodliteraloptions = Literal[method_optings]
outputliteraloptions = Literal[output_options]


async def check_url(
    url: str,
):
    if re.match(
        r"^https?://",
        url,
    ):
        the_url = url
    else:
        the_url = "http://" + url
    return the_url


async def get_error_message(
    error,
):
    errortype = type(
        error,
    )
    errortype = errortype.__name__
    if errortype != "HTTPException":
        the_error = error
    else:
        the_error = error.detail
    return the_error


@app.on_event(
    "startup",
)
async def app_startup_actions():
    py_version = python_version()
    unalix_version = unalix.__version__
    uvicorn_version = uvicorn.__version__
    jinja2_version = jinja2.__version__
    orjson_version = orjson.__version__
    aiofiles_version = aiofiles.__version__
    pydantic_version = pydantic.version.VERSION
    logger.info(
        "app started.\n"
        f"python version: {py_version}\n"
        f"app version: {app_version}\n"
        f"unalix version: {unalix_version}\n"
        f"fastapi version: {fastapi_version}\n"
        f"starlette version: {starlette_version}\n"
        f"uvicorn version: {uvicorn_version}\n"
        f"jinja2 version: {jinja2_version}\n"
        f"orjson version: {orjson_version}\n"
        f"aiofiles version: {aiofiles_version}\n"
        f"pydantic version: {pydantic_version}"
    )


@app.on_event(
    "shutdown",
)
async def app_shutdown_actions():
    logger.info(
        "app stopped, bye.",
    )


@app.api_route(
    "/docs",
    include_in_schema=False,
    methods=ALL_METHODS,
)
async def docs_swagger_route_func():
    the_openapi_url = app.openapi_url
    the_docs_title = app.title + " docs"
    return get_swagger_ui_html(
        openapi_url=the_openapi_url,
        title=the_docs_title,
    )


@app.api_route(
    "/redoc",
    include_in_schema=False,
    methods=ALL_METHODS,
)
async def docs_redoc_route_func():
    the_openapi_url = app.openapi_url
    the_docs_title = app.title + " docs"
    return get_redoc_html(
        openapi_url=the_openapi_url,
        title=the_docs_title,
    )


@app.api_route(
    "/",
    include_in_schema=False,
    methods=[
        "POST",
        "GET",
    ],
)
async def home(
    request: Request,
):
    return templates.TemplateResponse(
        "index.html",
        status_code=200,
        context={
            "request": request,
        },
    )


@app.api_route(
    "/api",
    methods=[
        "POST",
        "GET",
    ],
)
async def api(
    request: Request,
    method: Optional[methodliteraloptions] = None,
    url: Optional[str] = None,
    output: Optional[outputliteraloptions] = None,
):
    if url:
        old_url = await check_url(
            url=url,
        )
    else:
        return RedirectResponse(
            "/docs",
        )

    if not output:
        output = "html"

    if not method:
        method = "unshort"

    if not output in list(
        output_options,
    ):
        raise HTTPException(
            status_code=400,
            detail="invalid output type, the supported output types are json or html or redirect.",
        )

    if not method in list(
        method_optings,
    ):
        raise HTTPException(
            status_code=400,
            detail="invalid method type, the supported method types are clear or unshort.",
        )

    try:
        if method == "unshort":
            new_url = unalix.unshort_url(
                old_url,
                parse_documents=True,
            )
        elif method == "clear":
            new_url = unalix.clear_url(
                old_url,
            )
    except unalix.exceptions.ConnectError as exception:
        new_url = exception.url
    except Exception as exception:
        errtype = type(
            exception,
        )
        if output == "html":
            errmsgone = f"{errtype}: {exception}"
            return templates.TemplateResponse(
                "error.html",
                status_code=500,
                context={
                    "request": request,
                    "exception": f"{errmsgone}",
                },
            )
        if output == "json":
            errmsgone = f"{errtype}: {exception}"
            return ORJSONResponse(
                status_code=500,
                content={
                    "exception": f"{errmsgone}",
                },
            )
            return

        if output == "redirect":
            errmsgone = f"{errtype}: {exception}"
            raise HTTPException(
                status_code=500,
                detail=f"{errmsgone}",
            )

    if output == "html":
        return templates.TemplateResponse(
            "success.html",
            status_code=200,
            context={
                "request": request,
                "new_url": f"{new_url}",
            },
        )

    if output == "json":
        return ORJSONResponse(
            status_code=200,
            content={
                "new_url": f"{new_url}",
            },
        )

    if output == "redirect":
        return RedirectResponse(
            new_url,
        )


@app.exception_handler(
    400,
)
async def not_found_error_handle(
    request: Request,
    the_error: HTTPException,
):
    errortype = type(
        the_error,
    )
    errortype = errortype.__name__
    the_error_name = await get_error_message(
        error=the_error,
    )
    errmsgone = f"{errortype}: {the_error_name}"
    return templates.TemplateResponse(
        "error.html",
        status_code=400,
        context={
            "request": request,
            "exception": f"error 400 {errmsgone}",
        },
    )


@app.exception_handler(
    404,
)
async def page_not_found_error_handle(
    request: Request,
    the_error: HTTPException,
):
    request_path = request.url
    request_path = request_path.path
    request_url = request.client
    request_url = request_url.host
    request_full_url = f"{request_url}{request_path}"
    return templates.TemplateResponse(
        "error.html",
        status_code=404,
        context={
            "request": request,
            "exception": f"error 404: page {request_full_url} is not found",
        },
    )


@app.exception_handler(
    405,
)
async def method_not_allowed_error_handle(
    request: Request,
    the_error: HTTPException,
):
    return templates.TemplateResponse(
        "error.html",
        status_code=405,
        context={
            "request": request,
            "exception": f"error 405: method not allowed",
        },
    )


if show_server_errors:

    @app.exception_handler(
        500,
    )
    async def internal_server_error(
        request: Request,
        the_error: HTTPException,
    ):
        errortype = type(
            the_error,
        )
        errortype = errortype.__name__
        the_error_name = await get_error_message(
            error=the_error,
        )
        errmsgone = f"{errortype}: {the_error_name}"
        return templates.TemplateResponse(
            "error.html",
            status_code=500,
            context={
                "request": request,
                "exception": f"internal server error: {errmsgone}",
            },
        )


else:
    pass

if __name__ == "__main__":
    uvicorn.run(
        app=app,
        host=app_host,
        port=app_port,
    )
else:
    sys.exit(
        1,
    )
