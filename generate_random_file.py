
def main():
    import sys
    import random
    import string
    if len(sys.argv) == 2:
        f = open(sys.argv[1], 'w')
        message = ""
        for i in xrange(128):
            message += random.choice(string.letters)
            message += "\n"
        message = message * 10
        f.write(message)
        f.close()

        


if __name__ == '__main__':
    main()
