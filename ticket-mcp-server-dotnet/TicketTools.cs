using System.Net.Http.Headers;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Azure.Functions.Worker.Extensions.Mcp;
using Microsoft.Extensions.Logging;

namespace TicketMcpServer;

public class TicketTools
{
    private readonly IHttpClientFactory _httpClientFactory;
    private readonly ILogger<TicketTools> _logger;

    private static readonly string TicketApiUrl =
        Environment.GetEnvironmentVariable("TICKET_API_URL")
        ?? "https://emer-tickets-foundry-tool-api-chedfyh7dmezcfd5.westus-01.azurewebsites.net";

    private static readonly string? TicketApiKey =
        Environment.GetEnvironmentVariable("TICKET_API_KEY");

    public TicketTools(IHttpClientFactory httpClientFactory, ILogger<TicketTools> logger)
    {
        _httpClientFactory = httpClientFactory;
        _logger = logger;
    }

    private HttpClient CreateClient()
    {
        var client = _httpClientFactory.CreateClient();
        if (!string.IsNullOrEmpty(TicketApiKey))
        {
            client.DefaultRequestHeaders.Authorization =
                new AuthenticationHeaderValue("Bearer", TicketApiKey);
        }
        return client;
    }

    [Function(nameof(ListTickets))]
    public async Task<string> ListTickets(
        [McpToolTrigger("list_tickets", "Retrieves a list of all active support tickets from the system.")]
        ToolInvocationContext context)
    {
        using var client = CreateClient();
        var response = await client.GetAsync($"{TicketApiUrl}/api/tickets");
        var body = await response.Content.ReadAsStringAsync();

        return response.IsSuccessStatusCode
            ? $"Tickets Found:\n{body}"
            : $"Failed to retrieve ticket list (status {(int)response.StatusCode}): {body}";
    }

    [Function(nameof(GetTicketDetails))]
    public async Task<string> GetTicketDetails(
        [McpToolTrigger("get_ticket_details", "Retrieves the detailed status and summary of a specific ticket by its ID string.")]
        ToolInvocationContext context,
        [McpToolProperty("ticketId", "The ID of the ticket to look up.", isRequired: true)]
        string ticketId)
    {
        using var client = CreateClient();
        var response = await client.GetAsync($"{TicketApiUrl}/api/tickets/{ticketId}");
        var body = await response.Content.ReadAsStringAsync();

        return response.IsSuccessStatusCode
            ? $"Ticket Details for {ticketId}:\n{body}"
            : $"Ticket lookup failed (status {(int)response.StatusCode}): {body}";
    }
}