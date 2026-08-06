import os
import sys
import httpx
import uvicorn
from fastmcp import FastMCP

mcp = FastMCP("Ticket-Management-Server")

TICKET_API_URL = os.environ.get(
    "TICKET_API_URL",
    "https://emer-tickets-foundry-tool-api-chedfyh7dmezcfd5.westus-01.azurewebsites.net",
)
TICKET_API_KEY = os.environ.get("TICKET_API_KEY")


def _auth_headers() -> dict:
    if TICKET_API_KEY:
        return {"Authorization": f"Bearer {TICKET_API_KEY}"}
    return {}


@mcp.tool()
async def list_tickets() -> str:
    """Retrieves a list of all active support tickets from the system."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{TICKET_API_URL}/api/tickets", headers=_auth_headers())

    if response.status_code == 200:
        return f"Tickets Found:\n{response.text}"
    return f"Failed to retrieve ticket list (status {response.status_code}): {response.text}"


@mcp.tool()
async def get_ticket_details(ticket_id: str) -> str:
    """Retrieves the detailed status and summary of a specific ticket by its ID string."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{TICKET_API_URL}/api/tickets/{ticket_id}", headers=_auth_headers())

    if response.status_code == 200:
        return f"Ticket Details for {ticket_id}:\n{response.text}"
    return f"Ticket lookup failed (status {response.status_code}): {response.text}"


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "web":
        # Build FastMCP's real streamable-HTTP ASGI app. `path="/mcp"` fixes the
        # mount point at exactly /mcp (no nested /mcp/mcp), which we match to the
        # Azure Functions route below.
        app = mcp.http_app(path="/mcp", transport="streamable-http")

        port = int(os.environ.get("FUNCTIONS_CUSTOMHANDLER_PORT", 7071))

        # TEMP: log every incoming path/method while we confirm what
        # enableForwardingHttpRequest actually delivers to this process.
        # Remove once verified.
        @app.middleware("http")
        async def _log_requests(request, call_next):
            print(f"[incoming] {request.method} {request.url.path}", flush=True)
            return await call_next(request)

        uvicorn.run(app, host="127.0.0.1", port=port)
    else:
        mcp.run(transport="stdio")