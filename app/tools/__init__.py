import random


def get_random(n, total):
    box = [i for i in range(total)]
    out = []
    for i in range(n):
        index = random.randint(0, total - i - 1)
        out.append(box[index])
        box[index], box[total - i - 1] = box[total - i - 1], box[index]
    return out


if __name__ == "__main__":
    for i in get_random(10, 100):
        print(i,end=' ')
