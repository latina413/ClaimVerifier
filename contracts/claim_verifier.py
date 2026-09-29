# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
from genlayer.py.storage import TreeMap, DynArray, allow_storage
from genlayer.py.types import u32
@allow_storage

class ClaimRecord:
    claim: str
    evidence: DynArray[str]
    status: str
    decision: str
    reason: str

    def __init__(self, claim: str):
        self.claim = claim
        self.status = "PENDING"
        self.decision = ""
        self.reason = ""
@allow_storage

class VerificationRecord:
    claim_id: u32
    decision: str
    reason: str
    evidence_count: u32

    def __init__(
        self,
        claim_id: u32,
        decision: str,
        reason: str,
        evidence_count: u32,
    ):
        self.claim_id = claim_id
        self.decision = decision
        self.reason = reason
        self.evidence_count = evidence_count


class ClaimVerifier(gl.Contract):

    claims: TreeMap[u32, ClaimRecord]
    history: DynArray[VerificationRecord]
    next_claim_id: u32

    def __init__(self):
        self.next_claim_id = u32(1)

    @gl.public.write
    def submit_claim(self, claim: str) -> u32:
        if not claim.strip():
            raise gl.vm.UserError("Claim cannot be empty")

        claim_id = self.next_claim_id
        self.next_claim_id = u32(int(claim_id) + 1)

        self.claims[claim_id] = ClaimRecord(claim)

        return claim_id

    @gl.public.write
    def add_evidence(self, claim_id: u32, evidence: str) -> str:
        if claim_id not in self.claims:
            raise gl.vm.UserError("Claim not found")

        if not evidence.strip():
            raise gl.vm.UserError("Evidence cannot be empty")

        record = self.claims[claim_id]

        if record.status != "PENDING":
            raise gl.vm.UserError("Claim is not accepting evidence")

        for existing in record.evidence:
            if existing == evidence:
                raise gl.vm.UserError("Duplicate evidence")

        record.evidence.append(evidence)

        return "EVIDENCE_ADDED"

    @gl.public.write
    def verify_claim(self, claim_id: u32) -> str:
        if claim_id not in self.claims:
            raise gl.vm.UserError("Claim not found")

        record = self.claims[claim_id]

        if record.status != "PENDING":
            raise gl.vm.UserError("Claim is not pending")

        if len(record.evidence) == 0:
            raise gl.vm.UserError("Evidence is required")

        record.status = "EVALUATING"

        evidence_text = "\n".join(
            f"- {item}" for item in record.evidence
        )

        prompt = f"""
You are a claim verification assistant.

Evaluate whether the submitted evidence supports the claim.

Claim:
{record.claim}

Evidence:
{evidence_text}

Return ONLY valid JSON in exactly this format:

{{
    "decision": "VERIFIED", "REJECTED", or "INSUFFICIENT",
    "reason": "short explanation"
}}

VERIFIED means the evidence supports the claim.
REJECTED means the evidence contradicts the claim.
INSUFFICIENT means the evidence does not provide enough information.
"""

        def evaluate():
            return gl.nondet.exec_prompt(prompt)

        result = gl.eq_principle.prompt_comparative(
            evaluate,
            principle="The decision must be the same. The explanation may differ.",
        )

        decision = result["decision"]
        reason = result["reason"]

        if decision not in (
            "VERIFIED",
            "REJECTED",
            "INSUFFICIENT",
        ):
            record.status = "PENDING"
            raise gl.vm.UserError("Invalid decision")

        record.decision = decision
        record.reason = reason
        record.status = decision

        self.history.append(
            VerificationRecord(
                claim_id,
                decision,
                reason,
                u32(len(record.evidence)),
            )
        )

        return decision

    @gl.public.view
    def get_claim(self, claim_id: u32) -> dict:
        if claim_id not in self.claims:
            raise gl.vm.UserError("Claim not found")

        record = self.claims[claim_id]

        return {
            "claim": record.claim,
            "evidence": list(record.evidence),
            "status": record.status,
            "decision": record.decision,
            "reason": record.reason,
        }

    @gl.public.view
    def get_verification_history(self) -> list:
        return [
            {
                "claim_id": item.claim_id,
                "decision": item.decision,
                "reason": item.reason,
                "evidence_count": item.evidence_count,
            }
            for item in self.history
        ]
