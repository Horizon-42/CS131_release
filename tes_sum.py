def isPalindrome(x: int):
    if x < 0:
        return False
    else:
        if (x < 10):
            return True
        digits = []
        while True:
            digits.append(x % 10)
            x = x//10
            if (x == 0):
                break

        for i in range(len(digits)//2):
            if (digits[i] != digits[len(digits)-1-i]):
                return False
        return True


if __name__ == "__main__":
    print(isPalindrome(10))
