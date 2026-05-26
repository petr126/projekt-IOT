def decode_timer(bits):
    unit = int(bits[:3], 2)
    value = int(bits[3:], 2)

    units = {
        0b000: 2,          # 2s
        0b001: 60,         # 1min
        0b010: 3600,       # 1h
        0b011: 10*60,      # 10min
        0b100: 30,         # 30s
        0b101: 10*3600,    # 10h
        0b110: 320*3600,   # 320h
    }

    if unit not in units:
        return None

    return value * units[unit]

def parse_cpsms(resp):
    import re
    match = re.search(r'"(\d{8})","(\d{8})"', resp)
    if not match:
        return None

    tau_bits = match.group(1)
    at_bits = match.group(2)

    tau_seconds = decode_timer(tau_bits)
    active_seconds = decode_timer(at_bits)

    return tau_seconds, active_seconds

