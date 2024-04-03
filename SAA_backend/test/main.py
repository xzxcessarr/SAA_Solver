import uvicorn
from fastapi import FastAPI,Header,Body,Form,Request
from fastapi.responses import FileResponse,HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
app=FastAPI()
# template=Jinja2Templates("dist")
app.mount("/", StaticFiles(directory="dist", html=True), name="static")


# @app.get("/")
# def index(req: Request):
#     """使用fastapi作为后端"""
    # html="""
    # <html>
    # <body>hello fastapi</body>
    # </html>
    #
    # """
    # return template.TemplateResponse("index.html",context={"request":req})
    # return HTMLResponse(content=html,
    #                     headers={"a":"b"})
@app.get("/picture")
def picture():
    avatar="./爱丽丝之神-60.jpg"
    return FileResponse(avatar
                        # ,filename="爱丽丝之神-60.jpg"
                        )
@app.post("/login")
def login(username=Form(None),password=Form(None)):
    return {"data":{"username":username,"password":password}}

@app.get("/route")
def user(id,head=Header(None)):
    return {"msg":id, "head":head}

if __name__=='__main__':
    uvicorn.run(app)