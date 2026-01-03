from fastapi import WebSocket, WebSocketDisconnect
from fastapi.routing import APIRouter
from loguru import logger
import json
import uuid
from .websocket_manager import websocket_manager

websocket_router = APIRouter()

@websocket_router.websocket("/sdk/ws")
async def sdk_websocket_endpoint(websocket: WebSocket):
    # Authenticate WebSocket connection before accepting
    # Get trusted_domain from app.state if available
    # trusted_domain = getattr(websocket.app.state, "trusted_domain", "ring.shiweinan.com")
    # enable_auth = getattr(websocket.app.state, "enable_auth_middleware", True)
    
    # if enable_auth:
    #     from service_forge.api.http_api import authenticate_websocket
    #     await authenticate_websocket(websocket, trusted_domain)
    # else:
    #     # If auth is disabled, set default values
    #     websocket.state.user_id = websocket.headers.get("X-User-ID", "0")
    #     websocket.state.auth_token = websocket.headers.get("X-User-Token")
    
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                message_type = message.get("type")
                
                if message_type == "subscribe":
                    task_id_str = message.get("task_id")
                    if not task_id_str:
                        await websocket.send_text(
                            json.dumps({"error": "Missing task_id in subscribe message"})
                        )
                        continue
                    
                    if task_id_str.lower() == "all":
                        success = await websocket_manager.subscribe(websocket, None)
                        response = {"success": success, "type": "subscribe_response", "task_id": "all"}
                        await websocket.send_text(json.dumps(response))
                    else:
                        try:
                            task_id = uuid.UUID(task_id_str)
                            success = await websocket_manager.subscribe(websocket, task_id)
                            response = {"success": success, "type": "subscribe_response", "task_id": task_id_str}
                            await websocket.send_text(json.dumps(response))
                        except ValueError:
                            await websocket.send_text(
                                json.dumps({"error": "Invalid task_id format"})
                            )
                elif message_type == "unsubscribe":
                    task_id_str = message.get("task_id")
                    if not task_id_str:
                        await websocket.send_text(
                            json.dumps({"error": "Missing task_id in unsubscribe message"})
                        )
                        continue
                    
                    if task_id_str.lower() == "all":
                        success = await websocket_manager.unsubscribe(websocket, None)
                        response = {"success": success, "type": "unsubscribe_response", "task_id": "all"}
                        await websocket.send_text(json.dumps(response))
                    else:
                        try:
                            task_id = uuid.UUID(task_id_str)
                            success = await websocket_manager.unsubscribe(websocket, task_id)
                            response = {"success": success, "type": "unsubscribe_response", "task_id": task_id_str}
                            await websocket.send_text(json.dumps(response))
                        except ValueError:
                            await websocket.send_text(
                                json.dumps({"error": "Invalid task_id format"})
                            )
                else:
                    await websocket.send_text(
                        json.dumps({"error": f"Unknown message type: {message_type}"})
                    )
            except json.JSONDecodeError:
                logger.error(f"收到无效JSON消息: {data}")
                await websocket.send_text(
                    json.dumps({"error": "Invalid JSON format"})
                )
    except WebSocketDisconnect:
        await websocket_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"SDK WebSocket连接处理异常: {e}")
        await websocket_manager.disconnect(websocket)

