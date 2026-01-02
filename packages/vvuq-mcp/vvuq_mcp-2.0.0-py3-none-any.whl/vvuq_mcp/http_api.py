"""
VVUQ-MCP HTTP API Server

FastAPI server exposing VVUQ verification services via REST endpoints.
Provides a production-ready HTTP API for marketplace integration.
"""

import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, AsyncIterator, NoReturn
import httpx

from fastapi import FastAPI, HTTPException, status, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# Load environment
load_dotenv()

# Import VVUQ components
from vvuq_mcp.storage.neo4j_client import VVUQStorage
from vvuq_mcp.verifiers.lean4 import Lean4Verifier
from vvuq_mcp.models import Contract, ContractClaim, VerificationAttempt
from vvuq_mcp.auth import verify_api_key
from vvuq_mcp.secret_manager import get_secret
# Note: Payment ledger not yet implemented, stubbed for now

# Rate Limiter Configuration
limiter = Limiter(key_func=get_remote_address)



# Pydantic Models for API
class ClaimModel(BaseModel):
    """Model for a verification claim"""
    theorem: str = Field(..., description="Theorem statement in Lean4")
    allowed_imports: List[str] = Field(
        default=[
            "Mathlib.Data.Nat.Basic", 
            "Mathlib.Algebra.Field.Basic", 
            "Mathlib.Algebra.Ring.Basic"
        ],
        description="List of allowed Lean4 imports"
    )
    mathlib_version: Optional[str] = Field(
        default=None,
        description="Mathlib4 git tag or commit hash (e.g., 'v4.15.0' or 40-char hash).",
        pattern=r"^v\d+\.\d+\.\d+(-[a-zA-Z0-9]+)?$|^[a-f0-9]{40}$"
    )
    assumption_contexts: List[str] = Field(
        default_factory=list,
        description="List of assumed context modules (e.g. ['Physics:v1.0.0'])"
    )


class ContractCreateRequest(BaseModel):
    """Request model for creating a contract"""
    title: str = Field(..., max_length=200, description="Contract title")
    description: str = Field(..., description="Contract description")
    claims: List[ClaimModel] = Field(..., description="List of claims to verify")
    issuer_agent_id: str = Field(..., description="Agent creating the contract")


class ContractCreateResponse(BaseModel):
    """Response model for contract creation"""
    success: bool
    contract_id: str
    message: str


class ProofSubmitRequest(BaseModel):
    """Request model for proof submission"""
    contract_id: str = Field(..., description="Contract ID")
    prover_agent_id: str = Field(..., description="Agent submitting proof")
    proof_code: str = Field(..., description="Lean4 proof code")
    proof_claim_index: int = Field(default=0, description="Index of claim being proven")


class ProofSubmitResponse(BaseModel):
    """Response model for proof submission"""
    verdict: str = Field(..., description="ACCEPTED, REJECTED, or ERROR")
    contract_id: str
    prover_agent_id: str
    verification_time_ms: float
    compilation_output: Optional[str] = None
    errors: List[str] = Field(default_factory=list)


class PaymentProcessRequest(BaseModel):
    """Request model for payment processing"""
    contract_id: str = Field(..., description="Contract ID")


class PaymentProcessResponse(BaseModel):
    """Response model for payment processing"""
    success: bool
    payment_id: str
    amount: float
    from_agent: str
    to_agent: str
    timestamp: str


class VerificationHistoryResponse(BaseModel):
    """Response model for verification history"""
    contract_id: str
    attempts: List[Dict[str, Any]]


class FeedbackRequest(BaseModel):
    """Request model for submitting feedback"""
    title: str = Field(..., max_length=100, description="Brief feedback title")
    description: str = Field(..., description="Detailed feedback description")
    feedback_type: str = Field(..., pattern="^(bug|feature_request|improvement|performance|documentation|security|usability|general)$")
    severity: str = Field(..., pattern="^(critical|high|medium|low)$")
    tool_name: Optional[str] = Field(None, description="Related endpoint or tool name")
    reproduction_steps: Optional[str] = Field(None, description="Steps to reproduce (for bugs)")
    expected_behavior: Optional[str] = Field(None, description="Expected behavior (for bugs)")
    actual_behavior: Optional[str] = Field(None, description="Actual behavior (for bugs)")
    test_criteria: Optional[str] = Field(None, description="How to verify the fix")
    submitter_type: str = Field(default="person", pattern="^(person|agent|automated_system)$")
    contact_info: Optional[str] = Field(None, description="Contact info for follow-up")


class FeedbackResponse(BaseModel):
    """Response model for feedback submission"""
    success: bool
    feedback_id: str
    message: str
    github_issue_created: bool = False



# Application state
class AppState:
    """Application state holder"""
    storage: Optional[VVUQStorage] = None
    verifier: Optional[Lean4Verifier] = None


app_state = AppState()


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Initialize and cleanup application resources"""
    # Startup
    print("🚀 Starting VVUQ-MCP HTTP API Server...")
    
    # Initialize storage
    app_state.storage = VVUQStorage(
        uri=os.getenv("NEO4J_URI"),
        user=os.getenv("NEO4J_USER"),
        password=os.getenv("NEO4J_PASSWORD")
    )
    
    # Initialize verifier with project's Lean workspace (has Mathlib configured)
    project_root = Path(__file__).parent.parent.parent
    default_workspace = project_root / "lean-workspace"
    workspace_dir = Path(os.getenv("LEAN_WORKSPACE", str(default_workspace)))
    
    if not workspace_dir.exists():
        raise RuntimeError(f"Lean workspace not found at {workspace_dir}. "
                          f"Please ensure the lean-workspace directory exists with Mathlib configured.")
    
    app_state.verifier = Lean4Verifier(workspace_dir=workspace_dir)
    
    
    print("✅ VVUQ-MCP HTTP API Server ready!")
    print(f"   Storage: Connected to Neo4j")
    print(f"   Verifier: Lean4 workspace at {workspace_dir}")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down VVUQ-MCP HTTP API Server...")
    if app_state.storage:
        await app_state.storage.close()
    print("✅ Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="VVUQ-MCP API",
    description="Verification, Validation & Uncertainty Quantification - HTTP API",
    version="1.0.0",
    lifespan=lifespan
)

# Initialize Rate Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Add CORS middleware with secure configuration
# Load allowed origins from environment variable
allowed_origins = os.getenv(
    "VVUQ_ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:8000"  # Safe defaults for development
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Specific origins only, no wildcard
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Specific methods only
    allow_headers=["Content-Type", "Authorization"],  # Specific headers only
)

# Add rate limiting middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)


# Health check endpoint
@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "vvuq-mcp",
        "version": "1.0.0",
        "storage_connected": app_state.storage is not None,
        "verifier_ready": app_state.verifier is not None,
        "ledger_ready": False is not None
    }


# Contract endpoints
@app.post("/contracts", response_model=ContractCreateResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("200/minute")  # Rate limit: 200 contracts per minute per IP
async def create_contract(request: Request, contract_request: ContractCreateRequest, api_key: str = Depends(verify_api_key)) -> ContractCreateResponse:
    """
    Create a new verification contract.
    
    This endpoint creates a contract with one or more claims that need to be proven.
    """
    if not app_state.storage:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Storage not initialized"
        )
    
    try:
        # Generate unique contract ID
        contract_id = f"contract_{uuid.uuid4().hex[:12]}"
        
        # Convert claims to ContractClaim objects
        contract_claims = [
            ContractClaim(
                claim_id=idx + 1,
                theorem_statement=claim.theorem,
                allowed_dependencies=claim.allowed_imports,
                payment_amount=getattr(claim, 'payment_amount', 1.0),
                payment_type=getattr(claim, 'payment_type', 'all-or-nothing'),
                mathlib_version=claim.mathlib_version,
                assumption_contexts=claim.assumption_contexts
            )
            for idx, claim in enumerate(contract_request.claims)
        ]
        
        # Create Contract object
        contract = Contract(
            contract_id=contract_id,
            title=contract_request.title,
            description=contract_request.description,
            claims=contract_claims,
            issuer_agent_id=contract_request.issuer_agent_id,
            status="OPEN"
        )
        
        # Store contract
        returned_id = await app_state.storage.store_contract(contract)

        
        return ContractCreateResponse(
            success=True,
            contract_id=contract_id,
            message=f"Contract '{contract_request.title}' created successfully"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create contract: {str(e)}"
        )


@app.get("/contracts/{contract_id}")
async def get_contract(contract_id: str, api_key: str = Depends(verify_api_key)) -> Contract:
    """Get contract details by ID"""
    if not app_state.storage:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Storage not initialized"
        )
    
    try:
        contract = await app_state.storage.get_contract(contract_id)
        if not contract:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Contract {contract_id} not found"
            )
        return contract
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve contract: {str(e)}"
        )


# Proof submission endpoint
@app.post("/proofs/submit", response_model=ProofSubmitResponse)
@limiter.limit("100/minute")  # Rate limit: 100 proofs per minute per IP
async def submit_proof(request: Request, proof_request: ProofSubmitRequest, api_key: str = Depends(verify_api_key)) -> ProofSubmitResponse:
    """
    Submit a Lean4 proof for verification.
    
    This is the main verification endpoint. It compiles the proof,
    checks it against the contract claim, and returns the verdict.
    """
    if not app_state.verifier or not app_state.storage:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Services not initialized"
        )
    
    try:
        # Get contract to retrieve claim
        contract = await app_state.storage.get_contract(proof_request.contract_id)
        if not contract:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Contract {proof_request.contract_id} not found"
            )
        
        # Get the claim being proven
        if proof_request.proof_claim_index >= len(contract.claims):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Claim index {proof_request.proof_claim_index} out of range"
            )
        
        claim = contract.claims[proof_request.proof_claim_index]
        
        # Verify the proof
        result = await app_state.verifier.verify_proof(
            proof_code=proof_request.proof_code,
            expected_theorem=claim.theorem_statement,
            allowed_dependencies=claim.allowed_dependencies,
            timeout_seconds=120,
            mathlib_version=claim.mathlib_version,
            assumption_contexts=claim.assumption_contexts
        )
        
        
        # Store verification attempt
        now = datetime.now()
        attempt = VerificationAttempt(
            attempt_id=f"attempt_{uuid.uuid4().hex[:12]}",
            contract_id=proof_request.contract_id,
            claim_id=claim.claim_id,
            submitter_agent_id=proof_request.prover_agent_id,
            proof_code=proof_request.proof_code,
            result=result,
            submitted_at=now,
            verified_at=now
        )
        await app_state.storage.store_verification_attempt(attempt)

        
        return ProofSubmitResponse(
            verdict=result.verdict,
            contract_id=proof_request.contract_id,
            prover_agent_id=proof_request.prover_agent_id,
            verification_time_ms=result.verification_time_ms,
            compilation_output=result.compilation_output,
            errors=result.errors if result.verdict != "ACCEPTED" else []
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Verification failed: {str(e)}"
        )


# Payment endpoints
@app.post("/payments/process", response_model=PaymentProcessResponse)
async def process_payment(request: PaymentProcessRequest, api_key: str = Depends(verify_api_key)) -> NoReturn:
    """
    Process payment for a verified contract.

    **MVP SCOPE**: Payment processing is deferred to v1.1

    This endpoint returns 501 NOT_IMPLEMENTED to clearly indicate that
    cryptographic payment processing with ledger storage is planned for v1.1.

    MVP focuses on verification API only.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Payment processing available in v1.1 - MVP scope is verification API only"
    )


# Verification history endpoint
@app.get("/contracts/{contract_id}/verification-history", response_model=VerificationHistoryResponse)
async def get_verification_history(contract_id: str, api_key: str = Depends(verify_api_key)) -> VerificationHistoryResponse:
    """Get verification attempt history for a contract"""
    if not app_state.storage:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Storage not initialized"
        )
    
    try:
        history = await app_state.storage.get_verification_history(contract_id)
        
        # Serialize VerificationAttempt objects to dicts
        history_dicts = [attempt.model_dump(mode="json") for attempt in history]
        
        return VerificationHistoryResponse(
            contract_id=contract_id,
            attempts=history_dicts,
            total_attempts=len(history_dicts)
        )

    

    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve history: {str(e)}"
        )


# Feedback endpoint
@app.post("/feedback/submit", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(request: Request, feedback_request: FeedbackRequest, api_key: str = Depends(verify_api_key)) -> FeedbackResponse:
    """
    Submit feedback about the usage of the VVUQ API.
    
    This endpoint allows agents and users to report bugs, request features,
    or provide general feedback directly through the API.
    
    Data is stored in Neo4j for review by the development team.
    """
    if not app_state.storage:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Storage not initialized"
        )
        
    try:
        feedback_id = f"feedback_{uuid.uuid4().hex[:12]}"
        
        # Add metadata
        feedback_data = feedback_request.model_dump()
        feedback_data["timestamp"] = datetime.now().isoformat()
        feedback_data["submitter_ip"] = request.client.host if request.client else "unknown"
        
    # Store in Neo4j
        await app_state.storage.store_feedback(feedback_id, feedback_data)
        
        # Create GitHub Issue (if configured)
        github_token = get_secret("github-token")
        github_repo = os.getenv("GITHUB_REPO", "dirkenglund/vvuq-mcp")
        issue_created = False
        issue_url = None
        
        if github_token:
            try:
                async with httpx.AsyncClient() as client:
                    # Map feedback type to labels
                    labels = ["feedback", feedback_request.feedback_type]
                    if feedback_request.severity in ["critical", "high"]:
                        labels.append("priority-high")
                    
                    # Construct issue body
                    body = f"""
### Feedback: {feedback_request.title}

**Type:** {feedback_request.feedback_type}
**Severity:** {feedback_request.severity}
**Submitter:** {feedback_request.submitter_type}

**Description:**
{feedback_request.description}

---
*Metadata:*
- Feedback ID: `{feedback_id}`
- IP: {request.client.host if request.client else "unknown"}
- Tool: {feedback_request.tool_name or "N/A"}
"""
                    if feedback_request.reproduction_steps:
                        body += f"\n**Reproduction Steps:**\n{feedback_request.reproduction_steps}"
                        
                    response = await client.post(
                        f"https://api.github.com/repos/{github_repo}/issues",
                        headers={
                            "Authorization": f"token {github_token}",
                            "Accept": "application/vnd.github.v3+json"
                        },
                        json={
                            "title": f"[{feedback_request.feedback_type.upper()}] {feedback_request.title}",
                            "body": body,
                            "labels": labels
                        },
                        timeout=5.0
                    )
                    
                    if response.status_code == 201:
                        issue_created = True
                        issue_data = response.json()
                        issue_url = issue_data.get("html_url")
                        # Update Neo4j with issue URL
                        await app_state.storage.store_feedback(feedback_id, {"github_issue_url": issue_url})
                    else:
                         print(f"Failed to create GitHub issue: {response.text}")

            except Exception as exc:
                print(f"Error creating GitHub issue: {exc}")
        
        msg_suffix = ""
        if issue_created and issue_url:
            ticket_id = issue_url.split('/')[-1]
            msg_suffix = f" (Ticket #{ticket_id} Created)"
        elif issue_created:
             msg_suffix = " (GitHub Issue Created)"

        return FeedbackResponse(
            success=True,
            feedback_id=feedback_id,
            message=f"Feedback submitted successfully{msg_suffix}",
            github_issue_created=issue_created
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to store feedback: {str(e)}"
        )


# Run server
if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("VVUQ_HTTP_PORT", "8000"))
    
    uvicorn.run(
        "http_api:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable in production
        log_level="info"
    )
