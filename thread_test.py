import multiprocessing as mp
import time


class Worker(mp.Process):
    def __init__(self, len: int, queue: mp.Queue) -> None:
        super().__init__()
        self.len = len
        self.queue = queue
        self.start()

    def run(self) -> None:
        arr = []
        for i in range(self.len):
            arr.append(i)
            self.queue.put(arr)
            time.sleep(2)


q = mp.Queue()
w = Worker(10, q)

frame = 0
FPS = 30
sec = 0
while 1:
    frame += 1
    print(f"{frame=}", end="\r")
    if frame == FPS / 2:
        print("Get data")
        if not q.empty():
            print(f"{q.get(block=False)=}")
        print("Done")

    time.sleep(1 / FPS)
    if frame == FPS:
        frame = 0
        sec += 1
        if sec == 5:
            w.terminate()
            break
