import datetime
import heapq
import types
import time


class Task(object):

    def __init__(self, wait_until, coro):
        self.coro = coro
        self.waiting_until = wait_until

    def __eq__(self, other):
        return self.waiting_until == other.waiting_until

    def __lt__(self, other):
        return self.waiting_until < other.waiting_until


class SleepingLoop(object):

    def __init__(self, *coros):
        self._new = coros
        self._waiting = []

    def run_until_complete(self):

        # Start all the coroutines
        for coro in self._new:
            wait_for = coro.send(None)
            heapq.heappush(self._waiting, Task(wait_for, coro))

        # Keep running until there is no more work to do
        while self._waiting:
            now = datetime.datetime.now()
            task = heapq.heappop(self._waiting)

            if now < task.waiting_until:
                # ahead of schedule
                delta = task.waiting_until - now
                time.sleep(delta.total_seconds())
                now = datetime.datetime.now()

            try:
                #resume coroutine
                wait_until = task.coro.send(now)
                heapq.heappush(self._waiting, Task(wait_until, task.coro))

            except StopIteration:
                # The coroutine is done
                pass


@types.coroutine
def sleep(seconds):
    """ Pause a coroutine for the specified number of seconds"""

    now = datetime.datetime.now()
    wait_until = now + datetime.timedelta(seconds=seconds)
    actual = yield wait_until

    return actual - now

async def countdown(label, lenght, *, delay=0):
    """
    Countdown a launch for `length` seconds, waiting `delay` seconds.
    This is what a user would typically write.
    """

    print(label, 'waiting', delay, 'seconds before starting countdown')
    delta = await sleep(delay)
    print(label, 'starting after waiting', delta)

    while lenght:
        print(label, 'T-minus', lenght)
        waited = await sleep(1)
        lenght -= 1

    print(label, 'lift-off!')


def main():
    loop = SleepingLoop(countdown('A', 5), countdown('B', 3, delay=2), countdown('C', 4, delay=1))

    start = datetime.datetime.now()
    loop.run_until_complete()

    print('Total elapsed time: ', datetime.datetime.now() - start)


if __name__ == '__main__':
    main()
