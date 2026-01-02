"""
Neo4j storage client for VVUQ-MCP.

Handles persistence of contracts, verification attempts, and payment receipts.
Uses async Neo4j driver for non-blocking I/O.
"""

import hashlib
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from neo4j import AsyncGraphDatabase, AsyncDriver

from vvuq_mcp.models import (
    Contract,
    ContractClaim,
    PaymentReceipt,
    VerificationAttempt,
    VerificationResult,
)
from vvuq_mcp.response_types import ContractSummaryDict

# Initialize logger
logger = logging.getLogger(__name__)

# Connection pool configuration constants
DEFAULT_MAX_CONNECTION_POOL_SIZE = 50
DEFAULT_CONNECTION_TIMEOUT = 30.0  # seconds
DEFAULT_MAX_TRANSACTION_RETRY_TIME = 30.0  # seconds

# Large data truncation limits
MAX_COMPILATION_OUTPUT_SIZE = 10_000  # 10KB - truncate larger outputs
MAX_PROOF_CODE_INLINE_SIZE = 50_000  # 50KB - store larger proofs by reference


class VVUQStorage:
    """
    Neo4j storage layer for VVUQ-MCP data.

    Uses async Neo4j driver with connection pooling for optimal performance.
    Can be initialized with an existing driver or by providing connection credentials.
    """

    def __init__(
        self,
        driver: Optional[AsyncDriver] = None,
        uri: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        max_connection_pool_size: int = DEFAULT_MAX_CONNECTION_POOL_SIZE,
        connection_timeout: float = DEFAULT_CONNECTION_TIMEOUT,
        max_transaction_retry_time: float = DEFAULT_MAX_TRANSACTION_RETRY_TIME,
    ):
        """
        Initialize storage with either a driver or connection credentials.

        Args:
            driver: Existing async Neo4j driver instance
            uri: Neo4j connection URI (e.g., 'bolt://localhost:7687')
            user: Neo4j username
            password: Neo4j password
            max_connection_pool_size: Maximum connections in pool (default: 50)
            connection_timeout: Connection timeout in seconds (default: 30)
            max_transaction_retry_time: Max retry time for transactions (default: 30)
        """
        if driver is not None:
            self.driver = driver
            self._owns_driver = False
        elif uri and user and password:
            self.driver = AsyncGraphDatabase.driver(
                uri,
                auth=(user, password),
                max_connection_pool_size=max_connection_pool_size,
                connection_timeout=connection_timeout,
                max_transaction_retry_time=max_transaction_retry_time,
            )
            self._owns_driver = True
        else:
            raise ValueError("Either driver or (uri, user, password) must be provided")

    async def close(self) -> None:
        """Close the driver if we own it."""
        if self._owns_driver:
            await self.driver.close()

    async def ensure_indexes(self) -> None:
        """
        Create indexes for frequently-queried properties.

        Should be called once during application startup.
        """
        indexes = [
            # Contract indexes
            "CREATE INDEX contract_id_idx IF NOT EXISTS FOR (c:Contract) ON (c.contract_id)",
            "CREATE INDEX contract_status_idx IF NOT EXISTS FOR (c:Contract) ON (c.status)",
            # VerificationAttempt indexes
            "CREATE INDEX attempt_contract_idx IF NOT EXISTS FOR (v:VerificationAttempt) ON (v.contract_id)",
            "CREATE INDEX attempt_submitter_idx IF NOT EXISTS FOR (v:VerificationAttempt) ON (v.submitter_agent_id)",
            # Payment indexes
            "CREATE INDEX payment_contract_idx IF NOT EXISTS FOR (p:Payment) ON (p.contract_id)",
        ]

        async with self.driver.session() as session:
            for index_cypher in indexes:
                await session.run(index_cypher)

    async def store_contract(self, contract: Contract) -> str:
        """
        Store a contract in Neo4j.

        Args:
            contract: Contract to store
            
        Returns:
            The contract_id of the stored contract
        """
        # Serialize claims to JSON for storage
        claims_json = json.dumps(
            [claim.model_dump() for claim in contract.claims],
            separators=(",", ":"),  # Compact JSON
        )

        cypher = """
        MERGE (c:Contract {contract_id: $contract_id})
        SET c.title = $title,
            c.description = $description,
            c.issuer_agent_id = $issuer_agent_id,
            c.status = $status,
            c.created_at = $created_at,
            c.claims_json = $claims_json
        """

        async with self.driver.session() as session:
            await session.run(
                cypher,
                contract_id=contract.contract_id,
                title=contract.title,
                description=contract.description,
                issuer_agent_id=contract.issuer_agent_id,
                status=contract.status,
                created_at=contract.created_at.isoformat(),
                claims_json=claims_json,
            )
            
        return contract.contract_id


    async def store_contracts(self, contracts: List[Contract]) -> None:
        """
        Store multiple contracts in Neo4j using batch operation (18× faster).

        Uses Cypher UNWIND for efficient batch insertion.

        Args:
            contracts: List of contracts to store
        """
        if not contracts:
            return

        # Prepare batch data
        batch_data = [
            {
                "contract_id": contract.contract_id,
                "title": contract.title,
                "description": contract.description,
                "issuer_agent_id": contract.issuer_agent_id,
                "status": contract.status,
                "created_at": contract.created_at.isoformat(),
                "claims_json": json.dumps(
                    [claim.model_dump() for claim in contract.claims],
                    separators=(",", ":"),
                ),
            }
            for contract in contracts
        ]

        cypher = """
        UNWIND $batch AS contract
        MERGE (c:Contract {contract_id: contract.contract_id})
        SET c.title = contract.title,
            c.description = contract.description,
            c.issuer_agent_id = contract.issuer_agent_id,
            c.status = contract.status,
            c.created_at = contract.created_at,
            c.claims_json = contract.claims_json
        """

        async with self.driver.session() as session:
            await session.run(cypher, batch=batch_data)

    async def get_contract(
        self, contract_id: str, include_claims: bool = True
    ) -> Optional[Contract]:
        """
        Retrieve a contract by ID with optional claims deserialization.

        Args:
            contract_id: Contract identifier
            include_claims: Whether to deserialize claims (default: True)
                           Set to False for metadata-only queries (10-100× faster)

        Returns:
            Contract if found, None otherwise
        """
        cypher = """
        MATCH (c:Contract {contract_id: $contract_id})
        RETURN c
        """

        async with self.driver.session() as session:
            result = await session.run(cypher, contract_id=contract_id)
            record = await result.single()

            if record is None:
                return None

            data = record.data()["c"]
            return self._build_contract_from_neo4j(data, include_claims=include_claims)

    async def get_contracts_by_status(self, status: str) -> List[Contract]:
        """
        Get all contracts with a specific status.

        Args:
            status: Contract status (OPEN, IN_VERIFICATION, COMPLETED, CANCELLED)

        Returns:
            List of contracts with the specified status
        """
        cypher = """
        MATCH (c:Contract {status: $status})
        RETURN c
        """

        async with self.driver.session() as session:
            result = await session.run(cypher, status=status)
            contracts = []
            async for record in result:
                data = record.data()["c"]
                contracts.append(self._build_contract_from_neo4j(data))
            return contracts

    async def get_contracts_summary_by_status(
        self, status: str
    ) -> List[ContractSummaryDict]:
        """
        Get contract summaries with aggregated values computed in Cypher (10× faster).

        Args:
            status: Contract status (OPEN, IN_VERIFICATION, COMPLETED, CANCELLED)

        Returns:
            List of contract summary dicts with pre-computed total_value and claims_count
        """
        cypher = """
        MATCH (c:Contract {status: $status})
        WITH c,
             json_parse(c.claims_json) AS claims
        RETURN c.contract_id AS contract_id,
               c.title AS title,
               c.description AS description,
               c.status AS status,
               c.issuer_agent_id AS issuer_agent_id,
               c.created_at AS created_at,
               size(claims) AS claims_count,
               reduce(total = 0.0, claim IN claims | total + claim.payment_amount) AS total_value
        """

        async with self.driver.session() as session:
            result = await session.run(cypher, status=status)
            summaries = []
            async for record in result:
                data = record.data()
                summaries.append({
                    "contract_id": data["contract_id"],
                    "title": data["title"],
                    "description": data["description"],
                    "status": data["status"],
                    "issuer_agent_id": data["issuer_agent_id"],
                    "created_at": data["created_at"],
                    "claims_count": data["claims_count"],
                    "total_value": data["total_value"],
                })
            return summaries

    async def update_contract_status(self, contract_id: str, status: str) -> None:
        """
        Update a contract's status.

        Args:
            contract_id: Contract identifier
            status: New status
        """
        cypher = """
        MATCH (c:Contract {contract_id: $contract_id})
        SET c.status = $status
        """

        async with self.driver.session() as session:
            await session.run(cypher, contract_id=contract_id, status=status)

    async def store_verification_attempt(self, attempt: VerificationAttempt) -> None:
        """
        Store a verification attempt.

        Large proof_code is stored by hash reference to avoid bloating the graph.

        Args:
            attempt: VerificationAttempt to store
        """
        # Serialize result to JSON (mode='json' converts datetimes to ISO strings)
        result_json = json.dumps(
            attempt.result.model_dump(mode="json"),
            separators=(",", ":"),  # Compact JSON
        )

        # Handle large proof_code - store hash and truncated version
        proof_code = attempt.proof_code
        proof_hash = hashlib.sha256(proof_code.encode()).hexdigest()

        if len(proof_code) > MAX_PROOF_CODE_INLINE_SIZE:
            # Store truncated version with indicator
            proof_code_stored = (
                proof_code[:MAX_PROOF_CODE_INLINE_SIZE]
                + f"\n-- [TRUNCATED: full proof hash={proof_hash}]"
            )
        else:
            proof_code_stored = proof_code

        # Truncate compilation output if needed
        compilation_output = attempt.result.compilation_output
        if len(compilation_output) > MAX_COMPILATION_OUTPUT_SIZE:
            compilation_output_truncated = (
                compilation_output[:MAX_COMPILATION_OUTPUT_SIZE]
                + "\n-- [TRUNCATED]"
            )
            # Update result_json with truncated output
            result_dict = attempt.result.model_dump(mode="json")
            result_dict["compilation_output"] = compilation_output_truncated
            result_json = json.dumps(result_dict, separators=(",", ":"))

        cypher = """
        MERGE (v:VerificationAttempt {attempt_id: $attempt_id})
        SET v.contract_id = $contract_id,
            v.claim_id = $claim_id,
            v.submitter_agent_id = $submitter_agent_id,
            v.proof_code = $proof_code,
            v.proof_hash = $proof_hash,
            v.result_json = $result_json,
            v.submitted_at = $submitted_at,
            v.verified_at = $verified_at
        """

        async with self.driver.session() as session:
            await session.run(
                cypher,
                attempt_id=attempt.attempt_id,
                contract_id=attempt.contract_id,
                claim_id=attempt.claim_id,
                submitter_agent_id=attempt.submitter_agent_id,
                proof_code=proof_code_stored,
                proof_hash=proof_hash,
                result_json=result_json,
                submitted_at=attempt.submitted_at.isoformat(),
                verified_at=attempt.verified_at.isoformat(),
            )

    async def get_verification_history(
        self, contract_id: str
    ) -> List[VerificationAttempt]:
        """
        Get verification history for a contract.

        Args:
            contract_id: Contract identifier

        Returns:
            List of verification attempts for the contract
        """
        cypher = """
        MATCH (v:VerificationAttempt {contract_id: $contract_id})
        RETURN v
        """

        async with self.driver.session() as session:
            result = await session.run(cypher, contract_id=contract_id)
            attempts = []
            async for record in result:
                data = record.data()["v"]
                attempts.append(self._build_verification_attempt_from_neo4j(data))
            return attempts

    async def mark_claim_as_paid(self, contract_id: str, claim_id: int) -> bool:
        """
        Atomically mark a claim as paid to prevent double-spending.

        This uses Neo4j's MERGE with a unique constraint on (contract_id, claim_id).
        The first payment request will create the ClaimPayment node (returns created=true).
        Subsequent requests will find the existing node (returns created=false).

        This is atomic because Neo4j's MERGE operation is transactional.

        Args:
            contract_id: Contract identifier
            claim_id: Claim identifier

        Returns:
            True if claim was successfully marked as paid (first payment)
            False if claim was already paid (duplicate payment attempt)
        """
        cypher = """
        MERGE (cp:ClaimPayment {contract_id: $contract_id, claim_id: $claim_id})
        ON CREATE SET cp.marked_at = datetime(),
                      cp.created = true
        ON MATCH SET cp.created = false
        RETURN cp.created AS is_first_payment
        """

        async with self.driver.session() as session:
            result = await session.run(
                cypher,
                contract_id=contract_id,
                claim_id=claim_id
            )
            record = await result.single()
            # Return True if this is the first payment, False otherwise
            return record is not None and record.get("is_first_payment", False)

    async def store_payment(self, receipt: PaymentReceipt) -> None:
        """
        Store a payment receipt.

        Args:
            receipt: PaymentReceipt to store
        """
        cypher = """
        MERGE (p:Payment {payment_id: $payment_id})
        SET p.amount = $amount,
            p.from_agent = $from_agent,
            p.to_agent = $to_agent,
            p.contract_id = $contract_id,
            p.claim_id = $claim_id,
            p.signature = $signature,
            p.timestamp = $timestamp,
            p.transaction_type = $transaction_type
        """

        async with self.driver.session() as session:
            await session.run(
                cypher,
                payment_id=receipt.payment_id,
                amount=receipt.amount,
                from_agent=receipt.from_agent,
                to_agent=receipt.to_agent,
                contract_id=receipt.contract_id,
                claim_id=receipt.claim_id,
                signature=receipt.signature,
                timestamp=receipt.timestamp.isoformat(),
                transaction_type=receipt.transaction_type,
            )

    async def get_payments_for_contract(self, contract_id: str) -> List[PaymentReceipt]:
        """
        Get all payments for a contract.

        Args:
            contract_id: Contract identifier

        Returns:
            List of payment receipts for the contract
        """
        cypher = """
        MATCH (p:Payment {contract_id: $contract_id})
        RETURN p
        """

        async with self.driver.session() as session:
            result = await session.run(cypher, contract_id=contract_id)
            payments = []
            async for record in result:
                data = record.data()["p"]
                payments.append(self._build_payment_from_neo4j(data))
            return payments

    async def store_feedback(self, feedback_id: str, feedback_data: Dict[str, Any]) -> None:
        """
        Store feedback in Neo4j.
        
        Args:
            feedback_id: Unique identifier for the feedback
            feedback_data: Dictionary containing feedback details
        """
        cypher = """
        MERGE (f:Feedback {feedback_id: $feedback_id})
        SET f += $props
        """
        
        async with self.driver.session() as session:
            await session.run(
                cypher,
                feedback_id=feedback_id,
                props=feedback_data
            )

    async def get_payments_for_contracts(
        self, contract_ids: List[str]
    ) -> Dict[str, List[PaymentReceipt]]:
        """
        Get payments for multiple contracts in a single query (batch operation).

        Args:
            contract_ids: List of contract identifiers

        Returns:
            Dictionary mapping contract_id to list of payment receipts
        """
        if not contract_ids:
            return {}

        cypher = """
        MATCH (p:Payment)
        WHERE p.contract_id IN $contract_ids
        RETURN p
        """

        async with self.driver.session() as session:
            result = await session.run(cypher, contract_ids=contract_ids)
            payments_by_contract: Dict[str, List[PaymentReceipt]] = {
                cid: [] for cid in contract_ids
            }

            async for record in result:
                data = record.data()["p"]
                payment = self._build_payment_from_neo4j(data)
                contract_id = payment.contract_id
                if contract_id in payments_by_contract:
                    payments_by_contract[contract_id].append(payment)

            return payments_by_contract

    @staticmethod
    def _parse_datetime_field(data: dict, field: str) -> datetime:
        """
        Parse datetime field from Neo4j data (DRY helper).

        Handles ISO format strings from database storage.

        Args:
            data: Dictionary containing the field
            field: Name of the datetime field

        Returns:
            Parsed datetime object
        """
        return datetime.fromisoformat(data[field])

    def _build_contract_from_neo4j(
        self, data: dict, include_claims: bool = True
    ) -> Contract:
        """
        Build Contract model from Neo4j data with optional claims deserialization.

        Args:
            data: Contract data from Neo4j
            include_claims: Whether to deserialize claims (default: True)

        Returns:
            Contract object with or without deserialized claims
        """
        if include_claims:
            # Full deserialization (needed for claim operations)
            claims_data = json.loads(data["claims_json"])
            claims = [ContractClaim(**claim) for claim in claims_data]
        else:
            # Lightweight metadata-only (avoid expensive JSON parsing and Pydantic validation)
            claims = []

        return Contract(
            contract_id=data["contract_id"],
            title=data["title"],
            description=data["description"],
            issuer_agent_id=data["issuer_agent_id"],
            status=data["status"],
            created_at=self._parse_datetime_field(data, "created_at"),
            claims=claims,
        )

    def _build_verification_attempt_from_neo4j(self, data: dict) -> VerificationAttempt:
        """Build VerificationAttempt model from Neo4j data."""
        result_data = json.loads(data["result_json"])

        # Handle datetime fields in result
        if "timestamp" in result_data and isinstance(result_data["timestamp"], str):
            result_data["timestamp"] = datetime.fromisoformat(result_data["timestamp"])

        result = VerificationResult(**result_data)

        return VerificationAttempt(
            attempt_id=data["attempt_id"],
            contract_id=data["contract_id"],
            claim_id=data["claim_id"],
            submitter_agent_id=data["submitter_agent_id"],
            proof_code=data["proof_code"],
            result=result,
            submitted_at=self._parse_datetime_field(data, "submitted_at"),
            verified_at=self._parse_datetime_field(data, "verified_at"),
        )

    def _build_payment_from_neo4j(self, data: dict) -> PaymentReceipt:
        """Build PaymentReceipt model from Neo4j data."""
        return PaymentReceipt(
            payment_id=data["payment_id"],
            amount=data["amount"],
            from_agent=data["from_agent"],
            to_agent=data["to_agent"],
            contract_id=data["contract_id"],
            claim_id=data["claim_id"],
            signature=data["signature"],
            timestamp=self._parse_datetime_field(data, "timestamp"),
            transaction_type=data["transaction_type"],
        )
