"""
Agent Factory - Main FastAPI Service
Manages specialized AI agents for different automation tasks
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn


# Pydantic Models
class RefinePromptRequest(BaseModel):
    goal: str

class RefinePromptResponse(BaseModel):
    refined_prompt: str

class FeasibilityRequest(BaseModel):
    prompt: str

class FeasibilityResponse(BaseModel):
    text: str
    option1_title: str
    option1_value: str
    option2_title: str
    option2_value: str

class OptimizePromptRequest(BaseModel):
    prompt: str
    path: str

class OptimizePromptResponse(BaseModel):
    final_prompt: str

class GenerateRequest(BaseModel):
    optimized_prompt: str

class GenerateResponse(BaseModel):
    generated_code: str
    code_type: str  # "n8n_workflow" or "python_agent"
    deployment_instructions: str


# FastAPI App Configuration
app = FastAPI(
    title="Agent Factory",
    description="AI-powered service for creating and managing specialized automation agents",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# System prompt for the prompt refinement agent
REFINE_PROMPT_SYSTEM = """You are an expert AI assistant helping a developer scope an automation task. 
Your role is to ask precise, technical clarifying questions to transform vague requests into specific, actionable requirements.

Guidelines:
- Ask 2-4 specific technical questions
- Focus on triggers, actions, and technical specifications
- Be concise and developer-focused
- Consider implementation details like APIs, webhooks, file formats, etc.
- Help identify the exact scope and requirements"""

# System prompt for the feasibility/strategy agent
FEASIBILITY_SYSTEM = """You are a technical strategist specializing in automation tool selection. 
Your role is to analyze refined automation requirements and recommend the optimal implementation approach.

**Key Context for Decision Making:**
n8n is a source-available workflow automation tool with over 400 pre-built integrations. It excels at tasks that are:
- Event-driven (webhook triggers)
- Run on a schedule (cron)
- Involve data synchronization between two or more known cloud applications like Slack, Jira, Google Sheets, and Airtable
- Connecting existing APIs with minimal custom logic

Custom Python is required for tasks involving:
- Complex, bespoke logic
- Parsing unstructured text or code files
- Heavy data manipulation
- Custom algorithms or processing
- Tasks requiring libraries not available in n8n

**Guidelines:**
- Analyze the task characteristics carefully
- Recommend n8n for standard API integrations and simple workflows
- Recommend Custom Python for complex logic or data processing
- Always provide clear reasoning for your recommendation
- Present both options but highlight the optimal choice"""

# System prompt for the optimize prompt/architect agent
OPTIMIZE_PROMPT_SYSTEM = """You are an expert prompt architect specializing in transforming high-level automation requirements into detailed, production-ready technical specifications.

**Your Role:**
Transform user requirements into precise technical blueprints following prompt engineering best practices:
- Assign a clear expert persona 
- Be highly specific with technical details
- Define exact output formats and requirements
- Include comprehensive error handling
- Specify exact API endpoints, data mappings, and logic flows

**Implementation Path Guidelines:**

**For n8n-only workflows:**
- Focus on node configurations and connections
- Specify exact trigger types and conditions
- Define precise data mappings between services
- Include error handling branches
- Reference n8n-specific syntax and operations

**For Custom Python Agents:**
- Specify FastAPI microservice architecture
- Define exact endpoint structures and webhook handling
- Include production-grade error handling and logging
- Specify API integrations and data processing logic
- Define clear success/failure response formats

**Quality Standards:**
- Every prompt must be immediately actionable by a technical implementer
- Include specific field names, API endpoints, and data structures
- Define clear success criteria and failure conditions
- Specify exact output formats and response structures"""


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Agent Factory is running", "status": "healthy"}


@app.post("/refine_prompt", response_model=RefinePromptResponse)
async def refine_prompt(request: RefinePromptRequest):
    """
    Refines a vague automation goal into specific technical questions
    
    Example:
    Input: {"goal": "I need a bot for GitHub."}
    Output: {"refined_prompt": "To clarify: 1. What GitHub event should trigger this bot..."}
    """
    try:
        # For now, we'll create a mock refined prompt based on the goal
        # TODO: Replace with actual LLM API call
        refined_prompt = await mock_refine_prompt(request.goal)
        
        return RefinePromptResponse(refined_prompt=refined_prompt)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error refining prompt: {str(e)}")


@app.post("/feasibility", response_model=FeasibilityResponse)
async def feasibility_analysis(request: FeasibilityRequest):
    """
    Analyzes a refined prompt and recommends optimal implementation approach (n8n vs Custom Python)
    
    Example:
    Input: {"prompt": "A bot to run a nightly sanity check on 10 internal APIs and post a summary to Slack."}
    Output: {
        "text": "This task involves a scheduled trigger and connecting two known APIs...",
        "option1_title": "n8n Sanity Check Workflow",
        "option1_value": "n8n-only workflow",
        "option2_title": "Custom Python Agent",
        "option2_value": "Custom Python Agent"
    }
    """
    try:
        # For now, we'll create a mock feasibility analysis based on the prompt
        # TODO: Replace with actual LLM API call
        analysis = await mock_feasibility_analysis(request.prompt)
        
        return FeasibilityResponse(**analysis)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing feasibility: {str(e)}")


@app.post("/optimize_prompt", response_model=OptimizePromptResponse)
async def optimize_prompt(request: OptimizePromptRequest):
    """
    Transforms requirements into detailed technical specifications (The Architect Agent)
    
    Example:
    Input: {
        "prompt": "Check for rollback scripts in DB migration PRs.",
        "path": "Custom Python Agent"
    }
    Output: {
        "final_prompt": "SYSTEM: You are an expert Python SRE. Generate a FastAPI service..."
    }
    """
    try:
        # For now, we'll create a mock optimized prompt based on the requirements
        # TODO: Replace with actual LLM API call
        optimized_prompt = await mock_optimize_prompt(request.prompt, request.path)
        
        return OptimizePromptResponse(final_prompt=optimized_prompt)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error optimizing prompt: {str(e)}")


async def mock_refine_prompt(goal: str) -> str:
    """
    Mock function to simulate LLM prompt refinement
    TODO: Replace with actual LLM API integration
    """
    # Simple mock logic based on keywords
    goal_lower = goal.lower()
    
    if "github" in goal_lower and "bot" in goal_lower:
        return "To clarify: 1. What GitHub event should trigger this bot (e.g., `pull_request.opened`)? 2. What is the primary language of the repository? 3. What is the specific action the bot should perform?"
    
    elif "automation" in goal_lower or "automate" in goal_lower:
        return "To clarify: 1. What specific process needs automation? 2. What triggers should start this automation? 3. What systems/APIs are involved? 4. What is the expected output format?"
    
    elif "api" in goal_lower:
        return "To clarify: 1. What data sources need to be integrated? 2. What authentication method is required? 3. What is the expected response format? 4. What error handling is needed?"
    
    else:
        return f"To clarify your goal '{goal}': 1. What specific trigger or event should initiate this? 2. What systems or platforms are involved? 3. What is the desired end result? 4. Are there any technical constraints or requirements?"


async def mock_feasibility_analysis(prompt: str) -> dict:
    """
    Mock function to simulate LLM feasibility analysis for n8n vs Custom Python decision
    TODO: Replace with actual LLM API integration
    """
    prompt_lower = prompt.lower()
    
    # Keywords that suggest n8n is optimal
    n8n_keywords = ["schedule", "cron", "nightly", "webhook", "api", "slack", "jira", "google sheets", 
                    "airtable", "trigger", "integration", "sync", "connect"]
    
    # Keywords that suggest custom Python is needed
    python_keywords = ["parse", "analysis", "complex logic", "algorithm", "machine learning", 
                      "data manipulation", "custom", "processing", "calculation"]
    
    n8n_score = sum(1 for keyword in n8n_keywords if keyword in prompt_lower)
    python_score = sum(1 for keyword in python_keywords if keyword in prompt_lower)
    
    # Specific logic for common patterns
    if "sanity check" in prompt_lower and "api" in prompt_lower and ("slack" in prompt_lower or "schedule" in prompt_lower):
        return {
            "text": "This task involves a scheduled trigger and connecting two known APIs (HTTP and Slack). n8n is highly optimized for this type of linear workflow.",
            "option1_title": "n8n Sanity Check Workflow",
            "option1_value": "n8n-only workflow",
            "option2_title": "Custom Python Agent", 
            "option2_value": "Custom Python Agent"
        }
    
    elif "github" in prompt_lower and ("webhook" in prompt_lower or "pull request" in prompt_lower):
        return {
            "text": "GitHub webhooks and API integrations are well-supported in n8n. Unless complex code analysis is required, n8n can handle most GitHub automation tasks efficiently.",
            "option1_title": "n8n GitHub Workflow",
            "option1_value": "n8n-only workflow",
            "option2_title": "Custom Python Bot",
            "option2_value": "Custom Python Agent"
        }
    
    elif any(word in prompt_lower for word in ["parse", "analysis", "complex", "algorithm", "machine learning"]):
        return {
            "text": "This task requires complex logic, data processing, or custom algorithms that are beyond n8n's capabilities. Custom Python provides the flexibility needed for sophisticated processing.",
            "option1_title": "Custom Python Solution",
            "option1_value": "Custom Python Agent",
            "option2_title": "n8n with Custom Code",
            "option2_value": "n8n-only workflow"
        }
    
    elif n8n_score > python_score:
        return {
            "text": "This automation involves standard API integrations and workflows that n8n handles efficiently. The task appears to be event-driven or scheduled with known service integrations.",
            "option1_title": "n8n Automation Workflow",
            "option1_value": "n8n-only workflow", 
            "option2_title": "Custom Python Solution",
            "option2_value": "Custom Python Agent"
        }
    
    else:
        return {
            "text": "This task may require custom logic or specialized processing. While n8n could handle basic integrations, Python would provide more control and flexibility for complex requirements.",
            "option1_title": "Custom Python Agent",
            "option1_value": "Custom Python Agent",
            "option2_title": "n8n Workflow",
            "option2_value": "n8n-only workflow"
        }


async def mock_optimize_prompt(prompt: str, path: str) -> str:
    """
    Mock function to simulate LLM prompt optimization for technical specifications
    TODO: Replace with actual LLM API integration
    """
    prompt_lower = prompt.lower()
    path_lower = path.lower()
    
    # Example 1: Jira Sync (n8n Path)
    if "jira" in prompt_lower and "google sheet" in prompt_lower and "n8n" in path_lower:
        return """SYSTEM: You are an expert n8n JSON generator. Your task is to create a workflow that triggers when a new issue is created in the Jira project with the key 'PHOENIX'. The workflow must:

1. Use the 'Jira Trigger' node configured for the 'Issue Created' event.
2. Use the 'Google Sheets' node with the 'Append Row' operation.
3. Map the Jira issue 'Summary' field to column 'A', the 'Key' field to column 'B', and the 'Reporter's Name' to column 'C' in the target sheet.
4. Include a basic error handling branch.

Use the provided few-shot examples as your primary reference for correct syntax."""

    # Example 2: Visual Regression Testing (n8n Path)
    elif ("screenshot" in prompt_lower or "visual" in prompt_lower or "ui" in prompt_lower) and "n8n" in path_lower:
        return """SYSTEM: You are an expert n8n JSON generator. Your task is to create a workflow triggered by a webhook from our CI/CD pipeline's 'deployment_success' event for the 'staging' environment. The workflow must:

1. Use two parallel 'httpRequest' nodes to call a visual testing API for the URLs `staging.myapp.com/home` and `staging.myapp.com/pricing`.
2. Use a 'Compare Images' or similar function node to check for differences against baseline production images.
3. Use an 'If' node to check if the difference score is above a 5% threshold.
4. If the condition is met, use the 'Slack' node to post a detailed alert to the '#ui-regressions' channel, including the URL of the page that failed the visual test."""

    # Example 3: Vulnerability Scanning (Python Path)
    elif ("vulnerability" in prompt_lower or "security" in prompt_lower or "requirements.txt" in prompt_lower) and "python" in path_lower:
        return """SYSTEM: You are an expert Python security engineer. Generate a robust FastAPI microservice that exposes a `/webhook` endpoint to receive GitHub 'pull_request.opened' payloads. The service must:

1. Parse the webhook payload to get the PR details and the list of changed files.
2. If 'requirements.txt' is in the changed files list, fetch its content using the GitHub API.
3. Identify only the newly added libraries by comparing the file to its previous version.
4. For each new library, make an API call to a security vulnerability database (like the OSV API) to check for known vulnerabilities.
5. If any new library has a 'HIGH' or 'CRITICAL' severity vulnerability, use the GitHub API to post a comment back to the pull request, detailing the vulnerable package and linking to the CVE. The agent must then return a `{"status": "fail"}`.
6. If no critical vulnerabilities are found, it should return a `{"status": "pass"}`.

The code must be production-grade, with error handling for all API calls."""

    # Generic patterns for n8n workflows
    elif "n8n" in path_lower:
        # Detect common n8n patterns
        if "slack" in prompt_lower and "webhook" in prompt_lower:
            return f"""SYSTEM: You are an expert n8n JSON generator. Create a workflow that handles webhook triggers and integrates with Slack. The workflow must:

1. Use a 'Webhook' trigger node to receive incoming data.
2. Process the incoming payload using 'Set' or 'Function' nodes as needed.
3. Use the 'Slack' node to send formatted messages to the appropriate channel.
4. Include error handling with proper HTTP response codes.
5. Map all relevant data fields from the webhook to the Slack message format.

Based on the requirement: "{prompt}"

Ensure all node configurations are production-ready with proper error handling."""

        elif "schedule" in prompt_lower or "cron" in prompt_lower:
            return f"""SYSTEM: You are an expert n8n JSON generator. Create a scheduled workflow that runs on a defined interval. The workflow must:

1. Use a 'Cron' trigger node with the appropriate schedule expression.
2. Include data fetching nodes for the required APIs or services.
3. Process and transform the data using appropriate nodes.
4. Include conditional logic using 'If' nodes where necessary.
5. Implement proper error handling and logging.

Based on the requirement: "{prompt}"

Specify exact API endpoints, data mappings, and response handling."""

        else:
            return f"""SYSTEM: You are an expert n8n JSON generator. Create a workflow based on the following requirement: "{prompt}"

The workflow must:
1. Use appropriate trigger nodes (webhook, schedule, or manual).
2. Include all necessary processing and transformation nodes.
3. Connect to the required external services using built-in integrations.
4. Implement proper error handling and data validation.
5. Define clear success and failure paths.

Provide specific node configurations, data mappings, and connection details."""

    # Generic patterns for Python agents
    elif "python" in path_lower:
        if "github" in prompt_lower and ("pr" in prompt_lower or "pull request" in prompt_lower):
            return f"""SYSTEM: You are an expert Python developer. Generate a FastAPI microservice that handles GitHub webhooks for pull request events. The service must:

1. Expose a `/webhook` endpoint that receives GitHub 'pull_request' payloads.
2. Validate the webhook signature for security.
3. Parse the payload to extract PR details and changed files.
4. Implement the specific logic required: {prompt}
5. Use the GitHub API to interact with the repository (comments, status checks, etc.).
6. Return structured JSON responses with clear status indicators.
7. Include comprehensive error handling and logging.
8. Follow FastAPI best practices with proper Pydantic models.

The code must be production-grade with proper authentication, error handling, and documentation."""

        elif "api" in prompt_lower and ("monitor" in prompt_lower or "check" in prompt_lower):
            return f"""SYSTEM: You are an expert Python SRE. Generate a FastAPI service for API monitoring and health checking. The service must:

1. Implement endpoints for health monitoring and status reporting.
2. Include scheduled tasks for periodic API checks.
3. Handle authentication and rate limiting appropriately.
4. Implement proper logging and error reporting.
5. Based on the requirement: {prompt}
6. Return structured responses with clear status indicators.
7. Include retry logic and circuit breaker patterns.
8. Support configuration via environment variables.

The code must be production-ready with comprehensive error handling."""

        else:
            return f"""SYSTEM: You are an expert Python developer. Generate a FastAPI microservice based on the following requirement: "{prompt}"

The service must:
1. Implement appropriate endpoints with proper HTTP methods.
2. Use Pydantic models for request/response validation.
3. Include comprehensive error handling and logging.
4. Implement proper authentication and security measures.
5. Follow FastAPI best practices and patterns.
6. Include health check endpoints and proper status responses.
7. Handle external API integrations with retry logic.
8. Return structured JSON responses with clear success/failure indicators.

The code must be production-grade, well-documented, and ready for deployment."""

    else:
        # Fallback for unclear paths
        return f"""SYSTEM: You are an expert automation architect. Transform the following requirement into a detailed technical specification: "{prompt}"

The implementation should:
1. Define clear input/output specifications.
2. Include comprehensive error handling.
3. Specify exact API endpoints and data structures.
4. Define success criteria and failure conditions.
5. Include proper logging and monitoring.
6. Follow industry best practices for the chosen technology stack.

Provide a complete, actionable technical blueprint that can be immediately implemented."""


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
