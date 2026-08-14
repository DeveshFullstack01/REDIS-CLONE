def parse_command(data):
    """
    Take raw RESP bytes from the client and return a list of strings.
    Example: b'*1\r\n$4\r\nping\r\n'  ->  ['ping']
    """
    # Split the incoming bytes on \r\n into separate lines.
    parts = data.split(b"\r\n")

    # The first line tells us how many elements are in the array.
    # It looks like b'*1', so we drop the '*' and read the number.
    if not parts or not parts[0].startswith(b"*"):
        return None

    num_elements = int(parts[0][1:])

    result = []
    index = 1  # start reading after the '*N' line

    for _ in range(num_elements):
        # parts[index] is the length marker like b'$4' -- we can skip it,
        # because parts[index + 1] is the actual string.
        value = parts[index + 1]
        result.append(value.decode())
        index += 2  # move past both the '$N' line and the value line

    return result