def decode_tau(bits):
    unit = int(bits[:3], 2)
    value = int(bits[3:], 2)

    tau_units = {
        0b000: 10 * 60,        # 10 minutes
        0b001: 60 * 60,        # 1 hour
        0b010: 10 * 60 * 60,   # 10 hours
        0b011: 2,              # 2 seconds
        0b100: 30,             # 30 seconds
        0b101: 60,             # 1 minute
        0b110: 320 * 60 * 60   # 320 hours
    }

    if unit not in tau_units:
        return None

    return value * tau_units[unit]


def decode_active_time(bits):
    unit = int(bits[:3], 2)
    value = int(bits[3:], 2)

    active_units = {
        0b000: 2,          # 2 seconds
        0b001: 60,         # 1 minute
        0b010: 6 * 60,     # decihours (6 minutes)
    }

    # 111 means deactivated
    if unit == 0b111:
        return 0

    if unit not in active_units:
        return None

    return value * active_units[unit]


def parse_cpsms(resp):
    import re

    match = re.search(r'"(\d{8})","(\d{8})"', resp)

    if not match:
        return None

    tau_bits = match.group(1)
    active_bits = match.group(2)

    tau_seconds = decode_tau(tau_bits)
    active_seconds = decode_active_time(active_bits)

    return tau_seconds, active_seconds


# Example:
'''resp = '+CPSMS: 1,,,"00111000","00001111"'

tau, active = parse_cpsms(resp)

print("TAU:", tau, "seconds")
print("Active Time:", active, "seconds")
'''
