from fastapi import APIRouter, status, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
import os
from g4f.client import AsyncClient


router = APIRouter(prefix='/admin', include_in_schema=False, tags=["Admin panel"])
client = AsyncClient()


CLIENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(CLIENT_DIR, 'frontend')
CSS_DIR = os.path.join(FRONTEND_DIR, 'css')
JS_DIR = os.path.join(FRONTEND_DIR, 'js')


SYSTEM_PATHS = {
    '/admin/', '/admin/login', '/admin/panel', '/admin/api/',
    '/admin/api/app/status', '/admin/api/app/info', '/admin/api/app/restart',
    '/admin/api/console/execute', '/admin/frontend/', '/docs',
    '/openapi.json', '/redoc', '/favicon.ico'
}


@router.get('/frontend/css/{filename}')
async def get_css(filename: str):
    file_path = os.path.join(CSS_DIR, filename)
    print(f"[CSS] Request: {filename}, Path: {file_path}")
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return HTMLResponse(content=content, media_type="text/css")
    print(f"[CSS] File not found: {file_path}")
    return JSONResponse(status_code=404, content={"error": "File not found"})


@router.get('/frontend/js/{filename}')
async def get_js(filename: str):
    file_path = os.path.join(JS_DIR, filename)
    print(f"[JS] Request: {filename}, Path: {file_path}")
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return HTMLResponse(content=content, media_type="application/javascript")
    print(f"[JS] File not found: {file_path}")
    return JSONResponse(status_code=404, content={"error": "File not found"})


@router.get('/')
async def admin_index(request: Request):
    """
    Admin login page - displays the login form.
    """
    login_html_path = os.path.join(FRONTEND_DIR, 'index.html')

    if os.path.exists(login_html_path):
        with open(login_html_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())

    return {"message": "Admin Login Page", "status": "ready"}


@router.post('/login')
async def admin_login(username: str = Form(...), password: str = Form(...)):
    """
    Handle admin login authentication.
    Returns redirect to panel on success, error message on failure.
    """
    if username != "admin" or password != "admin":
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"success": False, "message": "Неверный логин или пароль"}
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"success": True, "message": "Успешная авторизация", "redirect_url": "/admin/panel"}
    )


@router.get('/panel')
async def admin_panel(request: Request):
    """
    Admin panel page - displays the main dashboard.
    """
    panel_html_path = os.path.join(FRONTEND_DIR, 'panel.html')

    if os.path.exists(panel_html_path):
        with open(panel_html_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Admin Panel", "status": "active"}
    )


@router.get('/api/app/status')
async def get_app_status(request: Request):
    """
    Get the status of the connected FastAPI application.
    """

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "running",
            "name": "FastAPI Application",
            "version": "1.0.0",
            "connected": True
        }
    )


@router.get('/api/app/info')
async def get_app_info(request: Request):
    """
    Get detailed information about the FastAPI application.
    Parses real endpoints from the app.routes.
    """
    app = getattr(request.state, 'app', None)
    endpoints = []

    if app and hasattr(app, 'routes'):
        for route in app.routes:
            try:
                if not hasattr(route, 'methods') or not hasattr(route, 'path'):
                    continue

                path = route.path

                if path in SYSTEM_PATHS or path.startswith('/admin/') or path.startswith('/docs') or \
                   path.startswith('/openapi') or path.startswith('/redoc') or path.startswith('/favicon'):
                    continue

                methods = route.methods

                for method in methods:
                    endpoint_info = {
                        "method": method.upper(),
                        "path": path,
                        "tag": "API"
                    }

                    endpoint_func = getattr(route, 'endpoint', None)
                    if endpoint_func:
                        func_name = getattr(endpoint_func, '__name__', str(endpoint_func))
                        endpoint_info["name"] = func_name

                        doc = getattr(endpoint_func, '__doc__', None)
                        if doc and doc.strip():
                            # Clean up docstring
                            description = doc.strip().split('\n')[0].strip()
                            endpoint_info["description"] = description
                        else:
                            endpoint_info["description"] = f"Handler: {func_name}"

                    route_name = getattr(route, 'name', None)
                    if route_name and route_name != endpoint_info.get('name'):
                        endpoint_info["description"] = f"{route_name}: {endpoint_info.get('description', '')}"

                    endpoints.append(endpoint_info)
            except Exception as e:
                print(f"Error parsing route: {e}")
                continue

    if not endpoints:
        endpoints = [
            {
                "method": "GET",
                "path": "/",
                "tag": "Root",
                "description": "Root endpoint"
            },
            {
                "method": "POST",
                "path": "/create/chat",
                "tag": "Chat",
                "description": "Create chat endpoint"
            }
        ]

    info = {
        "app_name": "FastAPI Application",
        "version": "1.0.0",
        "description": "FastAPI Admin Panel with Client functionality",
        "total_endpoints": len(endpoints),
        "endpoints": endpoints,
        "connected": True
    }

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=info
    )


@router.post('/api/app/restart')
async def restart_app(request: Request):
    """
    Restart the FastAPI application.
    """

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"success": True, "message": "Приложение перезапущено"}
    )


@router.get('/api/console/execute')
async def execute_console_command(request: Request, command: str):
    """
    Execute a console command in the admin panel.
    """
    commands = {
        'help': 'Доступные команды: help, status, clear, restart, info, version, uptime, memory, cpu',
        'status': 'Приложение работает стабильно. Все системы в норме.',
        'clear': 'Консоль очищена',
        'restart': 'Перезапуск приложения...',
        'info': 'FastAPI Admin Panel v1.0.0 - Мощная панель управления для FastAPI',
        'version': 'Версия: 1.0.0',
        'uptime': 'Время работы: Система активна',
        'memory': 'Использование памяти: В пределах нормы',
        'cpu': 'Нагрузка CPU: Оптимальная'
    }

    cmd = command.lower().strip()

    if cmd in commands:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"success": True, "output": commands[cmd]}
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"success": False, "output": f"Команда '{command}' не найдена. Введите 'help' для списка команд."}
    )


@router.post('/gpt')
async def gpt_panel(request: Request):
    """
    GPT chat endpoint with history support.
    Accepts message and optional conversation history.
    """
    try:
        data = await request.json()
        user_message = data.get('message', '')

        if not user_message:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": False, "error": "Message is required"}
            )

        response = await client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": user_message}]
        )

        ai_response = response.choices[0].message.content

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "response": ai_response,
                "model": "gpt-4"
            }
        )
    except Exception as e:
        print(f"GPT Error: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "error": str(e)}
        )