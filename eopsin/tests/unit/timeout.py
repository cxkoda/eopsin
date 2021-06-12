import multiprocessing as mp


class TimeoutException(Exception):
    pass


class InterruptableProcess(mp.Process):
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self._func = func
        self._args = args
        self._kwargs = kwargs
        self._result = None

    def run(self):
        self._result = self._func(*self._args, **self._kwargs)

    @property
    def result(self):
        return self._result


class timeout:
    def __init__(self, seconds=10):
        self._sec = seconds

    def __call__(self, f):
        def wrapped_f(*args, **kwargs):
            it = InterruptableProcess(f, *args, **kwargs)
            it.start()
            it.join(self._sec)
            if not it.is_alive():
                return it.result
            else:
                it.terminate()
                raise TimeoutException(f'Execution time of {self._sec} seconds exceeded')

        return wrapped_f


if __name__ == '__main__':
    import time


    @timeout(2)
    def f(seconds):
        time.sleep(seconds)
        return 'finished'


    print(f(1))
