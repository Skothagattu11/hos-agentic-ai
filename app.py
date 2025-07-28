from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import subprocess
import sys
import os
import json
import logging
from typing import Optional
import uvicorn
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
# Check multiple locations for .env file
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
env_locations = [
    current_dir / ".env",
    parent_dir / ".env",
    Path.cwd() / ".env"
]

env_loaded = False
for env_path in env_locations:
    if env_path.exists():
        load_dotenv(env_path)
        env_loaded = True
        print(f"[DEBUG] Loaded .env from: {env_path}")
        break

if not env_loaded:
    print("[DEBUG] No .env file found. Please create one using env.example as template.")
    load_dotenv()  # Load from system environment

# Configure logging with Unicode support for Windows
import codecs
import sys

# Fix logging Unicode issues
class SafeFileHandler(logging.FileHandler):
    def __init__(self, filename, mode='a', encoding='utf-8', delay=False):
        super().__init__(filename, mode, encoding='utf-8', delay=delay)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        SafeFileHandler('health_analysis_api.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Health Analysis API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class AnalysisRequest(BaseModel):
    user_id: str
    archetype: str

class HealthCheckResponse(BaseModel):
    status: str
    message: str

# Store active analysis processes
active_processes = {}

@app.get("/", response_model=HealthCheckResponse)
async def root():
    return HealthCheckResponse(status="healthy", message="Health Analysis API is running")

@app.get("/api/health", response_model=HealthCheckResponse)
async def health_check():
    return HealthCheckResponse(status="healthy", message="API is operational")

@app.post("/api/analyze")
async def start_analysis(request: AnalysisRequest):
    """Start health analysis and return real-time updates via Server-Sent Events"""
    
    logger.info(f"=== ANALYSIS REQUEST STARTED ===")
    logger.info(f"User ID: {request.user_id}")
    logger.info(f"Archetype: {request.archetype}")
    
    # Validate inputs
    if not request.user_id.strip():
        logger.error("Validation failed: User ID is empty")
        raise HTTPException(status_code=400, detail="User ID is required")
    
    if not request.archetype.strip():
        logger.error("Validation failed: Archetype is empty")
        raise HTTPException(status_code=400, detail="Archetype is required")
    
    # Set up environment variables - ensure they're passed to subprocess
    env = os.environ.copy()
    
    # Add Python Unicode environment variables to handle emoji characters
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    
    # Check for database connection options (Supabase or PostgreSQL)
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    database_url = os.getenv("DATABASE_URL")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    # Check for required environment variables - need either Supabase or DATABASE_URL
    logger.info(f"Environment check - OPENAI_API_KEY: {'Present' if openai_api_key else 'Missing'}")
    logger.info(f"Environment check - SUPABASE_URL: {'Present' if supabase_url else 'Missing'}")
    logger.info(f"Environment check - SUPABASE_KEY: {'Present' if supabase_key else 'Missing'}")
    logger.info(f"Environment check - DATABASE_URL: {'Present' if database_url else 'Missing'}")
    
    if not openai_api_key:
        logger.error("OPENAI_API_KEY not configured")
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured. Please check your .env file.")
    
    if not (supabase_url and supabase_key) and not database_url:
        logger.error("No database connection configured")
        raise HTTPException(
            status_code=500, 
            detail="Database connection not configured. Please provide either (SUPABASE_URL + SUPABASE_KEY) or DATABASE_URL in your .env file."
        )
    
    # Pass all available credentials to subprocess
    if supabase_url and supabase_key:
        env["SUPABASE_URL"] = supabase_url
        env["SUPABASE_KEY"] = supabase_key
    if database_url:
        env["DATABASE_URL"] = database_url
    env["OPENAI_API_KEY"] = openai_api_key
    
    # Log environment variables for debugging (without exposing sensitive data)
    logger.info(f"SUPABASE_URL set: {'Yes' if supabase_url else 'No'}")
    logger.info(f"SUPABASE_KEY set: {'Yes' if supabase_key else 'No'}")
    logger.info(f"DATABASE_URL set: {'Yes' if database_url else 'No'}")
    logger.info(f"OPENAI_API_KEY set: {'Yes' if openai_api_key else 'No'}")
    
    async def generate_analysis_stream():
        process = None
        try:
            logger.info("=== STARTING SUBPROCESS ===")
            # Start the Python analysis process with comprehensive Unicode handling
            cmd = [sys.executable, "main_api.py", request.user_id, request.archetype]
            logger.info(f"Command: {' '.join(cmd)}")
            logger.info(f"Working directory: {os.getcwd()}")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                env=env,  # Pass environment variables to subprocess
                encoding='utf-8',
                errors='replace'  # Replace problematic characters instead of failing
            )
            
            logger.info(f"Process started with PID: {process.pid}")
            
            # Store the process
            process_id = id(process)
            active_processes[process_id] = process
            
            # Send initial status
            logger.info("Sending initial status to client")
            yield f"data: {json.dumps({'type': 'status', 'message': 'Analysis started', 'stage': 'initializing'})}\n\n"
            
            # Read output line by line
            logger.info("Starting to read subprocess output")
            line_count = 0
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    logger.info(f"Subprocess ended, total lines processed: {line_count}")
                    break
                if output:
                    line = output.strip()
                    line_count += 1
                    
                    # Log all subprocess output to server logs (safely, without emoji)
                    safe_line = line.encode('ascii', errors='ignore').decode('ascii')
                    logger.info(f"Subprocess[{line_count}]: {safe_line[:100]}")
                    
                    # Only send major steps to user response
                    if line and should_include_in_response(line):
                        # Clean line for user display
                        clean_line = clean_line_for_response(line)
                        stage = determine_stage(clean_line)
                        
                        logger.info(f"→ User Response: {stage} - {clean_line[:50]}")
                        
                        # Send clean output to frontend
                        yield f"data: {json.dumps({'type': 'output', 'message': clean_line, 'stage': stage})}\n\n"
                        
                        await asyncio.sleep(0.1)
            
            # Wait for process to complete
            return_code = process.wait()
            logger.info(f"Subprocess completed with return code: {return_code}")
            
            if return_code == 0:
                logger.info("Analysis completed successfully")
                yield f"data: {json.dumps({'type': 'complete', 'message': 'Analysis completed successfully', 'stage': 'completed'})}\n\n"
            else:
                # Get error output
                error_output = process.stderr.read()
                safe_error = error_output.encode('ascii', errors='ignore').decode('ascii') if error_output else "Unknown error"
                
                logger.error(f"Analysis failed with return code {return_code}")
                logger.error(f"Error details: {safe_error}")
                
                # Send user-friendly error message
                user_error = "Analysis failed. Please check your configuration and try again."
                yield f"data: {json.dumps({'type': 'error', 'message': user_error, 'stage': 'error'})}\n\n"
            
        except Exception as e:
            logger.error(f"Exception during analysis stream: {str(e)}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'message': f'Server error: {str(e)}', 'stage': 'error'})}\n\n"
        
        finally:
            # Clean up
            logger.info("=== CLEANUP PHASE ===")
            if process:
                try:
                    logger.info(f"Terminating process PID: {process.pid}")
                    process.terminate()
                    process.wait(timeout=5)
                    logger.info("Process terminated gracefully")
                except Exception as cleanup_error:
                    logger.warning(f"Force killing process: {cleanup_error}")
                    process.kill()
                
                process_id = id(process)
                active_processes.pop(process_id, None)
                logger.info(f"Removed process {process_id} from active processes")
            
            logger.info("=== ANALYSIS REQUEST COMPLETED ===")
            logger.info(f"Active processes remaining: {len(active_processes)}")
    
    return StreamingResponse(
        generate_analysis_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )

def clean_line_for_response(line: str) -> str:
    """Clean line for user-friendly response - remove emoji and internal details"""
    import re
    
    # Remove emoji characters
    line = re.sub(r'[^\x00-\x7F]+', '', line)
    
    # Replace technical markers with user-friendly messages
    replacements = {
        "[CONNECTING]": "Connecting to database...",
        "[SUCCESS]": "✓",
        "[ERROR]": "✗", 
        "[WARNING]": "!",
        "Query fetch failed": "Database query in progress...",
        "Connected to Supabase successfully": "Database connected",
        "Connected via Supabase adapter": "Database connection established"
    }
    
    for old, new in replacements.items():
        line = line.replace(old, new)
    
    return line.strip()

def should_include_in_response(line: str) -> bool:
    """Filter what goes to the user response - only major steps"""
    line_lower = line.lower()
    
    # Skip technical details, internal logs, emoji errors
    skip_terms = [
        "query fetch failed", "connected to supabase successfully", 
        "connected via supabase adapter", "environment variable",
        "logging", "memory updated", "saved to memory",
        "debug", "loaded .env", "pid:", "process"
    ]
    
    if any(skip in line_lower for skip in skip_terms):
        return False
    
    # Include major user-facing steps
    include_terms = [
        "starting health analysis", "selected archetype", "initializing",
        "comprehensive health analysis", "behavior analysis", 
        "nutrition plan", "routine plan", "analysis complete",
        "error during analysis", "failed"
    ]
    
    return any(term in line_lower for term in include_terms)

def determine_stage(line: str) -> str:
    """Determine the analysis stage based on output content"""
    line_lower = line.lower()
    
    if "welcome to the health analysis system" in line_lower:
        return "initialization"
    elif "select your routine plan archetype" in line_lower:
        return "archetype_selection"
    elif "selected:" in line_lower:
        return "archetype_confirmed"
    elif "analyzing user profile" in line_lower or "profile analysis" in line_lower:
        return "profile_analysis"
    elif "health analysis" in line_lower:
        return "health_analysis"
    elif "behavior analysis" in line_lower:
        return "behavior_analysis"
    elif "nutrition plan" in line_lower:
        return "nutrition_planning"
    elif "routine plan" in line_lower:
        return "routine_planning"
    elif "generating" in line_lower:
        return "generating_plans"
    elif "completed" in line_lower or "finished" in line_lower:
        return "completed"
    elif "error" in line_lower:
        return "error"
    else:
        return "processing"

@app.get("/api/status")
async def get_status():
    """Get current API status and active processes"""
    return {
        "status": "running",
        "active_processes": len(active_processes),
        "timestamp": "2024-01-01T00:00:00Z"
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 