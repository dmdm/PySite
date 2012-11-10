def one():
    try:
        12 / 0
    except Exception as e:
        print("ERROR:", e)
        raise
    finally:
        print("Finally reached")


class Ex(Exception):
    pass

class Ex2(Exception):
    pass

def open_fd():
    print("FD opened")

def open_dst_fd():
    #raise Ex("ERROR on open DST FD")
    print("DST FD opened")

def copy():
    raise Ex("ERROR on copy")
    print("copy")

def close_dst_fd():
    print("DST FD closed")

def close_fd():
    print("FD closed")

def two():
    open_fd()
    try:
        open_dst_fd()
        try:
            copy()
        except Ex as e:
            print("INNER ERROR:", e)
            raise Ex2(e)
        finally:
            close_dst_fd()
    except Ex as e:
        print("OUTER ERROR:", e)
        raise Ex2(e)
    finally:
        close_fd()


def three():
    try:
        print("a")
        raise Ex("exexex")
        #raise Exception("general fault")
    except Ex as e:
        print("ERROR Ex:", str(e))
        raise # If I reraise exc here, will it be caught by next except clause?
    except Exception as e:
        print("General exception:", e)

#one()
#two()
three()

