
def get_contents(fn):
    try:
        with open(fn, 'rb') as fd:
            s = fd.read()
        return s
    except (OSError, IOError) as e:
        print("Caught Exception", type(e), e)


fn = "/tmp/foo"
s = get_contents(fn)
print("Contents:", s)
