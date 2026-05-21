import socket
import json
import os
import time
import random

SERVER_IP = "147.229.148.105"
SERVER_PORT = 7001

IMAGE_CHUNK_SIZE = 512
IMAGE_PATH = "images/obr.jpg"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(5)

server_address = (SERVER_IP, SERVER_PORT)


def send_telemetry():
    message = {
        "type": "telemetry",
        "device_id": "fotopast_01",
        "timestamp": int(time.time()),
        "battery": random.randint(60, 100),
        "signal": random.randint(-110, -70),
        "temperature": round(random.uniform(15.0, 30.0), 1),
        "status": "OK"
    }

    text = json.dumps(message)

    # Telemetrie je text, proto se posílá jako ASCII
    sock.sendto(text.encode("ascii"), server_address)

    print("\nTelemetrie odeslána:")
    print(message)


def send_image(image_path):
    if not os.path.exists(image_path):
        print("\nSoubor obrázku neexistuje")
        return

    image_size = os.path.getsize(image_path)
    image_id = int(time.time())

    info_message = {
        "type": "image_info",
        "id": image_id,
        "size": image_size,
        "encoding": "hex"
    }

    # První se pošle JSON informace o obrázku jako ASCII
    sock.sendto(json.dumps(info_message).encode("ascii"), server_address)

    print("\nOdeslána informace o obrázku")
    print(f"ID obrázku: {image_id}")
    print(f"Velikost: {image_size} B")
    print("Kódování: HEX")

    time.sleep(0.2)

    sent_size = 0

    with open(image_path, "rb") as image_file:
        while True:
            image_bytes = image_file.read(IMAGE_CHUNK_SIZE)

            if not image_bytes:
                break

            # Obrázek se převede na HEX text
            hex_text = image_bytes.hex()

            # HEX text se odešle jako ASCII
            sock.sendto(hex_text.encode("ascii"), server_address)

            try:
                response, _ = sock.recvfrom(512)

                if response == b"OK":
                    sent_size += len(image_bytes)

                    print(
                        f"Odeslána část obrázku: {len(image_bytes)} B, "
                        f"HEX velikost: {len(hex_text)} znaků, "
                        f"celkem {sent_size}/{image_size} B"
                    )

            except socket.timeout:
                print("\nServer neodpověděl, odesílání obrázku přerušeno")
                return

    print("\nObrázek odeslán")

while True:
    print("\nVyber možnost:")
    print("1 - Odeslat telemetrii")
    print("2 - Odeslat obrázek")
    print("0 - Konec")

    choice = input("Volba: ")

    if choice == "1":
        send_telemetry()

    elif choice == "2":
        send_image(IMAGE_PATH)

    elif choice == "0":
        print("Konec klienta")
        break

    else:
        print("Neplatná volba")