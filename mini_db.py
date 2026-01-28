import signal
import socket
import sys
import threading

db = {}  # in-memory key-value 'database'


def signal_handler(sig, frame):
    # save_db()
    sys.exit(0)


def start_server(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", port))
        s.listen()
        print(f"Ready\n\n")

        while True:
            conn, addr = s.accept()
            # instead of multiplexing, ie. select(), use threading instead
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.start()


def handle_client(conn, addr):
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break

            msg = data.decode("utf-8").strip().split()  # returns a list of str
            if not msg:
                continue

            # Assume at least <cmd> and <key> to be present
            # If cmd == POST, then assume <val> to be present as well
            cmd = msg[0].upper()
            # RHS is conditional expr: v1, if <condition> True, else v2
            key = msg[1] if len(msg) > 1 else None
            val = msg[2] if len(msg) > 2 else None

            # print(f"{cmd} {key} {val}") # sanity check

            if cmd == "GET":
                mode = 1
            elif cmd == "POST":
                mode = 2
            elif cmd == "DELETE":
                mode = 3
            else:
                mode = 4

                # separate identifying the 'cmd' (above), from each cmd's implementation (below)

            # NOTE. "match" is only available v3.10 & later
            match mode:
                case 1:
                    if key and key in db:
                        response = f"0 {db[key]}\n"
                    else:
                        response = "1\n"
                case 2:
                    if key and val:
                        db[key] = val
                        # save_db()
                        response = "0\n"
                case 3:
                    if key and key in db:
                        del db[key]
                        response = "0\n"
                    else:
                        response = "1\n"
                case 4:
                    response = "2\n"  # default response, for invalid/unhandled input

            conn.sendall(response.encode("utf-8"))  # send feedback back to client


if __name__ == "__main__":
    if len(sys.argv) != 2:  # python3 mini_db.py <port>
        sys.exit(1)

    signal.signal(signal.SIGINT, signal_handler)

    port = int(sys.argv[1])
    start_server(port)
