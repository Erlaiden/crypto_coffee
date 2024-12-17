import os
import asyncio
import websockets

async def handler(websocket, path):
    async for message in websocket:
        print(f"Received message: {message}")
        await websocket.send(f"Echo: {message}")

async def main():
    port = int(os.environ.get("PORT", 8765))
    async with websockets.serve(handler, "0.0.0.0", port):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
