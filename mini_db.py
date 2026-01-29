import json
import signal
import socket
import sys
import threading

db = {}  # in-memory key-value 'database'
filename = ""

def signal_handler(sig, frame):
    # save_db()
    sys.exit(0)

def load_db(filename):
    try:
        with open(filename, 'r') as f:
            # list comprehension
            db = dict(line.strip().split(' ') for line in f if ' ' in line)
        return db
    except FileNotFoundError:
        print("Expected usage: python3 mini_db.py <port> <db_file>")
        print("Error: <db_file> not found")
        sys.exit(1)

def save_db(filename):
    with open(filename, 'w') as f:
        for key, val in db.items():
            f.write(f"{key} {val}\n")

def start_server(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", port))
        s.listen()
        print(f"Ready\n\n")

        while True:
            conn, addr = s.accept()
            # alternatives to threading? multiplexing with select, asyncio ?
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

            cmd = msg[0].upper()
            # RHS for key & val below, is conditional expr, aka "ternary" 
            # value_1, if <condition> True, else value_2
            key = msg[1] if len(msg) > 1 else None
            val = msg[2] if len(msg) > 2 else None

            # NOTE. cmd is enforced to be UPPERCASE! 
            if cmd == "GET":
                mode = 1
            elif cmd == "POST":
                mode = 2
            elif cmd == "DELETE":
                mode = 3
            elif cmd == "SHOWDB":
                mode = 4
            elif cmd == "CLEARDB"
                mode = 5
            elif cmd == "SAVEDB"
                mode = 6
            else:
                mode = 7

            # separate identifying the 'cmd' (above), 
            # from each cmd's implementation (below)

            # NOTE. "match" is only available v3.10 & later
            match mode:
                case 1: # GET
                    if key and key in db:
                        response = f"0 {db[key]}\n"
                    else:
                        response = "1\n"
                case 2: # POST
                    if key and val:
                        db[key] = val
                        response = "0\n"
                    else:
                        response = "1\n"
                case 3: # DELETE
                    if key and key in db:
                        del db[key]
                        response = "0\n"
                    else:
                        response = "1\n"
                case 4: # SHOWDB
                    print(json.dumps(db, indent=2)) # display at server terminal
                    response = "0\n"
                case 5: # CLEARDB
                    db.clear()
                    response = "0\n"
                case 6: # SAVEDB
                    save_db(filename)
                    response = "0\n"
                case 7:
                    response = "2\n"  # default response, for invalid/unhandled input
            conn.sendall(response.encode("utf-8"))  # send feedback back to client


if __name__ == "__main__":
    if len(sys.argv) != 2:  # python3 mini_db.py <port>
        print("Expected usage: python3 mini_db.py <port> <db_file>")
        sys.exit(1)

    signal.signal(signal.SIGINT, signal_handler)

    port = int(sys.argv[1])
    filename = sys.argv[2]

    db = load_db(filename)
    
    start_server(port)
