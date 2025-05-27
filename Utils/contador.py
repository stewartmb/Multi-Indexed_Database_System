reads = 0
writes = 0


def contar_read():
    print("reee")
    global reads
    reads += 1
    print("Total reads:", reads)


def contar_write():
    print("wiii")
    global writes
    writes += 1

def get_counts():
    return {
        "reads": reads,
        "writes": writes
    }