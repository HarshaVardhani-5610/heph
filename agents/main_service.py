"""
Agent Factory - Main FastAPI Service
Manages specialized AI agents for different automation tasks
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import sys
import os
import asyncio

# Add parent directory to path to import api_key_manager
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api_key_manager import get_perplexity_manager, call_perplexity_api


# Pydantic Models
class RefinePromptRequest(BaseModel):
    goal: str

class RefinePromptResponse(BaseModel):
    refined_prompt: str
    questions: Optional[str] = None  # Clarifying questions to ask user

class FeasibilityRequest(BaseModel):
    prompt: str
    user_answers: Optional[str] = None  # User's answers to clarifying questions

class FeasibilityResponse(BaseModel):
    text: str
    option1_title: str
    option1_value: str
    option2_title: str
    option2_value: str
    recommended_option: Optional[str] = None

class OptimizePromptRequest(BaseModel):
    prompt: str
    path: str
    refinement_instruction: Optional[str] = None

class OptimizePromptResponse(BaseModel):
    final_prompt: str

class GenerateRequest(BaseModel):
    prompt: str
    path: str
    requirements: Optional[str] = None
    optimization_notes: Optional[str] = None

class GenerateResponse(BaseModel):
    generated_code: str
    file_structure: Optional[dict] = None
    implementation_notes: Optional[str] = None


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


@app.get("/api-status")
async def api_status():
    """Get current status of Perplexity API keys"""
    try:
        manager = get_perplexity_manager()
        return manager.get_status()
    except Exception as e:
        return {"error": f"Failed to get API status: {str(e)}"}


@app.post("/refine_prompt", response_model=RefinePromptResponse)
async def refine_prompt(request: RefinePromptRequest):
    """
    Analyzes user goals like an intelligent consultant and asks only necessary questions
    
    Example:
    Input: {"goal": "I need to check my website"}
    Output: {
        "refined_prompt": "Website monitoring system for health checks",
        "questions": "What is the URL of the website you want to monitor?"
    }
    
    Input: {"goal": "Monitor https://api.myapp.com and send alerts to Slack"}
    Output: {
        "refined_prompt": "API monitoring system with Slack notifications",
        "questions": "What should trigger an alert (downtime, slow response, errors)? What is your Slack webhook URL?"
    }
    """
    try:
        # Use Perplexity API for intelligent analysis and targeted questions
        system_prompt = f"""You are an intelligent automation consultant. Your job is to analyze the user's goal and ask only the specific questions needed to make it actionable.

**Your Process:**
1. First, summarize your understanding of what they want to achieve in one sentence
2. Second, identify the specific missing entities or ambiguities in their request (e.g., missing URL, vague action, undefined trigger)
3. Finally, formulate 1-2 precise questions to get only the information you are missing
4. Do NOT ask any questions if the goal is already clear and actionable

**Examples of Intelligent Analysis:**

User: "I need to check my website"
Missing: URL, what "check" means, what to do with results
Questions: "1. What is the URL of the website? 2. What should happen when issues are detected?"

User: "Monitor https://api.myapp.com and alert Slack when down"
Missing: Slack details, definition of "down"
Questions: "1. What is your Slack webhook URL? 2. Should alerts trigger on downtime only, or also slow responses/errors?"

User: "Backup my database every night at 2 AM"
Missing: Database details, backup location
Questions: "1. What type of database (MySQL, PostgreSQL, etc.) and connection details? 2. Where should backups be stored?"

User: "Send a daily report of our API usage to team@company.com at 9 AM"
Missing: Data source, report format
Questions: "1. Which API service provides the usage data? 2. What specific metrics should be included in the report?"

**User's Goal:** "{request.goal}"

Analyze this goal and respond with EXACTLY this JSON format:
{{
  "refined_prompt": "One sentence summary of what they want to achieve",
  "questions": "Your targeted questions (or null if no questions needed)"
}}

Remember: Only ask what you actually need to know. Don't ask generic questions."""

        # Call Perplexity API
        response = await call_perplexity_api(
            system_prompt,
            max_tokens=800,
            temperature=0.2  # Lower temperature for more focused analysis
        )
        
        # Extract and parse the response
        if response.get('choices') and response['choices'][0].get('message'):
            content = response['choices'][0]['message']['content']
            
            # Try to extract JSON from response
            import json
            import re
            
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group())
                    return RefinePromptResponse(
                        refined_prompt=data.get('refined_prompt', f"Refined goal: {request.goal}"),
                        questions=data.get('questions', "Please provide more details about your automation requirements.")
                    )
                except json.JSONDecodeError:
                    pass
        
        # Fallback to mock if API fails
        return await mock_refine_prompt_with_questions(request.goal)
    
    except Exception as e:
        # Fallback to mock function if API fails
        try:
            return await mock_refine_prompt_with_questions(request.goal)
        except:
            raise HTTPException(status_code=500, detail=f"Error refining prompt: {str(e)}")


@app.post("/feasibility", response_model=FeasibilityResponse)
async def feasibility_analysis(request: FeasibilityRequest):
    """
    Analyzes a refined prompt AND user answers to recommend optimal implementation approach
    
    Example:
    Input: {
        "prompt": "Database rollback script checker for GitLab PRs",
        "user_answers": "1. Monitor all PRs with .sql files 2. Check for CREATE/ALTER/DROP statements 3. Post comments on PRs missing rollbacks"
    }
    Output: {
        "text": "This task requires parsing SQL files and GitLab API integration...",
        "option1_title": "Custom Python Agent",
        "option1_value": "Custom Python Agent",
        "option2_title": "n8n + Custom Scripts", 
        "option2_value": "n8n-only workflow",
        "recommended_option": "Custom Python Agent"
    }
    """
    try:
        # Build comprehensive prompt including user answers
        full_context = f"Original Goal: {request.prompt}"
        if request.user_answers:
            full_context += f"\n\nUser's Clarifying Answers: {request.user_answers}"
        
        # Use Perplexity API for feasibility analysis
        system_prompt = f"""You are a technical strategist specializing in automation tool selection. 
Your role is to analyze automation requirements (including user clarifications) and recommend the optimal approach.

**Key Context for Decision Making:**
n8n is excellent for:
- Event-driven workflows (webhooks)
- Scheduled tasks (cron)
- API integrations between known services (Slack, Jira, Google Sheets, etc.)
- Simple data transformations

Custom Python is required for:
- Complex logic and algorithms
- File parsing (code, logs, documents)
- Heavy data manipulation
- Custom API implementations
- Tasks requiring specialized libraries

**Analysis Context:**
{full_context}

**Guidelines:**
- Analyze BOTH the original goal AND the user's clarifying answers
- Consider implementation complexity, maintainability, and scalability
- Recommend the approach that best fits the specific requirements
- Provide clear reasoning for your recommendation

Return ONLY a JSON object with these exact fields:
{{
  "text": "your detailed analysis considering the user's answers",
  "option1_title": "recommended option title",
  "option1_value": "Custom Python Agent" or "n8n-only workflow",
  "option2_title": "alternative option title", 
  "option2_value": "n8n-only workflow" or "Custom Python Agent",
  "recommended_option": "Custom Python Agent" or "n8n-only workflow"
}}"""

        # Call Perplexity API
        response = await call_perplexity_api(
            system_prompt,
            max_tokens=1000,
            temperature=0.2
        )
        
        # Extract and parse the response
        if response.get('choices') and response['choices'][0].get('message'):
            content = response['choices'][0]['message']['content']
            
            # Try to extract JSON from response
            import json
            import re
            
            # Look for JSON in the response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                try:
                    analysis_data = json.loads(json_match.group())
                    return FeasibilityResponse(**analysis_data)
                except json.JSONDecodeError:
                    pass
        
        # Fallback to mock if API fails or parsing fails
        return await mock_feasibility_analysis(request.prompt, request.user_answers)
    
    except Exception as e:
        # Fallback to mock function if API fails
        try:
            return await mock_feasibility_analysis(request.prompt, request.user_answers)
        except:
            raise HTTPException(status_code=500, detail=f"Error analyzing feasibility: {str(e)}")
        
        # Fallback to mock if parsing fails
        analysis = await mock_feasibility_analysis(request.prompt)
        return FeasibilityResponse(**analysis)
    
    except Exception as e:
        # Fallback to mock function if API fails
        try:
            analysis = await mock_feasibility_analysis(request.prompt)
            return FeasibilityResponse(**analysis)
        except:
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
        # Use Perplexity API for prompt optimization
        system_prompt = f"""You are an expert prompt architect specializing in transforming high-level automation requirements into detailed, production-ready technical specifications.

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
- Specify exact output formats and response structures

Transform this requirement into a detailed technical specification:
Prompt: "{request.prompt}"
Implementation Path: "{request.path}"

Create a comprehensive SYSTEM prompt that an AI agent can follow to implement this exactly."""

        # Call Perplexity API
        response = await call_perplexity_api(
            system_prompt,
            max_tokens=1500,
            temperature=0.1
        )
        
        # Extract the optimized prompt from response
        if response.get('choices') and response['choices'][0].get('message'):
            optimized_prompt = response['choices'][0]['message']['content']
        else:
            # Fallback to mock if API response is unexpected
            optimized_prompt = await mock_optimize_prompt(request.prompt, request.path)
        
        return OptimizePromptResponse(final_prompt=optimized_prompt)
    
    except Exception as e:
        # Fallback to mock function if API fails
        try:
            optimized_prompt = await mock_optimize_prompt(request.prompt, request.path)
            return OptimizePromptResponse(final_prompt=optimized_prompt)
        except:
            raise HTTPException(status_code=500, detail=f"Error optimizing prompt: {str(e)}")


@app.post("/generate_code", response_model=GenerateResponse)
async def generate_code(request: GenerateRequest):
    """
    Station 4 - The Builder Agent: Generates actual code from optimized prompts
    
    This is the final and most critical agent that executes the technical specifications
    from the Architect agent with absolute precision and adherence to instructions.
    
    Example:
    Input: {"optimized_prompt": "SYSTEM: You are an expert Python SRE. Generate a FastAPI service..."}
    Output: {
        "generated_code": "from fastapi import FastAPI...",
        "code_type": "python_agent",
        "deployment_instructions": "1. Install dependencies: pip install fastapi uvicorn..."
    }
    """
    try:
        # Use Perplexity API for code generation with the optimized prompt
        code_generation_prompt = f"""Follow this technical specification exactly and generate production-ready code:

{request.optimized_prompt}

Requirements:
- Generate complete, syntactically correct code
- Include proper error handling and logging
- Use environment variables for configuration
- Follow security best practices
- Include comprehensive comments
- Make the code production-ready

If this is for n8n, generate valid JSON workflow.
If this is for Python, generate complete FastAPI microservice code.

Also provide deployment instructions as a separate section."""

        # Call Perplexity API
        response = await call_perplexity_api(
            code_generation_prompt,
            max_tokens=4000,
            temperature=0.1
        )
        
        # Extract and process the response
        if response.get('choices') and response['choices'][0].get('message'):
            generated_content = response['choices'][0]['message']['content']
            
            # Determine code type and extract deployment instructions
            code_type = "python_agent"
            if "n8n" in request.optimized_prompt.lower() or "nodes" in generated_content:
                code_type = "n8n_workflow"
            
            # Try to separate code from deployment instructions
            deployment_instructions = "1. Follow the generated code implementation"
            if "deployment" in generated_content.lower() or "install" in generated_content.lower():
                # Try to extract deployment section
                parts = generated_content.split("Deployment")
                if len(parts) > 1:
                    deployment_instructions = f"Deployment{parts[-1]}"
                    generated_content = parts[0]
            
            return GenerateResponse(
                generated_code=generated_content,
                code_type=code_type,
                deployment_instructions=deployment_instructions
            )
        
        # Fallback to mock if API response is unexpected
        result = await mock_generate_code(request.optimized_prompt)
        return GenerateResponse(
            generated_code=result["code"],
            code_type=result["type"],
            deployment_instructions=result["deployment"]
        )
    
    except Exception as e:
        # Fallback to mock function if API fails
        try:
            result = await mock_generate_code(request.optimized_prompt)
            return GenerateResponse(
                generated_code=result["code"],
                code_type=result["type"],
                deployment_instructions=result["deployment"]
            )
        except:
            raise HTTPException(status_code=500, detail=f"Error generating code: {str(e)}")


async def mock_refine_prompt_with_questions(goal: str) -> RefinePromptResponse:
    """
    Mock function demonstrating intelligent consultant behavior
    Only asks for genuinely missing information, not generic questions
    """
    goal_lower = goal.lower()
    
    # Website monitoring examples
    if "check" in goal_lower and "website" in goal_lower and "http" not in goal_lower:
        return RefinePromptResponse(
            refined_prompt="Website monitoring system for health checks",
            questions="1. What is the URL of the website? 2. What should happen when issues are detected?"
        )
    
    # API monitoring with partial details
    elif "monitor" in goal_lower and "api" in goal_lower and "slack" in goal_lower and "webhook" not in goal_lower:
        return RefinePromptResponse(
            refined_prompt="API monitoring system with Slack notifications", 
            questions="1. What is your Slack webhook URL? 2. Should alerts trigger on downtime only, or also slow responses/errors?"
        )
    
    # Database backup with missing connection details
    elif "backup" in goal_lower and ("database" in goal_lower or "postgresql" in goal_lower or "mysql" in goal_lower):
        return RefinePromptResponse(
            refined_prompt="Automated database backup system",
            questions="1. What are the database connection details? 2. Where should backups be stored?"
        )
    
    # Complete and actionable goals - no questions needed!
    elif ("http" in goal_lower and "every" in goal_lower and "log" in goal_lower) or \
         ("send" in goal_lower and "get request" in goal_lower and "hour" in goal_lower):
        return RefinePromptResponse(
            refined_prompt="Automated HTTP health check with response logging",
            questions=None  # Goal is already complete and actionable!
        )
    
    # GitLab automation with specific details
    elif "gitlab" in goal_lower and "sql" in goal_lower and "rollback" in goal_lower:
        return RefinePromptResponse(
            refined_prompt="GitLab SQL rollback validation system for pull request monitoring",
            questions="1. What is your GitLab API token? 2. Which specific GitLab project(s) should be monitored?" 
                     # Goal is very specific about what to do, just needs access details
        )
    
    # GitHub automation with specific details  
    elif "github" in goal_lower and ("pull request" in goal_lower or "commit" in goal_lower):
        if "webhook" not in goal_lower:
            return RefinePromptResponse(
                refined_prompt="GitHub repository automation system",
                questions="1. What is your GitHub webhook URL? 2. Which specific events should trigger actions?"
            )
        else:
            return RefinePromptResponse(
                refined_prompt="GitHub repository automation with webhook integration",
                questions=None  # All details provided
            )
    
    # Very vague goals need clarification
    elif len(goal.split()) < 6 and ("bot" in goal_lower or "automate something" in goal_lower):
        return RefinePromptResponse(
            refined_prompt=f"Automation system for {goal}",
            questions="1. What specific task should be automated? 2. What should trigger this automation? 3. What actions should be performed?"
        )
    
    # Generic catch-all - but still intelligent
    else:
        # Analyze what's actually missing
        missing_elements = []
        if "monitor" in goal_lower and "http" not in goal_lower:
            missing_elements.append("URL or endpoint to monitor")
        if "alert" in goal_lower and "email" not in goal_lower and "slack" not in goal_lower:
            missing_elements.append("notification destination")
        if "schedule" in goal_lower and not any(time in goal_lower for time in ["daily", "hourly", "minute", "am", "pm"]):
            missing_elements.append("specific timing")
            
        if missing_elements:
            questions = f"What {' and '.join(missing_elements)} should be used?"
        else:
            questions = "1. What specific triggers should start this automation? 2. What actions should be performed?"
            
        return RefinePromptResponse(
            refined_prompt=f"Intelligent automation system for {goal}",
            questions=questions
        )

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


async def mock_feasibility_analysis(prompt: str, user_answers: Optional[str] = None) -> FeasibilityResponse:
    """
    Mock function to simulate LLM feasibility analysis for n8n vs Custom Python decision
    NOW INCLUDES USER ANSWERS in the analysis!
    TODO: Replace with actual LLM API integration
    """
    # Combine prompt and user answers for comprehensive analysis
    full_context = prompt.lower()
    if user_answers:
        full_context += f" {user_answers.lower()}"
    
    # Keywords that suggest n8n is optimal
    n8n_keywords = ["schedule", "cron", "nightly", "webhook", "api integration", "slack", "jira", "google sheets", 
                    "airtable", "simple trigger", "connect services", "sync data"]
    
    # Keywords that suggest custom Python is needed
    python_keywords = ["parse", "parsing", "complex logic", "algorithm", "file processing", "custom", 
                      "sql analysis", "code analysis", "machine learning", "data science", "scraping",
                      "rollback", "migration check", "validation", "compliance"]
    
    # Count keyword matches
    n8n_score = sum(1 for keyword in n8n_keywords if keyword in full_context)
    python_score = sum(1 for keyword in python_keywords if keyword in full_context)
    
    # Special cases based on user answers
    if user_answers and any(word in user_answers.lower() for word in ["parse sql", "analyze code", "check files", "rollback", "migration"]):
        python_score += 3
    
    if user_answers and any(word in user_answers.lower() for word in ["slack notification", "webhook", "schedule", "simple integration"]):
        n8n_score += 2
    
    # Determine recommendation
    if python_score > n8n_score:
        recommended = "Custom Python Agent"
        analysis_text = f"Based on your requirements (especially: {user_answers[:100] if user_answers else 'the complexity mentioned'}...), this task requires custom logic, file parsing, or complex data manipulation that exceeds n8n's capabilities. A Custom Python Agent will provide the flexibility and processing power needed."
        option1_title = "🐍 Custom Python Agent (Recommended)"
        option1_value = "Custom Python Agent"
        option2_title = "⚡ n8n Workflow"
        option2_value = "n8n-only workflow"
    else:
        recommended = "n8n-only workflow"
        analysis_text = f"Your requirements (including: {user_answers[:100] if user_answers else 'the workflow aspects'}...) align well with n8n's strengths in API integrations, scheduled tasks, and connecting established services. This approach will be faster to implement and easier to maintain."
        option1_title = "⚡ n8n Workflow (Recommended)"
        option1_value = "n8n-only workflow"
        option2_title = "🐍 Custom Python Agent"
        option2_value = "Custom Python Agent"
    
    return FeasibilityResponse(
        text=analysis_text,
        option1_title=option1_title,
        option1_value=option1_value,
        option2_title=option2_title,
        option2_value=option2_value,
        recommended_option=recommended
    )
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


async def mock_generate_code(optimized_prompt: str) -> dict:
    """
    Station 4 - The Builder Agent: Mock function to simulate LLM code generation
    
    This is the most critical agent that must follow instructions with absolute precision.
    It generates production-grade code based on the technical specifications from the Architect.
    
    Mandates:
    - Follow system prompt with absolute precision
    - Generate production-grade, PEP 8 compliant Python code
    - NEVER hardcode sensitive information (use environment variables)
    - For n8n JSON, follow provided examples as strict schema and style guide
    - Generate syntactically valid and secure code
    
    TODO: Replace with actual LLM API integration
    """
    
    # n8n Few-Shot Examples for Context (prepended to n8n prompts)
    N8N_EXAMPLE_1 = """{
  "name": "Automated GitHub Scanner for Exposed AWS IAM Keys",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [
            {
              "triggerAtHour": 8,
              "unit": "days"
            }
          ]
        }
      },
      "name": "Run Daily at 8am",
      "type": "n8n-nodes-base.scheduleTrigger",
      "typeVersion": 1.1,
      "position": [460, 300],
      "id": "2784795e-a61f-4b0d-9541-118d3615469e"
    },
    {
      "parameters": {
        "operation": "list",
        "options": {}
      },
      "name": "List AWS Users",
      "type": "n8n-nodes-base.awsIam",
      "typeVersion": 1,
      "position": [700, 300],
      "id": "e0374e53-4809-4820-9467-331e1f13b19c",
      "credentials": {
        "aws": {
          "id": "YOUR_AWS_CREDENTIAL_ID",
          "name": "AWS Credentials"
        }
      }
    },
    {
      "parameters": {
        "batchSize": 1
      },
      "name": "Split Users for Processing",
      "type": "n8n-nodes-base.splitInBatches",
      "typeVersion": 2,
      "position": [920, 300],
      "id": "787c8801-689e-473d-88b1-3e5e31707963"
    },
    {
      "parameters": {
        "operation": "listAccessKeys",
        "userName": "={{ $('Split Users for Processing').item.json.UserName }}",
        "options": {}
      },
      "name": "Get User Access Keys",
      "type": "n8n-nodes-base.awsIam",
      "typeVersion": 1,
      "position": [1140, 300],
      "id": "c356942a-9216-43d9-959f-d312154c153f",
      "credentials": {
        "aws": {
          "id": "YOUR_AWS_CREDENTIAL_ID",
          "name": "AWS Credentials"
        }
      }
    },
    {
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{ $json.Status }}",
              "value2": "Active"
            }
          ]
        }
      },
      "name": "Filter Active Keys Only",
      "type": "n8n-nodes-base.if",
      "typeVersion": 1,
      "position": [1360, 300],
      "id": "f5d1e2a0-4c12-40e9-b5f7-679e96f8a8e3"
    },
    {
      "parameters": {
        "resource": "search",
        "operation": "code",
        "query": "={{ $json.AccessKeyId }}",
        "options": {}
      },
      "name": "Search GitHub for Exposed Keys",
      "type": "n8n-nodes-base.gitHub",
      "typeVersion": 3,
      "position": [1580, 200],
      "id": "a9b8e4d3-1d2a-4c8d-8e7c-a1f2b3c4d5e6",
      "credentials": {
        "gitHubApi": {
          "id": "YOUR_GITHUB_CREDENTIAL_ID",
          "name": "GitHub Credentials"
        }
      }
    }
  ],
  "connections": {
    "Run Daily at 8am": {
      "main": [
        [
          {
            "node": "List AWS Users",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "List AWS Users": {
      "main": [
        [
          {
            "node": "Split Users for Processing",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  },
  "pinData": {},
  "settings": {
    "executionOrder": "v1"
  },
  "staticData": null,
  "tags": [],
  "triggerCount": 0,
  "versionId": "f9a8b7c6-d5e4-f3a2-b1c0-d9e8f7a6b5c4"
}"""

    N8N_EXAMPLE_2 = """{
  "name": "Save n8n Workflows to GitHub",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [
            {
              "triggerAtHour": 2,
              "unit": "days"
            }
          ]
        }
      },
      "name": "Run Daily at 2am",
      "type": "n8n-nodes-base.scheduleTrigger",
      "typeVersion": 1.1,
      "position": [450, 350],
      "id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d"
    },
    {
      "parameters": {
        "url": "={{ $env.N8N_URL + 'api/v1/workflows' }}",
        "options": {}
      },
      "name": "Get All Workflows",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.1,
      "position": [690, 350],
      "id": "b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e",
      "credentials": {
        "httpHeaderAuth": {
          "id": "YOUR_N8N_API_KEY_CREDENTIAL_ID",
          "name": "n8n API Key"
        }
      }
    }
  ],
  "connections": {
    "Run Daily at 2am": {
      "main": [
        [
          {
            "node": "Get All Workflows",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  },
  "pinData": {},
  "settings": {
    "executionOrder": "v1"
  },
  "staticData": null,
  "tags": [],
  "triggerCount": 0,
  "versionId": "4d5e6f7a-8b9c-0d1e-2f3a-4b5c6d7e8f9a"
}"""

    N8N_EXAMPLE_3 = """{
  "name": "Monitor Multiple Github Repos via Webhook",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "github-webhook",
        "options": {}
      },
      "name": "Webhook Trigger",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1,
      "position": [440, 580],
      "webhookId": "f1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c",
      "id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d"
    },
    {
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{$json.headers['x-github-event']}}",
              "value2": "push"
            }
          ]
        }
      },
      "name": "Route by Event Type",
      "type": "n8n-nodes-base.if",
      "typeVersion": 1,
      "position": [1240, 580],
      "id": "e5f6a7b8-c9d0-4e1f-2a3b-4c5d6e7f8a9b"
    }
  ],
  "connections": {
    "Webhook Trigger": {
      "main": [
        [
          {
            "node": "Route by Event Type",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  },
  "pinData": {},
  "settings": {
    "executionOrder": "v1"
  },
  "staticData": null,
  "tags": [],
  "triggerCount": 1,
  "versionId": "4d5e6f7a-8b9c-0d1e-2f3a-4b5c6d7e8f9a"
}"""
    
    prompt_lower = optimized_prompt.lower()
    
    # Detect if this is an n8n workflow request
    if "n8n" in prompt_lower and "json" in prompt_lower:
        # For n8n workflows, prepend examples and generate JSON
        enhanced_prompt = f"""Here are three reference n8n workflow examples to follow as style and schema guides:

EXAMPLE 1: {N8N_EXAMPLE_1}

EXAMPLE 2: {N8N_EXAMPLE_2}

EXAMPLE 3: {N8N_EXAMPLE_3}

{optimized_prompt}

Generate syntactically valid n8n JSON that follows the exact structure and patterns shown in the examples above."""
        
        # Mock n8n workflow generation based on prompt content
        if "jira" in prompt_lower and "google sheet" in prompt_lower:
            return {
                "code": """{
  "name": "Jira to Google Sheets Sync",
  "nodes": [
    {
      "parameters": {
        "project": "PHOENIX",
        "events": ["jira:issue_created"],
        "options": {}
      },
      "name": "Jira Trigger - New Issue Created",
      "type": "n8n-nodes-base.jiraTrigger",
      "typeVersion": 1,
      "position": [440, 300],
      "id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
      "credentials": {
        "jiraApi": {
          "id": "YOUR_JIRA_CREDENTIAL_ID",
          "name": "Jira API Credentials"
        }
      }
    },
    {
      "parameters": {
        "operation": "appendRow",
        "documentId": "{{ $env.GOOGLE_SHEET_ID }}",
        "sheetName": "Q3 Planning",
        "columns": {
          "mappingMode": "defineBelow",
          "value": {
            "A": "={{ $json.fields.summary }}",
            "B": "={{ $json.key }}",
            "C": "={{ $json.fields.reporter.name }}"
          }
        },
        "options": {}
      },
      "name": "Add to Google Sheet",
      "type": "n8n-nodes-base.googleSheets",
      "typeVersion": 3,
      "position": [660, 300],
      "id": "b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e",
      "credentials": {
        "googleSheetsOAuth2": {
          "id": "YOUR_GOOGLE_SHEETS_CREDENTIAL_ID",
          "name": "Google Sheets OAuth2"
        }
      }
    }
  ],
  "connections": {
    "Jira Trigger - New Issue Created": {
      "main": [
        [
          {
            "node": "Add to Google Sheet",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  },
  "pinData": {},
  "settings": {
    "executionOrder": "v1"
  },
  "staticData": null,
  "tags": [],
  "triggerCount": 0,
  "versionId": "c1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e5f"
}""",
                "type": "n8n_workflow",
                "deployment": """1. Import this JSON into your n8n instance
2. Configure Jira API credentials with project access to 'PHOENIX'
3. Set up Google Sheets OAuth2 credentials with write access
4. Set environment variable GOOGLE_SHEET_ID to your target sheet ID
5. Activate the workflow
6. Test by creating a new issue in the PHOENIX Jira project"""
            }
        
        elif "github" in prompt_lower and "webhook" in prompt_lower:
            return {
                "code": """{
  "name": "GitHub Repository Monitor",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "github-webhook",
        "options": {}
      },
      "name": "GitHub Webhook Trigger",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1,
      "position": [440, 300],
      "webhookId": "github-monitor-webhook-id",
      "id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d"
    },
    {
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{$json.headers['x-github-event']}}",
              "value2": "push"
            }
          ]
        }
      },
      "name": "Filter Push Events",
      "type": "n8n-nodes-base.if",
      "typeVersion": 1,
      "position": [660, 300],
      "id": "b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e"
    },
    {
      "parameters": {
        "text": "=🔔 New push to *{{ $json.repository.full_name }}*\\n\\n*Commits:*\\n{{ $json.commits.map(c => `• ${c.message} by ${c.author.name}`).join('\\n') }}",
        "channel": "#github-activity",
        "options": {}
      },
      "name": "Send Slack Notification",
      "type": "n8n-nodes-base.slack",
      "typeVersion": 2,
      "position": [880, 300],
      "id": "c3d4e5f6-a7b8-4c9d-0e1f-2a3b4c5d6e7f",
      "credentials": {
        "slackApi": {
          "id": "YOUR_SLACK_CREDENTIAL_ID",
          "name": "Slack API Credentials"
        }
      }
    }
  ],
  "connections": {
    "GitHub Webhook Trigger": {
      "main": [
        [
          {
            "node": "Filter Push Events",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Filter Push Events": {
      "main": [
        [
          {
            "node": "Send Slack Notification",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  },
  "pinData": {},
  "settings": {
    "executionOrder": "v1"
  },
  "staticData": null,
  "tags": [],
  "triggerCount": 0,
  "versionId": "d4e5f6a7-b8c9-4d0e-1f2a-3b4c5d6e7f8a"
}""",
                "type": "n8n_workflow",
                "deployment": """1. Import this JSON into your n8n instance
2. Configure Slack API credentials with channel posting permissions
3. Note the webhook URL from the workflow
4. Set up GitHub webhook in your repository pointing to the n8n webhook URL
5. Configure webhook to send 'push' events
6. Activate the workflow and test with a git push"""
            }
        
        else:
            # Generic n8n workflow
            return {
                "code": """{
  "name": "Generic Automation Workflow",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [
            {
              "triggerAtHour": 9,
              "unit": "days"
            }
          ]
        }
      },
      "name": "Daily Trigger",
      "type": "n8n-nodes-base.scheduleTrigger",
      "typeVersion": 1.1,
      "position": [440, 300],
      "id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d"
    },
    {
      "parameters": {
        "url": "https://api.example.com/data",
        "options": {}
      },
      "name": "Fetch Data",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.1,
      "position": [660, 300],
      "id": "b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e"
    }
  ],
  "connections": {
    "Daily Trigger": {
      "main": [
        [
          {
            "node": "Fetch Data",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  },
  "pinData": {},
  "settings": {
    "executionOrder": "v1"
  },
  "staticData": null,
  "tags": [],
  "triggerCount": 0,
  "versionId": "e5f6a7b8-c9d0-4e1f-2a3b-4c5d6e7f8a9b"
}""",
                "type": "n8n_workflow",
                "deployment": """1. Import this JSON into your n8n instance
2. Configure any required API credentials
3. Modify the HTTP request URL and parameters as needed
4. Activate the workflow
5. Test the workflow manually or wait for the scheduled trigger"""
            }
    
    # Python FastAPI agent generation
    elif "fastapi" in prompt_lower or "python" in prompt_lower:
        # Generate production-grade Python FastAPI code
        if "github" in prompt_lower and "webhook" in prompt_lower:
            return {
                "code": '''"""
Production-Grade GitHub Webhook FastAPI Service
"""
import os
import hashlib
import hmac
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException, Header, Depends
from fastapi.responses import JSONResponse
import httpx
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app configuration
app = FastAPI(
    title="GitHub Webhook Handler",
    description="Production-grade GitHub webhook processing service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Pydantic models
class WebhookResponse(BaseModel):
    """Response model for webhook processing"""
    status: str = Field(..., description="Processing status")
    message: str = Field(..., description="Processing message")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Service health status")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Configuration
GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def verify_github_signature(payload: bytes, signature: str) -> bool:
    """
    Verify GitHub webhook signature for security
    
    Args:
        payload: Raw request payload
        signature: GitHub signature header
        
    Returns:
        bool: True if signature is valid
    """
    if not GITHUB_WEBHOOK_SECRET:
        logger.warning("GitHub webhook secret not configured")
        return False
        
    if not signature:
        return False
        
    # Remove 'sha256=' prefix
    expected_signature = signature.replace('sha256=', '')
    
    # Generate HMAC signature
    mac = hmac.new(
        GITHUB_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    )
    computed_signature = mac.hexdigest()
    
    return hmac.compare_digest(expected_signature, computed_signature)

async def send_slack_notification(message: str) -> bool:
    """
    Send notification to Slack
    
    Args:
        message: Message to send
        
    Returns:
        bool: True if successful
    """
    if not SLACK_WEBHOOK_URL:
        logger.error("Slack webhook URL not configured")
        return False
        
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                SLACK_WEBHOOK_URL,
                json={"text": message},
                timeout=10.0
            )
            response.raise_for_status()
            logger.info("Slack notification sent successfully")
            return True
            
    except Exception as e:
        logger.error(f"Failed to send Slack notification: {e}")
        return False

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(status="healthy")

@app.post("/webhook", response_model=WebhookResponse)
async def github_webhook(
    request: Request,
    x_github_event: Optional[str] = Header(None),
    x_hub_signature_256: Optional[str] = Header(None)
):
    """
    GitHub webhook endpoint
    
    Processes GitHub webhook events with signature verification
    and sends notifications to Slack
    """
    try:
        # Get raw payload for signature verification
        payload = await request.body()
        
        # Verify GitHub signature
        if not verify_github_signature(payload, x_hub_signature_256):
            logger.warning("Invalid GitHub webhook signature")
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse JSON payload
        try:
            data = await request.json()
        except Exception as e:
            logger.error(f"Failed to parse JSON payload: {e}")
            raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
        # Process different event types
        if x_github_event == "push":
            await handle_push_event(data)
        elif x_github_event == "pull_request":
            await handle_pull_request_event(data)
        else:
            logger.info(f"Unhandled event type: {x_github_event}")
        
        return WebhookResponse(
            status="success",
            message=f"Processed {x_github_event} event successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        raise HTTPException(status_code=500, detail="Internal processing error")

async def handle_push_event(data: Dict[str, Any]) -> None:
    """Handle GitHub push events"""
    try:
        repository = data.get("repository", {})
        commits = data.get("commits", [])
        
        if not commits:
            return
            
        repo_name = repository.get("full_name", "Unknown Repository")
        commit_messages = [
            f"• {commit.get('message', 'No message')} by {commit.get('author', {}).get('name', 'Unknown')}"
            for commit in commits[:5]  # Limit to 5 commits
        ]
        
        message = f"""🔔 New push to *{repo_name}*

*Commits:*
{chr(10).join(commit_messages)}
        
*Branch:* {data.get('ref', '').replace('refs/heads/', '')}
*Pusher:* {data.get('pusher', {}).get('name', 'Unknown')}"""
        
        await send_slack_notification(message)
        logger.info(f"Processed push event for {repo_name}")
        
    except Exception as e:
        logger.error(f"Error handling push event: {e}")

async def handle_pull_request_event(data: Dict[str, Any]) -> None:
    """Handle GitHub pull request events"""
    try:
        action = data.get("action")
        pull_request = data.get("pull_request", {})
        repository = data.get("repository", {})
        
        if action not in ["opened", "closed", "merged"]:
            return
            
        repo_name = repository.get("full_name", "Unknown Repository")
        pr_title = pull_request.get("title", "No title")
        pr_number = pull_request.get("number", "Unknown")
        pr_url = pull_request.get("html_url", "")
        author = pull_request.get("user", {}).get("login", "Unknown")
        
        message = f"""📋 Pull Request {action} in *{repo_name}*

*PR #{pr_number}:* {pr_title}
*Author:* {author}
*Action:* {action}
*URL:* {pr_url}"""
        
        await send_slack_notification(message)
        logger.info(f"Processed PR {action} event for {repo_name}")
        
    except Exception as e:
        logger.error(f"Error handling pull request event: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        log_level="info"
    )''',
                "type": "python_agent",
                "deployment": """1. Install dependencies:
   pip install fastapi uvicorn httpx pydantic

2. Set environment variables:
   export GITHUB_WEBHOOK_SECRET="your_github_webhook_secret"
   export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
   export PORT=8000

3. Run the service:
   uvicorn main:app --host 0.0.0.0 --port 8000

4. Configure GitHub webhook:
   - URL: https://your-domain.com/webhook
   - Content type: application/json
   - Secret: same as GITHUB_WEBHOOK_SECRET
   - Events: pushes, pull requests

5. Test the webhook:
   - Make a commit to trigger push event
   - Create/close a PR to trigger PR events

6. Production deployment:
   - Use a reverse proxy (nginx)
   - Enable HTTPS
   - Set up monitoring and logging
   - Consider rate limiting"""
            }
        
        elif "security" in prompt_lower or "vulnerability" in prompt_lower:
            return {
                "code": '''"""
Production-Grade Security Vulnerability Scanner FastAPI Service
"""
import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import JSONResponse
import httpx
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Security Vulnerability Scanner",
    description="Production-grade vulnerability scanning for GitHub PRs",
    version="1.0.0"
)

# Pydantic models
class ScanResult(BaseModel):
    """Vulnerability scan result"""
    status: str = Field(..., description="Scan status: pass/fail")
    vulnerabilities_found: int = Field(..., description="Number of vulnerabilities")
    critical_count: int = Field(..., description="Critical vulnerabilities")
    high_count: int = Field(..., description="High severity vulnerabilities")
    message: str = Field(..., description="Scan result message")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class Vulnerability(BaseModel):
    """Individual vulnerability details"""
    package: str = Field(..., description="Vulnerable package name")
    version: str = Field(..., description="Package version")
    severity: str = Field(..., description="Vulnerability severity")
    cve_id: Optional[str] = Field(None, description="CVE identifier")
    description: str = Field(..., description="Vulnerability description")

# Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OSV_API_URL = "https://api.osv.dev/v1/query"

async def get_file_content(repo: str, path: str, ref: str) -> Optional[str]:
    """
    Get file content from GitHub repository
    
    Args:
        repo: Repository in format "owner/repo"
        path: File path in repository
        ref: Git reference (commit SHA, branch, etc.)
        
    Returns:
        File content as string or None if not found
    """
    if not GITHUB_TOKEN:
        logger.error("GitHub token not configured")
        return None
        
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3.raw"
    }
    params = {"ref": ref}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params, timeout=30.0)
            if response.status_code == 200:
                return response.text
            elif response.status_code == 404:
                logger.info(f"File {path} not found in {repo}")
                return None
            else:
                response.raise_for_status()
                
    except Exception as e:
        logger.error(f"Error fetching file {path} from {repo}: {e}")
        return None

async def parse_requirements(content: str) -> List[Dict[str, str]]:
    """
    Parse requirements.txt content to extract packages
    
    Args:
        content: Requirements file content
        
    Returns:
        List of package dictionaries with name and version
    """
    packages = []
    
    for line in content.strip().split('\\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
            
        # Handle different requirement formats
        if '>=' in line:
            name, version = line.split('>=', 1)
        elif '==' in line:
            name, version = line.split('==', 1)
        elif '~=' in line:
            name, version = line.split('~=', 1)
        else:
            # No version specified
            name = line.split('[')[0]  # Remove extras
            version = "latest"
            
        packages.append({
            "name": name.strip(),
            "version": version.strip()
        })
    
    return packages

async def check_vulnerability(package: str, version: str) -> List[Vulnerability]:
    """
    Check package for vulnerabilities using OSV API
    
    Args:
        package: Package name
        version: Package version
        
    Returns:
        List of vulnerabilities found
    """
    query = {
        "package": {
            "name": package,
            "ecosystem": "PyPI"
        }
    }
    
    if version != "latest":
        query["version"] = version
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                OSV_API_URL,
                json=query,
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            
            vulnerabilities = []
            for vuln in data.get("vulns", []):
                # Determine severity
                severity = "UNKNOWN"
                for affected in vuln.get("affected", []):
                    severity_info = affected.get("database_specific", {}).get("severity")
                    if severity_info:
                        severity = severity_info
                        break
                
                vulnerabilities.append(Vulnerability(
                    package=package,
                    version=version,
                    severity=severity,
                    cve_id=vuln.get("id"),
                    description=vuln.get("summary", "No description available")[:200]
                ))
            
            return vulnerabilities
            
    except Exception as e:
        logger.error(f"Error checking vulnerability for {package}: {e}")
        return []

async def post_github_comment(repo: str, pr_number: int, comment: str) -> bool:
    """
    Post comment to GitHub PR
    
    Args:
        repo: Repository in format "owner/repo"
        pr_number: Pull request number
        comment: Comment text
        
    Returns:
        True if successful
    """
    if not GITHUB_TOKEN:
        logger.error("GitHub token not configured")
        return False
        
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=headers,
                json={"body": comment},
                timeout=30.0
            )
            response.raise_for_status()
            logger.info(f"Posted comment to PR #{pr_number} in {repo}")
            return True
            
    except Exception as e:
        logger.error(f"Error posting comment to PR #{pr_number}: {e}")
        return False

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.post("/webhook", response_model=ScanResult)
async def vulnerability_scan_webhook(request: Request):
    """
    GitHub webhook endpoint for vulnerability scanning
    
    Scans requirements.txt changes in pull requests for security vulnerabilities
    """
    try:
        data = await request.json()
        
        # Only process pull request opened events
        if data.get("action") != "opened":
            return ScanResult(
                status="skipped",
                vulnerabilities_found=0,
                critical_count=0,
                high_count=0,
                message="Not a PR opened event"
            )
        
        pr = data.get("pull_request", {})
        repo = data.get("repository", {}).get("full_name")
        pr_number = pr.get("number")
        head_sha = pr.get("head", {}).get("sha")
        
        if not all([repo, pr_number, head_sha]):
            raise HTTPException(status_code=400, detail="Missing required PR data")
        
        # Get changed files
        changed_files = []
        if "requirements.txt" in str(data):  # Simple check for demo
            changed_files.append("requirements.txt")
        
        if "requirements.txt" not in changed_files:
            return ScanResult(
                status="pass",
                vulnerabilities_found=0,
                critical_count=0,
                high_count=0,
                message="requirements.txt not modified"
            )
        
        # Get requirements.txt content
        content = await get_file_content(repo, "requirements.txt", head_sha)
        if not content:
            return ScanResult(
                status="pass",
                vulnerabilities_found=0,
                critical_count=0,
                high_count=0,
                message="requirements.txt not found"
            )
        
        # Parse packages
        packages = await parse_requirements(content)
        
        # Scan for vulnerabilities
        all_vulnerabilities = []
        critical_count = 0
        high_count = 0
        
        for package in packages:
            vulns = await check_vulnerability(package["name"], package["version"])
            all_vulnerabilities.extend(vulns)
            
            for vuln in vulns:
                if vuln.severity in ["CRITICAL"]:
                    critical_count += 1
                elif vuln.severity in ["HIGH"]:
                    high_count += 1
        
        # Determine scan status
        status = "fail" if (critical_count > 0 or high_count > 0) else "pass"
        
        # Post comment if vulnerabilities found
        if status == "fail":
            comment = f"""🚨 **Security Vulnerability Scan Results**

Found {len(all_vulnerabilities)} vulnerabilities in requirements.txt:
- Critical: {critical_count}
- High: {high_count}

**Vulnerable packages:**
"""
            for vuln in all_vulnerabilities[:5]:  # Limit to 5 for readability
                comment += f"- **{vuln.package}** ({vuln.version}): {vuln.severity}\\n"
                if vuln.cve_id:
                    comment += f"  CVE: {vuln.cve_id}\\n"
                comment += f"  {vuln.description[:100]}...\\n\\n"
            
            await post_github_comment(repo, pr_number, comment)
        
        return ScanResult(
            status=status,
            vulnerabilities_found=len(all_vulnerabilities),
            critical_count=critical_count,
            high_count=high_count,
            message=f"Scan completed. Found {len(all_vulnerabilities)} vulnerabilities."
        )
        
    except Exception as e:
        logger.error(f"Vulnerability scan error: {e}")
        raise HTTPException(status_code=500, detail="Scan processing error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))''',
                "type": "python_agent",
                "deployment": """1. Install dependencies:
   pip install fastapi uvicorn httpx pydantic

2. Set environment variables:
   export GITHUB_TOKEN="your_github_personal_access_token"
   export PORT=8000

3. Run the service:
   uvicorn main:app --host 0.0.0.0 --port 8000

4. Configure GitHub webhook:
   - URL: https://your-domain.com/webhook
   - Content type: application/json
   - Events: pull requests

5. GitHub token permissions needed:
   - repo (for accessing repository content)
   - pull requests (for posting comments)

6. Test the service:
   - Create a PR that modifies requirements.txt
   - Service will scan for vulnerabilities and comment on high/critical findings

7. Production considerations:
   - Use proper secrets management
   - Implement rate limiting
   - Add monitoring and alerting
   - Consider caching OSV API responses"""
            }
        
        else:
            # Generic Python FastAPI service
            return {
                "code": '''"""
Production-Grade FastAPI Microservice
"""
import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app configuration
app = FastAPI(
    title="Microservice API",
    description="Production-grade FastAPI microservice",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service health status")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = Field("1.0.0", description="Service version")

class ProcessRequest(BaseModel):
    """Generic processing request"""
    data: Dict[str, Any] = Field(..., description="Request data")
    options: Optional[Dict[str, Any]] = Field(None, description="Processing options")

class ProcessResponse(BaseModel):
    """Generic processing response"""
    status: str = Field(..., description="Processing status")
    result: Dict[str, Any] = Field(..., description="Processing result")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Configuration
API_KEY = os.getenv("API_KEY")
SERVICE_URL = os.getenv("SERVICE_URL", "https://api.example.com")

async def validate_api_key(api_key: Optional[str] = None) -> bool:
    """
    Validate API key for authentication
    
    Args:
        api_key: API key to validate
        
    Returns:
        True if valid
    """
    if not API_KEY:
        logger.warning("API key not configured")
        return True  # Allow if not configured
        
    return api_key == API_KEY

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    
    Returns service health status and basic information
    """
    return HealthResponse(status="healthy")

@app.post("/process", response_model=ProcessResponse)
async def process_data(
    request: ProcessRequest,
    api_key_valid: bool = Depends(validate_api_key)
):
    """
    Generic data processing endpoint
    
    Processes incoming data according to specified options
    """
    try:
        if not api_key_valid:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        # Process the data
        result = await process_business_logic(request.data, request.options or {})
        
        return ProcessResponse(
            status="success",
            result=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Processing error: {e}")
        raise HTTPException(status_code=500, detail="Internal processing error")

async def process_business_logic(data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main business logic processing function
    
    Args:
        data: Input data to process
        options: Processing options
        
    Returns:
        Processed result
    """
    try:
        # Implement your business logic here
        processed_data = {
            "input_received": data,
            "processing_options": options,
            "processed_at": datetime.utcnow().isoformat(),
            "result": "Processing completed successfully"
        }
        
        # Example external API call
        if options.get("call_external_api"):
            external_result = await call_external_service(data)
            processed_data["external_result"] = external_result
        
        return processed_data
        
    except Exception as e:
        logger.error(f"Business logic error: {e}")
        raise

async def call_external_service(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call external service API
    
    Args:
        data: Data to send to external service
        
    Returns:
        External service response
    """
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('EXTERNAL_API_TOKEN', 'token')}"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{SERVICE_URL}/api/process",
                json=data,
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
            
    except httpx.HTTPError as e:
        logger.error(f"External API error: {e}")
        raise HTTPException(status_code=502, detail="External service error")
    except Exception as e:
        logger.error(f"Unexpected error calling external service: {e}")
        raise HTTPException(status_code=500, detail="Service communication error")

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler"""
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint not found", "timestamp": datetime.utcnow().isoformat()}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Custom 500 handler"""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "timestamp": datetime.utcnow().isoformat()}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        log_level="info"
    )''',
                "type": "python_agent",
                "deployment": """1. Install dependencies:
   pip install fastapi uvicorn httpx pydantic

2. Set environment variables:
   export API_KEY="your_secure_api_key"
   export SERVICE_URL="https://api.example.com"
   export EXTERNAL_API_TOKEN="external_service_token"
   export PORT=8000

3. Run the service:
   uvicorn main:app --host 0.0.0.0 --port 8000

4. Test the service:
   curl -X GET http://localhost:8000/health
   curl -X POST http://localhost:8000/process \\
     -H "Content-Type: application/json" \\
     -d '{"data": {"test": "value"}, "options": {"call_external_api": false}}'

5. Production deployment:
   - Use environment-specific configurations
   - Set up proper logging and monitoring
   - Configure CORS appropriately
   - Use HTTPS in production
   - Implement rate limiting and authentication
   - Set up health checks and metrics"""
            }
    
    # Fallback for unclear requests
    else:
        return {
            "code": "# Unable to determine code type from prompt\n# Please specify either 'n8n workflow' or 'Python FastAPI' in your request",
            "type": "unknown",
            "deployment": "Please clarify whether you need an n8n workflow or Python FastAPI service"
        }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
