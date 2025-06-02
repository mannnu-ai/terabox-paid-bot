
import httpx
import re

async def get_direct_link(terabox_url):
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(terabox_url)
            match = re.search(r'"downloadUrl":"(https.*?)"', r.text)
            if match:
                return match.group(1).replace("\\u0026", "&")
    except Exception:
        pass
    return None
