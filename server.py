import socket
import json
import os

SERVER_IP = "127.0.0.1"
SERVER_PORT = 65444

IMAGE_CHUNK_SIZE = 1024

IMAGE_BUFFER_SIZE = IMAGE_CHUNK_SIZE * 2

INFO_BUFFER_SIZE = 1024

SAVE_DIR = "images"
os.makedirs(SAVE_DIR, exist_ok=True)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((SERVER_IP, SERVER_PORT))

print(f"UDP server běží")

receiving_image = False
image_file = None
expected_size = 0
received_size = 0
image_path = ""



while True:

    #v případě posílání obrázku
    if receiving_image:
        data, client_address = sock.recvfrom(IMAGE_BUFFER_SIZE)

        hex_text = data.decode("ascii")
        image_bytes = bytes.fromhex(hex_text)

        image_file.write(image_bytes)
        received_size += len(image_bytes)

        print(
            f"Přijata část obrázku: {len(image_bytes)} B, "
            f"celkem {received_size}/{expected_size} B"
        )

        # Po každé části obrázku odpověď OK
        sock.sendto(b"OK", client_address)

        if received_size >= expected_size:
            image_file.close()
            image_file = None
            receiving_image = False

            print("\nObrázek přijat")
        continue

    data, client_address = sock.recvfrom(INFO_BUFFER_SIZE)

    text = data.decode("ascii").strip()

    try:
        message = json.loads(text)
    except json.JSONDecodeError:
        # Pokud to není JSON
        print("\nTelemetrie přijata")
        continue

    if message.get("type") == "image_info":

        image_id = message.get("id")
        expected_size = int(message.get("size", 0))

        image_id = str(image_id)

        image_name = f"{image_id}.jpg"
        image_path = os.path.join(SAVE_DIR, image_name)

        image_file = open(image_path, "wb")
        received_size = 0
        receiving_image = True

        print("\nZAČÁTEK PŘÍJMU OBRÁZKU")
        print("Očekávání obrázku\n")


    else:
        print("\nTELEMETRIE")
        print(f"Od: {client_address}")
        print(message)
        print()
