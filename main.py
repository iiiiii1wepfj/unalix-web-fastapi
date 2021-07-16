from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional
from config import port
import uvicorn, unalix, re

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"))


@app.get("/")
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
        old_url = url if re.match(r"^https?://", url) else "http://" + url
    else:
        return RedirectResponse("/docs")
    if not output:
        output = "html"

    if not method:
        method = "unshort"

    if not output in ["json", "html", "redirect"]:
        raise HTTPException(status_code=400)

    if not method in ["clear", "unshort"]:
        raise HTTPException(status_code=400)

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


uvicorn.run(app=app, host="0.0.0.0", port=port)
