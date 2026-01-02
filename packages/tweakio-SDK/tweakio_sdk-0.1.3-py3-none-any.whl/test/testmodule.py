"""
Testing Module for the library
"""
import sys
import os

# Add parent directory to sys.path to find SDK modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio

import BrowserManager as bm
import ChatLoader as chats
import MessageLoader as ml
# import login


async def main():

    """
    Testing Main Method.
    """
    # import directory as dirs
    # d : dict = await dirs.get_all_paths()
    # for k, v in d.items():
    #     print(f"{k}: {v}")
    import tracemalloc
    tracemalloc.start()
    # -----
    b = bm.BrowserManager()
    page = await b.getPage()
    # wp_login = login.WhatsappLogin(page=page, number="63980 14720", country="india")
    # await wp_login.login()
    await page.goto("https://web.whatsapp.com")
    chatObj = chats.ChatLoader(page=page)

    await asyncio.sleep(6)
    print("Start Chat Roller")
    load = ml.MessageLoader(page=page)

    async for chat, name in chatObj.ChatRoller(cycle=1, MaxChat=6):
        await asyncio.sleep(2)
        print("Chat name:", name)
        print("----------- Message Loader work Start------------")
        async for msg, txt, tracing , obj in load.LiveMessages(pollingTime=2.0, chat_id=chat):
            element = msg
            text = txt
            print(text + f"-- Tracing  : [{tracing}] : [{obj.get('type')}]")  # Just Looping through messages right now

        print("----------- Message Loader work Done ------------")

        unread_status = await chatObj.isUnread(chat)
        if unread_status:
            print(f"[{name}] has unread messages!")
        elif unread_status is None:
            print(f"[{name}] manually marked unread (no numeric badge)")
        else:
            print(f"[{name}] is read")
        await chatObj.ChatClicker(chat)
        await chatObj.Do_Unread(chat)

    # -----
    print("Login Done , Waiting...")
    await asyncio.sleep(20000)
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')

    print("[ Top 10 memory allocations ]")
    for stat in top_stats[:10]:
        print(stat)


if __name__ == "__main__":
    asyncio.run(main())
