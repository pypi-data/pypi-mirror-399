import asyncio
from decoder.cli.update_notifier.adapters.pypi_version_update_gateway import PyPIVersionUpdateGateway
import httpx

async def main():
    gateway = PyPIVersionUpdateGateway(project_name="decoder-cli")
    print(f"Checking update for decoder-cli...")
    try:
        update = await gateway.fetch_update()
        if update:
            print(f"Found update: {update.latest_version}")
        else:
            print("No update found.")
    except Exception as e:
        print(f"Error: {e}")

    # Inspect the raw response to see what's going on
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://pypi.org/simple/decoder-cli/", headers={"Accept": "application/vnd.pypi.simple.v1+json"})
        print(f"PyPI Status: {resp.status_code}")
        # print(resp.text[:500]) # print start of response

if __name__ == "__main__":
    asyncio.run(main())
