reads = 0
writes = 0
history = []

def contar_read():
    global reads
    reads += 1


def contar_write():
    global writes
    writes += 1

def get_counts():
    return {
        "reads": reads,
        "writes": writes
    }

def reset_counts():
    global reads, writes
    history.append((reads, writes))
    r = reads
    w = writes
    reads = 0
    writes = 0
    return r, w