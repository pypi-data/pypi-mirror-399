from fastmcp import FastMCP
from vvuq.client import VVUQClient
import os
from typing import List, Dict, Any, Optional

# Create FastMCP server
mcp = FastMCP("vvuq-access",  dependencies=["vvuq-client"])

def get_client() -> VVUQClient:
    """Get authenticated VVUQ client from environment."""
    api_url = os.getenv("VVUQ_API_URL", "http://127.0.0.1:8081") 
    api_key = os.getenv("VVUQ_API_KEY")
    
    if not api_key:
        raise ValueError("VVUQ_API_KEY environment variable is required to access the VVUQ Verification Network.")
        
    return VVUQClient(base_url=api_url, api_key=api_key)

@mcp.tool()
def submit_proof(contract_id: str, claim_id: int, proof_code: str, submitter_agent_id: str) -> Dict[str, Any]:
    """
    Submit a Lean4 proof for verification.
    """
    client = get_client()
    return client.submit_proof(
        contract_id=contract_id,
        claim_id=claim_id,
        proof_code=proof_code,
        submitter_agent_id=submitter_agent_id
    )

@mcp.tool()
def create_contract(title: str, description: str, claims: List[Dict[str, Any]], issuer_id: str) -> Dict[str, Any]:
    """
    Create a new verification contract.
    
    Args:
        claims: List of dicts with 'claim_id', 'theorem_statement', 'payment_amount'
    """
    client = get_client()
    return client.create_contract(
        title=title,
        description=description,
        claims=claims,
        issuer_id=issuer_id
    )

@mcp.tool()
def get_contract(contract_id: str) -> Optional[Dict[str, Any]]:
    """Get contract details."""
    client = get_client()
    return client.get_contract(contract_id)

@mcp.tool()
def process_payment(contract_id: str, claim_id: int, from_agent: str, to_agent: str, amount: float) -> Dict[str, Any]:
    """Process cryptographic payment (Requires VVUQ_SECRET_KEY in environment)."""
    # Note: Client might need update to support payment if not already there, 
    # or this tool maps directly if client exposes it.
    client = get_client()
    # Assuming client has process_payment method. If not, this will fail at runtime, 
    # but serves as placeholder for the Proxy pattern.
    if hasattr(client, 'process_payment'):
        return client.process_payment(contract_id, claim_id, from_agent, to_agent, amount)
    else:
        raise NotImplementedError("Payment processing not yet available in current SDK version.")

@mcp.tool()
def submit_feedback(title: str, description: str, feedback_type: str = "general", severity: str = "low") -> Dict[str, Any]:
    """Submit feedback or bug reports."""
    client = get_client()
    return client.submit_feedback(
        title=title,
        description=description,
        feedback_type=feedback_type,
        severity=severity,
        submitter_type="agent_via_mcp"
    )

def main():
    mcp.run()

if __name__ == "__main__":
    main()
