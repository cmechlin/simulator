import asyncio

VITAL_LOOP = 250
NONVITAL_LOOP = 100


async def VitalALoop():
    vLoopTime = VITAL_LOOP * 0.001
    while True:
        await asyncio.sleep(vLoopTime)
        log("vital A loop")


async def VitalBLoop():
    vLoopTime = VITAL_LOOP * 0.001
    while True:
        await asyncio.sleep(vLoopTime)
        log("vital B loop")


async def NonVitalLoop():
    nvLoopTime = NONVITAL_LOOP * 0.001
    while True:
        await asyncio.sleep(nvLoopTime)
        log("nonvital loop")

def log(msg):
  print(msg)

def main():
    loop = asyncio.get_event_loop()

    try:
        # loop.run_until_complete(myCoroutine())
        asyncio.ensure_future(VitalALoop())
        asyncio.ensure_future(VitalBLoop())
        asyncio.ensure_future(NonVitalLoop())
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        print("Closing Loop")
        loop.close()

    if __name__ == "__main__":
        main()
