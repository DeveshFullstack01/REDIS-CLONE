import asyncio

async def handle_client(reader, writer):
    addr = writer.get_extra_info("peername")
    print(f"New connection from {addr}")

    try:
        while True:
            data = await reader.read(1024)
            if not data:
                print(f"Connection closed by {addr}")
                break

            print(f"Received raw bytes: {data!r}")

            writer.write(b"+PONG\r\n")
            await writer.drain()
    except (ConnectionResetError, ConnectionAbortedError):
        print(f"Connection reset by {addr}")
    finally:
        try:
            writer.close()
            await writer.wait_closed()
        except (ConnectionResetError, ConnectionAbortedError, OSError):
            pass



async def main():
    server = await asyncio.start_server(handle_client, "127.0.0.1", 6380)
    print("Server listening on 127.0.0.1:6380")
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())