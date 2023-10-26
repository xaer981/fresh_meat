def is_num_lt_max(val, max):
    if not val:

        return True

    try:
        val = int(val)

    except ValueError:

        return False

    if val > max:

        return False

    return True
