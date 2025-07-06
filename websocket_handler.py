import asyncio
import logging

logger = logging.getLogger(__name__)


class WebSocketManager:
    def __init__(self):
        self.clients = set()

    async def register(self, websocket):
        self.clients.add(websocket)

    async def unregister(self, websocket):
        self.clients.discard(websocket)

    async def broadcast(self, message):
        remove = set()
        for client in self.clients:
            try:
                if client.open:
                    await client.send(message)
                    logger.info("Message sent to ws Client")
                else:
                    logger.warning("Unregistering closed wsconn")
                    remove.add(client)
            except Exception:
                logger.warning("Unregistering errored wsconn")
                remove.add(client)
        for client in remove:
            self.clients.discard(client)

    async def handler(self, websocket, path, ctl1, cfg, VERSION):
        await self.register(websocket)
        logger.warning("WebSocket CONNECTION MADE")
        await websocket.send(f"Version : {VERSION}")
        await websocket.send(ctl1.stateMonitor.getDisplayHeaderString())

        try:
            while True:
                try:
                    msg = await asyncio.wait_for(websocket.recv(), timeout=20)
                    logger.warning("WS RX message")
                except asyncio.TimeoutError:
                    try:
                        logger.warning(
                            "No data in 20 secs from client- checking connection"
                        )
                        pong_waiter = await websocket.ping()
                        await asyncio.wait_for(pong_waiter, timeout=10)
                        logger.warning("Ping rxed - client alive")
                    except Exception:
                        logger.warning(
                            "No ping response - Remove dead client websocket"
                        )
                        break
                else:
                    logger.warning("msg RXED from client - still connected do nothing")
        finally:
            await self.unregister(websocket)
            logger.warning("Dropped out of onConnect handler")
