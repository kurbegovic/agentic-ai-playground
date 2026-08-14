import azure.functions as func
import json
import os

import pyodbc

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

SQL_CONN_STRING = os.environ.get("SQL_CONN_STRING")


def get_connection():
    return pyodbc.connect(SQL_CONN_STRING)


def _row_to_ticket(row) -> dict:
    return {
        "id": str(row.Id),
        "title": row.Title,
        "description": row.Description,
        "status": row.Status,
        "priority": row.Priority,
    }


# 1. LIST ENDPOINT
@app.route(route="tickets", methods=["GET"])
def list_tickets(req: func.HttpRequest) -> func.HttpResponse:
    """Returns a list of all support tickets from the database."""
    try:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Id, Title, Description, Status, Priority FROM Tickets ORDER BY Id")
            tickets = [_row_to_ticket(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    except pyodbc.Error as e:
        return func.HttpResponse(
            json.dumps({"error": f"Database error: {e}"}),
            mimetype="application/json",
            status_code=500
        )

    return func.HttpResponse(
        json.dumps(tickets),
        mimetype="application/json",
        status_code=200
    )

# 2. GET ENDPOINT
@app.route(route="tickets/{id}", methods=["GET"])
def get_ticket(req: func.HttpRequest) -> func.HttpResponse:
    """Gets details for a single ticket by its ID from the database."""
    ticket_id = req.route_params.get('id')
    try:
        ticket_id_int = int(ticket_id)
    except (TypeError, ValueError):
        return func.HttpResponse(
            json.dumps({"error": "Ticket not found"}),
            mimetype="application/json",
            status_code=404
        )

    try:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT Id, Title, Description, Status, Priority FROM Tickets WHERE Id = ?",
                ticket_id_int
            )
            row = cursor.fetchone()
        finally:
            conn.close()
    except pyodbc.Error as e:
        return func.HttpResponse(
            json.dumps({"error": f"Database error: {e}"}),
            mimetype="application/json",
            status_code=500
        )

    if not row:
        return func.HttpResponse(
            json.dumps({"error": "Ticket not found"}),
            mimetype="application/json",
            status_code=404
        )

    return func.HttpResponse(
        json.dumps(_row_to_ticket(row)),
        mimetype="application/json",
        status_code=200
    )

# 3. OPENAPI SPEC ENDPOINT (Required by AI Foundry)
@app.route(route="openapi.json", methods=["GET"])
def get_openapi(req: func.HttpRequest) -> func.HttpResponse:
    """Serves the OpenAPI specification file for AI Foundry tool registration."""
    host_url = req.url.split('/api/')[0]
    
    openapi_spec = {
        "openapi": "3.0.1",
        "info": {
            "title": "Support Ticket Tool API",
            "version": "1.0.0",
            "description": "API for listing and retrieving support tickets for AI Foundry agents."
        },
        "servers": [{"url": f"{host_url}/api"}],
        "paths": {
            "/tickets": {
                "get": {
                    "operationId": "listTickets",
                    "summary": "Retrieve a list of all sample support tickets",
                    "responses": {
                        "200": {
                            "description": "A successful list of tickets"
                        }
                    }
                }
            },
            "/tickets/{id}": {
                "get": {
                    "operationId": "getTicket",
                    "summary": "Get details of a single ticket by ID",
                    "parameters": [
                        {
                            "name": "id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "The unique numerical ID of the ticket"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Ticket details successfully retrieved"
                        },
                        "404": {
                            "description": "Ticket ID not found"
                        }
                    }
                }
            }
        }
    }
    return func.HttpResponse(
        json.dumps(openapi_spec),
        mimetype="application/json",
        status_code=200
    )
