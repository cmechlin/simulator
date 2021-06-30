import argparse
import asyncio
import mmap
from os import access
import EpromReader as ER
from Eprom import Eprom
from Controller import Controller

VITAL_LOOP = 250
NONVITAL_LOOP = 100

async def VitalALoop():
    binary = ER.EpromReader()
    vLoopTime = VITAL_LOOP * 0.001
    while True:
        for equation in binary.equations:
            equation.eval()
        await asyncio.sleep(vLoopTime)
        # log("vital A loop")


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


def simulator():
    loop = asyncio.get_event_loop()

    try:
        # loop.run_until_complete(myCoroutine())
        asyncio.ensure_future(VitalALoop())
        # asyncio.ensure_future(VitalBLoop())
        # asyncio.ensure_future(NonVitalLoop())
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        print("Closing Loop")
        loop.close()


def main():
    parser = argparse.ArgumentParser(description="Load the Binary File")
    parser.add_argument("filepath", action="store", type=str, help="the path to the binary")
    args = parser.parse_args()
    filepath = args.filepath

    # load the file
    print(filepath)
    with open(args.filepath, "rb") as f:
        eprom_bytes = mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_READ)

    eprom = Eprom(eprom_bytes)

    # Create the controller
    controller = Controller()
    controller.run(eprom)



    # simulator()
    # print("here")

    # print(binary.statuses[37].getState())
    # binary.statuses[37].setState(True)
    # print(binary.statuses[37].getState())

    # # print(f"{self.type}: Status {self.name} state is {self.state}")
    # print(binary.statuses[44].getState())
    # # binary.statuses[44].setState(True)
    # print(binary.statuses[44].getState())
    # pass


if __name__ == "__main__":
    main()