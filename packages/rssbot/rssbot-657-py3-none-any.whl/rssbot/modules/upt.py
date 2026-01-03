# This file is placed in the Public Domain.


import time


from rssbot.defines import elapsed


STARTTIME = time.time()


def upt(event):
    event.reply(elapsed(time.time()-STARTTIME))
