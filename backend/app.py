import asyncio
import json
from logging.config import dictConfig

import aio_pika
import uvicorn
from aio_pika import IncomingMessage
from fastapi import Depends, FastAPI, WebSocketDisconnect, WebSocket, status
from tortoise.contrib.fastapi import register_tortoise

from backend.auth.models import UserDB
from backend.auth.users import auth_backend, \
    current_active_user, fastapi_users, \
    get_jwt_strategy, get_user_manager, UserManager
from connection_manager import ConnectionManager

from settings import loging_config, SETTINGS


dictConfig(loging_config)
app = FastAPI()
connection_manager = ConnectionManager()


async def rabbitmq_consume(queue_name: str) -> None:
    connection = await aio_pika.connect_robust(
        host=SETTINGS.rabbit.host,
        port=SETTINGS.rabbit.port,
        login=SETTINGS.rabbit.user,
        password=SETTINGS.rabbit.password,
        virtualhost=SETTINGS.rabbit.vhost,
    )
    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=10)
        queue = await channel.declare_queue(queue_name)
        message: IncomingMessage
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    msg = json.loads(message.body.decode())
                    await connection_manager.broadcast(msg)


@app.on_event("startup")
def startup():
    asyncio.ensure_future(rabbitmq_consume('backend'))


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(
        websocket: WebSocket, client_id: int,
        user_manager: UserManager = Depends(get_user_manager)
):
    await websocket.accept()
    strategy = get_jwt_strategy()
    token: str = websocket.headers.get('Authorization')
    token = token if token is None else token.replace('Bearer ', '')
    user = await strategy.read_token(
         token, user_manager
    )
    if not (user is not None and user.is_active):
        await websocket.send_json({'msg': 'Unauthorized'})
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await connection_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await connection_manager.send_personal_message(
                {'client_id': client_id, 'says': data}, websocket
            )
            await connection_manager.broadcast(
                {'client_id': client_id, 'says': data}
            )
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
        await connection_manager.broadcast(
            {'client_id': client_id, 'event': 'left'}
        )


app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(),
    prefix="/auth", tags=["auth"]
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(),
    prefix="/users",
    tags=["users"]
)


@app.get("/authenticated-route")
async def authenticated_route(user: UserDB = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}


register_tortoise(
    app,
    db_url=f'postgres://'
           f'{SETTINGS.backend.psql.user}:{SETTINGS.backend.psql.password}@'
           f'{SETTINGS.backend.psql.host}:{SETTINGS.backend.psql.port}/'
           f'{SETTINGS.backend.psql.db}',
    modules={"models": ["backend.auth.models"]},
    generate_schemas=True
)

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
