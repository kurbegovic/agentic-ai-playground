using Azure.AI.AgentServer.Core;
using Azure.AI.AgentServer.Responses;
using Azure.AI.AgentServer.Responses.Models;
using Azure.AI.Projects;
using Azure.Core;
using Azure.Identity;
using DotNetEnv;
using Microsoft.Agents.AI;
using Microsoft.Agents.AI.Foundry.Hosting;
using Microsoft.Agents.AI.Workflows;

#pragma warning disable MAAI001

Env.TraversePath().Load();

var projectEndpoint = new Uri(Environment.GetEnvironmentVariable("FOUNDRY_PROJECT_ENDPOINT")
    ?? throw new InvalidOperationException("FOUNDRY_PROJECT_ENDPOINT environment variable is not set."));

// Credential selection: local dev (azd ai agent run) has no Managed Identity but
// has Azure CLI available. Deployed containers have Managed Identity available but
// do NOT have Azure CLI installed. IDENTITY_ENDPOINT is set only when Managed
// Identity is available (App Service, Container Apps, Functions, and Foundry
// hosted agent containers), so it reliably distinguishes the two environments.
var hasManagedIdentity = Environment.GetEnvironmentVariable("IDENTITY_ENDPOINT") is not null;

TokenCredential credential = hasManagedIdentity
    ? new DefaultAzureCredential()
    : new AzureCliCredential();

var projectClient = new AIProjectClient(projectEndpoint, credential);

// Fetch existing, already-published agents by name. GetAgentAsync (no version
// argument) always resolves the latest published version, so you don't need to
// manually update a version number in code every time you republish an agent.
var errorResolverResult = await projectClient.AgentAdministrationClient
    .GetAgentAsync("error-resolver-agent", CancellationToken.None);
var githubIssueManagerResult = await projectClient.AgentAdministrationClient
    .GetAgentAsync("github-issue-manager", CancellationToken.None);

AIAgent errorResolverAgent = projectClient.AsAIAgent(errorResolverResult.Value);
AIAgent githubIssueManagerAgent = projectClient.AsAIAgent(githubIssueManagerResult.Value);

// Sequential chain: error-resolver-agent -> github-issue-manager
AIAgent agent = AgentWorkflowBuilder
    .BuildSequential("devops-error-pipeline", errorResolverAgent, githubIssueManagerAgent)
    .AsAIAgent(
        name: "devops-error-pipeline",
        description: "Analyzes error logs and creates or updates GitHub issues with root cause and resolution steps.");

var builder = AgentHost.CreateBuilder(args);
builder.Services.AddFoundryResponses(agent);

// Local dev fallback: the real Foundry platform injects an x-agent-user-id header
// automatically for session isolation. Running locally via `azd ai agent run` has
// nothing supplying that header, which otherwise causes a
// "HostedSessionIsolationKeyProvider returned null" crash. This override supplies
// a static fallback for local testing only.
builder.Services.AddSingleton<HostedSessionIsolationKeyProvider, LocalDevSessionIsolationKeyProvider>();

builder.RegisterProtocol("responses", endpoints => endpoints.MapFoundryResponses());

var app = builder.Build();
app.Run();

sealed class LocalDevSessionIsolationKeyProvider : HostedSessionIsolationKeyProvider
{
    public override ValueTask<HostedSessionContext> GetKeysAsync(
        ResponseContext context,
        CreateResponse request,
        CancellationToken cancellationToken)
    {
        return ValueTask.FromResult(new HostedSessionContext("local-dev-user"));
    }
}