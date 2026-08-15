import asyncio
from protocol import parse_command
from datastore import DataStore

# Create the single database instance shared by all connections.
db = DataStore()


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
        key = command[1]
        value = command[2]
        db.set(key, value)
        # Optional: SET key value EX seconds
        if len(command) >= 5 and command[3].upper() == "EX":
            seconds = int(command[4])
            db.set_expiry(key, seconds)
        return b"+OK\r\n"

    elif name == "GET":
        value = db.get(key := command[1])
        if value is None:
            return b"$-1\r\n"
        return f"${len(value)}\r\n{value}\r\n".encode()

    elif name == "DEL":
        deleted = 0
        for key in command[1:]:
            if db.delete(key):
                deleted += 1
        return f":{deleted}\r\n".encode()

    elif name == "EXISTS":
        count = 0
        for key in command[1:]:
            if db.exists(key):
                count += 1
        return f":{count}\r\n".encode()

    elif name == "EXPIRE":
        key = command[1]
        seconds = int(command[2])
        if db.set_expiry(key, seconds):
            return b":1\r\n"
        return b":0\r\n"

    elif name == "TTL":
        key = command[1]
        return f":{db.ttl(key)}\r\n".encode()

    elif name == "PERSIST":
        key = command[1]
        if db.persist(key):
            return b":1\r\n"
        return b":0\r\n"

    elif name == "DBSIZE":
        # How many keys are physically in the store (real Redis has this too).
        return f":{len(db._data)}\r\n".encode()

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


async def expiry_sweeper():
    """
    Background task: periodically run active expiration so that expired
    keys nobody reads are still cleaned up. Runs for the life of the server.
    """
    while True:
        # Keep sweeping while lots of keys are expiring, then rest.
        while db.active_expire_cycle() > 0.25:
            pass
        await asyncio.sleep(0.1)  # 100ms between cycles


async def main():
    server = await asyncio.start_server(handle_client, "127.0.0.1", 6380)
    print("Server listening on 127.0.0.1:6380")

    # Launch the background expiry sweeper.
    asyncio.create_task(expiry_sweeper())

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())