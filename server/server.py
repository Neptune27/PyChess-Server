import asyncio
import uuid
from asyncio import StreamReader, StreamWriter
from random import randint

rooms = {
}


async def handle_room(reader, writer):
    pass


async def handle_client(reader: StreamReader, writer: StreamWriter):
    uid = uuid.uuid4()
    client_info = {
        "uid": uid,
        "writer": writer,
        "role": "p"
    }

    room_id = -1
    while True:
        request = (await reader.read(1024)).decode('utf8')
        if request == 'quit':
            break
        tokens = request.split("|")
        if tokens[0] == "join":
            rid = tokens[1]

            if room_id in rooms:
                rooms[room_id].remove(client_info)

            room_id = int(rid)
            if room_id not in rooms:
                rooms[room_id] = []

            rooms[room_id].append(client_info)
            print(f"Rooms: {rooms}")
            await send_to_other(uid, room_id, f"join|{client_info['role']}")
        else:
            await send_to_other(uid, room_id, request)

    rooms[room_id].remove(writer)
    writer.close()


async def send_to_other(uid, room_id, message):
    for client_info in rooms[room_id]:
        if client_info['uid'] == uid:
            continue
        sender = client_info["writer"]
        sender.write(message.encode('utf8'))
        await sender.drain()


async def run_server():
    server = await asyncio.start_server(handle_client, '0.0.0.0', 9999)
    async with server:
        await server.serve_forever()


asyncio.run(run_server())
