# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *

class ClaimVerifier(gl.Contract):

    def __init__(self):
        pass

    @gl.public.write

    def verify_claim(self, claim: str, evidence: str) -> str:
        prompt = f"""
You are a claim verification assistant.

Evaluate whether the evidence supports the claim.

Claim:
{claim}

Evidence:
{evidence}

Return ONLY valid JSON in exactly this format:

{{
    "decision": "VERIFIED" or "REJECTED",
    "reason": "short explanation"
}}
"""

        def evaluate():
            return gl.nondet.exec_prompt(prompt)

        result = gl.eq_principle.prompt_comparative(
            evaluate,
            principle="The decision must be the same. The explanation may differ.",
        )

        data = result

        if data["decision"] not in ("VERIFIED", "REJECTED"):
            raise gl.vm.UserError("Invalid decision")

        return data["decision"]
