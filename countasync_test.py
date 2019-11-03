#!/usr/bin/env python3
# countasync.py
#runs in python console, not IPython

import asyncio

async def count():
    print("One")
    await asyncio.sleep(1)
    print("Two")

async def main():
    await asyncio.gather(count(), count(), count())

if __name__ == "__main__":
    import time
    s = time.perf_counter()
    try:
#        asyncio.run(main())
        asyncio.get_event_loop().run_until_complete((main()))#works too
    except:
        raise
    elapsed = time.perf_counter() - s
    print(f"{__file__} executed in {elapsed:0.2f} seconds.")