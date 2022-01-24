import random


# If n is prime, then always returns true,
# If n is composite than returns false with
# high probability Higher value of k increases
# probability of correct result
def prime_test(N, k):
    # This is main function, that is connected to the Test button. You don't need to touch it.
    return fermat(N, k), miller_rabin(N, k)


def mod_exp(x, y, N):
    if y == 0: return 1;
    z = mod_exp(x, y // 2, N);
    # y is an even number -> N = z^2
    if y % 2 == 0:
        return z ** 2 % N
    else:
        return x * (z ** 2) % N


# Time complexity of n^2 with integer k which is size n bits
def fprobability(k):
    # You will need to implement this function and change the return value.   
    return 1 - (1 / 2 ** k)


# Time complexity of n^2 with integer k which is size n bits
def mprobability(k):
    # You will need to implement this function and change the return value.   
    return 1 - (4 ** -k)


# Time complexity of k*n^3 because we call mod_exp (which is order n^3) k times
def fermat(N, k):
    # if N is an even number return composite
    if (N % 2) == 0:
        return 'composite'

    # Run through the number of tests
    for i in range(0, k):
        ran = random.randint(1, N - 1)
        # If the result of the modular exponentiation is not 1 we know the number is composite
        if mod_exp(ran, N - 1, N) != 1:
            return 'composite'
        # reduce the value of k for every loop
        k -= 1
    return 'prime'


def miller_helper(base, power, N):
    result = mod_exp(base, power, N)
    if result % 2 == 0:
        return "composite"
    if result == (N - 1):
        return "prime"
    elif result != 1:
        return miller_helper(result, power // 2, N)


# Time complexity of k*n^2 because we call mod_exp (which is order n^3) k times.
def miller_rabin(N, k):
    for i in range(0, k):
        # If the exponent is odd we want to move on to test the next base
        if N % 2 == 0:
            return "composite"
        ran = random.randint(2, N - 2)
        b = mod_exp(ran, N - 1, N)
        if b == 1 or b == -1:
            return "prime"
        # if the result of mod_exp is not one and also not N - 1 -> test as N-1
        else:
            return miller_helper(b, N - 1, N)
        # reduce the value of k for every loop
        k -= 1
