import asyncio
from httpx import ASGITransport, AsyncClient
from api import admin_panel_app


async def main():
    window_ms = input("New window_ms? Integers only (Empty input for not changing)\t")
    if window_ms == "":
        window_ms = None
    else:
        window_ms = int(window_ms)

    spike_threshold = input("New spike_threshold? Floats only (Empty input for not changing)\t")
    if spike_threshold == "":
        spike_threshold = spike_threshold
    else:
        spike_threshold = float(spike_threshold)

    transport = ASGITransport(app=admin_panel_app)
    async with AsyncClient(transport=transport, base_url="http://privateserver") as client:
        response = await client.patch(
            "/change",
            json={
                "window_ms": window_ms,
                "spike_threshold": spike_threshold
            }
        )

        print(response.status_code)
        print(response.json())


if __name__ == "__main__":
    asyncio.run(main())
