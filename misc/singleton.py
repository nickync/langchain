class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        print(f"Calling __call__ for {cls}")
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class A(metaclass=SingletonMeta):
    pass

class B(metaclass=SingletonMeta):
    pass

a = A()
b = B()

# print(id(a))
# print(id(b))


import threading
import time

class Singleton:
    _instance = None
    _lock = threading.Lock()  # 类级锁，保证线程安全

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:  # 第一次检查（提高性能）
            with cls._lock:
                #time.sleep(1) # this introduces race condition and singleton fails
                if cls._instance is None:  # 第二次检查（防止竞争）
                    cls._instance = super().__new__(cls)
        return cls._instance


# 测试
def test_singleton():
    s = Singleton()
    print(f"Instance ID: {id(s)}")

threads = [threading.Thread(target=test_singleton) for _ in range(5)]
for t in threads:
    t.start()
for t in threads:
    t.join()


def remove_dul(ls):
    res = []
    for i in ls:
        if i not in res:
            res.append(i)
    return res

print(remove_dul([3,3,2,6,1,1,6,2]))
