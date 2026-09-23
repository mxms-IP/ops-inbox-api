import httpx, time, threading

def hit(label):
    start = time.time()
    print(f"{label}: starting at {start:.2f}")
    r = httpx.post(
        "http://127.0.0.1:8000/api/v1/inbox/webhook",
        json={"sender": "a@b.com", "subject": "test", "body": "test"},
        timeout=30.0,
    )
    end = time.time()
    print(f"{label}: started {start:.2f}  finished {end:.2f}  took {end - start:.2f}s -> {r.json()}")

t1 = threading.Thread(target=hit, args=("req1",))
t2 = threading.Thread(target=hit, args=("req2",))
t1.start(); t2.start()
t1.join(); t2.join()