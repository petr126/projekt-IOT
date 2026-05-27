import socket
import json
import os
import time

SERVER_IP = "0.0.0.0"
SERVER_PORT = 7001

IMAGE_CHUNK_SIZE = 512
IMAGE_BUFFER_SIZE = IMAGE_CHUNK_SIZE * 2

INFO_BUFFER_SIZE = 512
RECEIVE_TIMEOUT = 10

SAVE_DIR = "images"
os.makedirs(SAVE_DIR, exist_ok=True)


def run_server():
    receiving_image = False
    image_file = None
    expected_size = 0
    received_size = 0
    image_path = ""

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((SERVER_IP, SERVER_PORT))
    sock.settimeout(RECEIVE_TIMEOUT)

    print("UDP server běží")

    def reset_server_state(delete_partial_file=True):
        nonlocal receiving_image
        nonlocal image_file
        nonlocal expected_size
        nonlocal received_size
        nonlocal image_path

        if image_file is not None:
            image_file.close()
            image_file = None

        if delete_partial_file and image_path != "" and os.path.exists(image_path):
            os.remove(image_path)

        receiving_image = False
        expected_size = 0
        received_size = 0
        image_path = ""

        print("\nPříjem obrázku byl přerušen")
        print("Server je vrácen do původního stavu\n")

    try:
        while True:

            if receiving_image:
                try:
                    data, client_address = sock.recvfrom(IMAGE_BUFFER_SIZE)

                    hex_text = data.decode("ascii").strip()
                    image_bytes = bytes.fromhex(hex_text)

                    image_file.write(image_bytes)
                    received_size += len(image_bytes)

                    print(
                        f"Přijata část obrázku: {len(data)} B, "
                        f"celkem {received_size}/{expected_size} B"
                    )

                    sock.sendto(b"OK", client_address)

                    if received_size >= expected_size:
                        image_file.close()
                        image_file = None
                        receiving_image = False

                        expected_size = 0
                        received_size = 0
                        image_path = ""

                        print("\nObrázek přijat\n")

                except socket.timeout:
                    reset_server_state(delete_partial_file=True)

                except Exception as e:
                    print(f"\nChyba při příjmu obrázku: {e}")
                    reset_server_state(delete_partial_file=True)

                continue

            try:
                data, client_address = sock.recvfrom(INFO_BUFFER_SIZE)

            except socket.timeout:
                continue

            text = data.decode("ascii").strip()

            try:
                message = json.loads(text)

            except json.JSONDecodeError:
                print("\nTelemetrie přijata")
                continue

            if message.get("type") == "image_info":

                image_id = message.get("id")
                expected_size = int(message.get("size", 0))

                image_name = f"{image_id}.jpg"
                image_path = os.path.join(SAVE_DIR, image_name)

                image_file = open(image_path, "wb")
                received_size = 0
                receiving_image = True

                print("\nZAČÁTEK PŘÍJMU OBRÁZKU")
                print(f"ID obrázku: {image_id}")
                print(f"Očekávaná velikost: {expected_size} B\n")

            else:
                print("\nTELEMETRIE")
                print(f"Od: {client_address}")
                print(message)
                print()

    finally:
        if image_file is not None:
            image_file.close()

        sock.close()


while True:
    try:
        run_server()

    except KeyboardInterrupt:
        print("\nServer byl ručně ukončen")
        break

    except Exception as e:
        print(f"\nSERVER SPADL KVŮLI CHYBĚ: {e}")
        print("Server se za 2 sekundy znovu spustí...\n")
        time.sleep(2)
