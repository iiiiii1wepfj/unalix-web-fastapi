from fastapi import FastAPI
from fastapi import Request
from fastapi import __version__ as fastapi_version
from fastapi.exceptions import HTTPException
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.docs import get_redoc_html
from fastapi.responses import RedirectResponse
from fastapi.responses import ORJSONResponse
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import Response as StarletteResponseObject
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
        "HEAD",
        "OPTIONS",
        "DELETE",
        "PATCH",
        "PUT",
    ]
from typing import Optional
from typing import Literal
from typing import Any
from loguru import logger
from loguru import __version__ as loguru_version
from platform import python_version as get_python_version
from config import app_host
from config import app_port
from config import show_server_errors
from config import app_title
from config import app_description
from config import log_format
from config import the_license_name
from config import the_license_link
from config import org_name
from config import org_website
from config import org_mail
from config import app_version
from config import unalix_conf_http_timeout
from config import app_debug_mode
from datetime import datetime
import uvicorn
import yaml
import toml
import simplexml
import unalix
import re
import sys
import os


# https://github.com/tiangolo/fastapi/issues/558
class XMLResponse(
    StarletteResponseObject,
):
    media_type = "application/xml"

    def render(
        self,
        content: Any,
    ) -> bytes:
        json_res_one = {
            "response": content,
        }
        res_one = simplexml.dumps(
            json_res_one,
        )
        res = res_one.encode(
            "utf-8",
        )
        return res


class YAMLResponse(
    StarletteResponseObject,
):

    media_type = "application/yaml"


class JSONPResponse(
    StarletteResponseObject,
):

    media_type = "application/javascript"


class TOMLResponse(
    StarletteResponseObject,
):

    media_type = "application/toml"


unalix.config.HTTP_TIMEOUT = unalix_conf_http_timeout

the_license_info = {
    "name": f"{the_license_name}",
    "url": f"{the_license_link}",
}

the_contact_info = {
    "name": f"{org_name}",
    "url": f"{org_website}",
    "email": f"{org_mail}",
}

app = FastAPI(
    docs_url=None,
    redoc_url=None,
    title=app_title,
    description=app_description,
    version=app_version,
    debug=app_debug_mode,
    contact=the_contact_info,
    license_info=the_license_info,
)

templates = Jinja2Templates(
    directory="templates",
)

app.mount(
    path="/static",
    app=StaticFiles(
        directory="static",
    ),
    name="static",
)

logger.add(
    sink=sys.stdout,
    colorize=True,
    format=log_format,
)


output_options = (
    "html",
    "json",
    "jsonp",
    "xml",
    "yaml",
    "toml",
    "text",
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
    event_type="startup",
)
async def app_startup_actions():
    py_version = get_python_version()
    unalix_version = unalix.__version__
    uvicorn_version = uvicorn.__version__
    jinja2_version = jinja2.__version__
    orjson_version = orjson.__version__
    aiofiles_version = aiofiles.__version__
    pydantic_version = pydantic.version.VERSION
    re_version = re.__version__
    simplexml_version = simplexml.__version__
    toml_version = toml.__version__
    app_pid = os.getpid()
    the_time_datetime = datetime.now()
    the_year_now = the_time_datetime.year
    logger.info(
        "app started.\n"
        f"python version: {py_version},\n"
        f"app version: {app_version},\n"
        f"unalix version: {unalix_version},\n"
        f"fastapi version: {fastapi_version},\n"
        f"starlette version: {starlette_version},\n"
        f"uvicorn version: {uvicorn_version},\n"
        f"jinja2 version: {jinja2_version},\n"
        f"orjson version: {orjson_version},\n"
        f"aiofiles version: {aiofiles_version},\n"
        f"pydantic version: {pydantic_version},\n"
        f"re version: {re_version},\n"
        f"loguru version: {loguru_version},\n"
        f"simplexml version: {simplexml_version},\n"
        f"toml version: {toml_version},\n"
        f"app pid: {app_pid}."
        f"\n\n© {the_year_now} Amano Team.\n\n"
    )


@app.on_event(
    event_type="shutdown",
)
async def app_shutdown_actions():
    logger.info(
        "app stopped, bye.",
    )


@app.api_route(
    path="/docs",
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
    path="/redoc",
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
    path="/",
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
        name="index.html",
        status_code=200,
        context={
            "request": request,
        },
    )


@app.api_route(
    path="/api",
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
            status_code=307,
            url="/docs",
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
            detail="invalid output type, the supported output types are json or jsonp or xml or yaml or toml or text or html or redirect.",
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
                url=old_url,
                parse_documents=True,
            )
        elif method == "clear":
            new_url = unalix.clear_url(
                url=old_url,
            )
    except unalix.exceptions.ConnectError as exception:
        new_url = exception.url
    except Exception as exception:
        errtype_one = type(
            exception,
        )
        errtype = errtype_one.__name__
        if output == "html":
            errmsgone = f"{errtype}: {exception}"
            return templates.TemplateResponse(
                name="error.html",
                status_code=500,
                context={
                    "request": request,
                    "exception": f"{errmsgone}.",
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
        if output == "jsonp":
            errmsgone = f"{errtype}: {exception}"
            resjson = {
                "exception": f"{errmsgone}",
            }
            return JSONPResponse(
                status_code=500,
                content=f"response({resjson})",
            )
        if output == "xml":
            errmsgone = f"{errtype}: {exception}"
            return XMLResponse(
                status_code=500,
                content={
                    "exception": f"{errmsgone}",
                },
            )
        if output == "yaml":
            errmsgone = f"{errtype}: {exception}"
            return templates.TemplateResponse(
                name="error.html",
                status_code=500,
                context={
                    "request": request,
                    "exception": f"{errmsgone}.",
                },
            )
        if output == "toml":
            errmsgone = f"{errtype}: {exception}"
            return templates.TemplateResponse(
                name="error.html",
                status_code=500,
                context={
                    "request": request,
                    "exception": f"{errmsgone}.",
                },
            )
        if output == "text":
            return PlainTextResponse(
                status_code=500,
                content=f"{errtype}: {exception}",
            )
        if output == "redirect":
            errmsgone = f"{errtype}: {exception}"
            raise HTTPException(
                status_code=500,
                detail=f"{errmsgone}",
            )

    if output == "html":
        return templates.TemplateResponse(
            name="success.html",
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
    if output == "jsonp":
        jsonres = {
            "new_url": f"{new_url}",
        }
        return JSONPResponse(
            status_code=200,
            content=f"response({jsonres})",
        )
    if output == "xml":
        return XMLResponse(
            status_code=200,
            content={
                "new_url": f"{new_url}",
            },
        )
    if output == "yaml":
        jsonres = {
            "new_url": f"{new_url}",
        }
        return YAMLResponse(
            status_code=200,
            content=yaml.dump(
                jsonres,
            ),
        )
    if output == "toml":
        jsonres = {
            "new_url": f"{new_url}",
        }
        return TOMLResponse(
            status_code=200,
            content=toml.dumps(
                jsonres,
            ),
        )
    if output == "text":
        return PlainTextResponse(
            status_code=200,
            content=new_url,
        )
    if output == "redirect":
        return RedirectResponse(
            status_code=307,
            url=new_url,
        )


@app.exception_handler(
    exc_class_or_status_code=400,
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
        name="error.html",
        status_code=400,
        context={
            "request": request,
            "exception": f"error 400 {errmsgone}.",
        },
    )


@app.exception_handler(
    exc_class_or_status_code=404,
)
async def page_not_found_error_handle(
    request: Request,
    the_error: HTTPException,
):
    request_path = request.url
    request_path = request_path.path
    request_url = request.url
    request_url = request_url.hostname
    request_url_http_or_https = request.url
    request_url_http_or_https = request_url_http_or_https.scheme
    request_url_http_or_https = f"{request_url_http_or_https}://"
    request_full_url = f"{request_url_http_or_https}{request_url}{request_path}"
    return templates.TemplateResponse(
        name="error.html",
        status_code=404,
        context={
            "request": request,
            "exception": f"error 404: page {request_full_url} is not found.",
        },
    )


@app.exception_handler(
    exc_class_or_status_code=405,
)
async def method_not_allowed_error_handle(
    request: Request,
    the_error: HTTPException,
):
    request_http_method = request.method
    request_path = request.url
    request_path = request_path.path
    request_url = request.url
    request_url = request_url.hostname
    request_url_http_or_https = request.url
    request_url_http_or_https = request_url_http_or_https.scheme
    request_url_http_or_https = f"{request_url_http_or_https}://"
    request_full_url = f"{request_url_http_or_https}{request_url}{request_path}"
    return templates.TemplateResponse(
        name="error.html",
        status_code=405,
        context={
            "request": request,
            "exception": f"error 405: method {request_http_method} is not allowed for {request_full_url}.",
        },
    )


if show_server_errors:

    @app.exception_handler(
        exc_class_or_status_code=500,
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
            name="error.html",
            status_code=500,
            context={
                "request": request,
                "exception": f"error 500 internal server error: {errmsgone}.",
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
        "you can't import this.",
    )
