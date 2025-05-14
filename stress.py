import time
import threading
import hashlib
import os
import sys


def cpu_load(level):
    if level == 1:
        while True:
            pass
    elif level == 2:
        data = b"Hello, World!"
        while True:
            hashlib.sha256(data).hexdigest()
    elif level == 3:
        while True:
            os.system("dd if=/dev/zero of=/dev/null bs=1M count=100")
    elif level == 4:
        while True:
            os.system("dd if=/dev/zero of=/dev/null bs=10M count=100")
    else:
        while True:
            os.system("dd if=/dev/zero of=/dev/null bs=100M count=100")


def main():
    if len(sys.argv) > 1:
        level = int(sys.argv[1])
    else:
        level = 1
    print(f"Running CPU load at level: {level}({os.getpid()})")
    threads: list[threading.Thread] = []
    for i in range(10):
        t = threading.Thread(target=cpu_load, args=(level,))
        t.start()
        threads.append(t)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
        os._exit(0)


if __name__ == "__main__":
    main()
