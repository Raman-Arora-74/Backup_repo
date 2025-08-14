import asyncio

async def pizza_order():
    print("Order the Pizza")
    await asyncio.sleep(5)
    print("Order is made but not delivered")
    await asyncio.sleep(2)
    print("Pizza Deliverd")
async def party_room():
    print("Book a room")
    await asyncio.sleep(4)
    print("Cleaning done")
    await asyncio.sleep(3)
    print("Done party room")
async def main():
    print("Today is party")
    print("Raman Order pizza and I do some party room settings !")
    task1 = asyncio.create_task(pizza_order())
    task2 = asyncio.create_task(party_room())
    await asyncio.sleep(5)
    print("People is outside")
    await asyncio.sleep(2)
    print("People are in the room of party")
    await task1 
    await task2 
    print("party done")

asyncio.run(main())