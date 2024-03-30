import asyncio
import json
import uuid
from asyncio import StreamReader, StreamWriter
from random import randint

rooms = []
undo_request = {}
tie_request = {}


async def handle_client(reader: StreamReader, writer: StreamWriter):
    uid = uuid.uuid4()
    client_info = {
        "uid": uid,
        "writer": writer,
        "role": "p",
        "play_as": "w",
        "can_undo": True,
        "can_tie": True,
        "room_id": -1

    }
    counter = 0

    while True:
        try:
            requests = (await reader.read(1024)).decode('utf8')
            print(f"Requests: {requests}")
            print(f"Requests Length: {len(requests)}")
            if len(requests) == 0:
                counter += 1
            if counter == 20:
                raise ConnectionResetError("")

            for request in requests.split("\\"):
                await handle_request(request, client_info)
        except ConnectionResetError:
            break

    room_id = client_info["room_id"]
    await send_to_other(uid, room_id, f"quit|{client_info['role']}")

    if len(rooms) > client_info['room_id'] - 1 >= 0:
        rooms[client_info['room_id'] - 1].remove(client_info)
        if len(rooms[room_id - 1]) == 0:
            rooms.pop(room_id - 1)
    print(rooms)

    writer.close()


def clean_up_rooms():
    global rooms
    new_room = [room for room in rooms if len(room) > 0]
    rooms = new_room
    for i, room in enumerate(rooms):
        for client_info in room:
            client_info["room_id"] = i + 1


async def handle_request(request: str, client_info: dict):
    if request == 'quit':
        raise ConnectionResetError()

    tokens = request.split("|")
    room_id, uid = client_info["room_id"], client_info["uid"]
    match tokens[0]:
        case "join":
            clean_up_rooms()

            rid = tokens[1]

            if len(rooms) >= room_id >= 0:
                rooms[room_id - 1].remove(client_info)

            client_info["room_id"] = int(rid)
            room_id = client_info["room_id"]

            if len(rooms) != room_id:
                rooms.append([])
                client_info["room_id"] = len(rooms)
                room_id = client_info["room_id"]

            rooms[room_id - 1].append(client_info)
            if len(rooms[room_id - 1]) > 2:
                client_info["role"] = "s"
            print(f"Rooms: {rooms}")

            undo_request[room_id] = 0
            await send_to_other(uid, room_id, f"join|{client_info['role']}")
        case "rooms":
            clean_up_rooms()

            room_infos = [[i, len(room)] for i, room in enumerate(rooms)]
            client_info["writer"].write(f"room_info|{json.dumps(room_infos)}".encode('utf8'))
        case "fen":
            is_white = json.loads(tokens[2])
            client_info["play_as"] = "w" if is_white else 'b'
            await send_to_other(uid, room_id, request)
        case "command":
            if tokens[1] == "/undo":
                await handle_command_undo(client_info, room_id)
            if tokens[1] == "/tie":
                await handle_command_tie(client_info, room_id)
            if tokens[1] == "/forfeit":
                await send_to_all(room_id, f"command|forfeit|{client_info['play_as']}")
        case "p":
            if room_id in undo_request and undo_request[room_id] != 0:
                undo_request[room_id] = 0
                await send_to_all(room_id, f"command|undo|d")
            if room_id in tie_request and tie_request[room_id] != 0:
                tie_request[room_id] = 0
                await send_to_all(room_id, f"command|tie|d")
            await send_to_other(uid, room_id, request)
        case _:
            await send_to_other(uid, room_id, request)


async def handle_command_undo(client_info: dict, room_id: int) -> None:
    if client_info["can_undo"] and room_id not in undo_request:
        undo_request[room_id] = 1
    elif client_info["can_undo"]:
        undo_request[room_id] += 1

    client_info["can_undo"] = False
    if undo_request[room_id] > 1:
        await send_to_all(room_id, f"command|undo|a|{client_info['play_as']}")
        undo_request[room_id] = 0

        for client_inf in rooms[room_id - 1]:
            client_inf["can_undo"] = True

    else:
        await send_to_other(client_info["uid"], room_id, f"command|undo|r")
    print(rooms)


async def handle_command_tie(client_info: dict, room_id: int) -> None:
    if client_info["can_tie"] and room_id not in tie_request:
        tie_request[room_id] = 1
    elif client_info["can_tie"]:
        tie_request[room_id] += 1

    client_info["can_tie"] = False
    if tie_request[room_id] > 1:
        await send_to_all(room_id, f"command|tie|a")
        tie_request[room_id] = 0

        for client_inf in rooms[room_id - 1]:
            client_inf["can_tie"] = True

    else:
        await send_to_other(client_info["uid"], room_id, f"command|tie|r")
    print(rooms)


async def send_to_other(uid, room_id, message):
    if room_id < 0:
        return
    for client_info in rooms[room_id - 1]:
        if client_info['uid'] == uid:
            continue
        sender = client_info["writer"]
        await send(sender, message)


async def send_to_all(room_id, message):
    for client_info in rooms[room_id - 1]:
        sender = client_info["writer"]
        await send(sender, message)


async def send(sender, message):
    sender.write(f"{message}\\".encode('utf8'))
    await sender.drain()


async def run_server():
    server = await asyncio.start_server(handle_client, '0.0.0.0', 9999)
    async with server:
        await server.serve_forever()


asyncio.run(run_server())
