
def suite(n, b=1):
    for _ in range(n):
        arr = [c for c in str(b)]
        r = [1, arr[0]]
        for digit in arr[1:]:
            if r[-1] == digit:
                r[-2] += 1
            else:
                r.extend([1, digit])
        b = int(''.join([str(e) for e in r]))
    return b
