import asyncio
from protocol import parse_command

# This dictionary is our entire database, held in memory.
# Keys and values are both strings, for now.
store = {}

def handle_command(command):
    if command is None or len(command) == 0:
        return b"-ERR empty command\r\n"

    name = command[0].upper()

    if name == "PING":
        return b"+PONG\r\n"

    elif name == "ECHO":
        message = command[1]
        return f"${len(message)}\r\n{message}\r\n".encode()

    elif name == "SET":
        # SET key value  ->  store the pair, reply +OK
        key = command[1]
        value = command[2]
        store[key] = value
        return b"+OK\r\n"

    elif name == "GET":
        # GET key  ->  return the value, or null if missing
        key = command[1]
        if key in store:
            value = store[key]
            return f"${len(value)}\r\n{value}\r\n".encode()
        else:
            return b"$-1\r\n"  # RESP null: "this key does not exist"

    elif name == "DEL":
        # DEL key [key ...]  ->  delete keys, reply count of how many existed
        deleted = 0
        for key in command[1:]:
            if key in store:
                del store[key]
                deleted += 1
        return f":{deleted}\r\n".encode()

    elif name == "EXISTS":
        # EXISTS key [key ...]  ->  reply count of how many exist
        count = 0
        for key in command[1:]:
            if key in store:
                count += 1
        return f":{count}\r\n".encode()

    else:
        return f"-ERR unknown command '{command[0]}'\r\n".encode()



async def handle_client(reader, writer):
    addr = writer.get_extra_info("peername")
    print(f"New connection from {addr}")

    try:
        while True:
            data = await reader.read(1024)
            if not data:
                print(f"Connection closed by {addr}")
                break

            command = parse_command(data)
            print(f"Parsed command: {command}")

            response = handle_command(command)
            writer.write(response)
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