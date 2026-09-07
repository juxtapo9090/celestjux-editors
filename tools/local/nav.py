import json, urllib.request, asyncio, websockets, sys
PORT = 33687
URL = sys.argv[1]
t = json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json"))
pages = [p for p in t if p.get("type")=="page" and p.get("webSocketDebuggerUrl")]
for p in pages: print("tab:", p.get("url"))
ws_url = pages[0]["webSocketDebuggerUrl"]

async def main():
    async with websockets.connect(ws_url, max_size=64*1024*1024) as ws:
        await ws.send(json.dumps({"id":1,"method":"Page.navigate","params":{"url":URL}}))
        while True:
            m=json.loads(await ws.recv())
            if m.get("id")==1: print("navigate ->", m.get("result")); break
        await asyncio.sleep(3)
        await ws.send(json.dumps({"id":2,"method":"Runtime.evaluate","params":{
            "expression":"JSON.stringify({url:location.href, cjx: typeof window.cjx, themes: (window.cjx? cjx.themes(): null)})",
            "returnByValue":True,"awaitPromise":True}}))
        while True:
            m=json.loads(await ws.recv())
            if m.get("id")==2:
                print("page:", str(m.get("result",{}).get("result",{}).get("value"))[:600]); break
asyncio.run(main())
