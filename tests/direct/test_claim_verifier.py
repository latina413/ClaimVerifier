from pathlib import Path

from gltest.direct import VMContext, deploy_contract


CONTRACT_PATH = (
    Path(__file__).resolve().parents[2]
    / "contracts"
    / "claim_verifier.py"
)


def deploy_with_mock(vm, response):
    vm.mock_llm(
        r".*",
        response,
    )

    return deploy_contract(CONTRACT_PATH, vm)


def test_claim_verifier_verified():
    vm = VMContext()

    with vm.activate():
        contract = deploy_with_mock(
            vm,
            {
                "decision": "VERIFIED",
                "reason": "Evidence supports the claim.",
            },
        )

        claim_id = contract.submit_claim(
            "The Earth orbits the Sun."
        )

        contract.add_evidence(
            claim_id,
            "Astronomical observations show that Earth revolves around the Sun.",
        )

        result = contract.verify_claim(claim_id)

        assert result == "VERIFIED"

        claim = contract.get_claim(claim_id)

        assert claim["status"] == "VERIFIED"
        assert claim["decision"] == "VERIFIED"
        assert len(claim["evidence"]) == 1


def test_claim_verifier_rejected():
    vm = VMContext()

    with vm.activate():
        contract = deploy_with_mock(
            vm,
            {
                "decision": "REJECTED",
                "reason": "Evidence contradicts the claim.",
            },
        )

        claim_id = contract.submit_claim(
            "The Earth is flat."
        )

        contract.add_evidence(
            claim_id,
            "Satellite observations show that Earth is approximately spherical.",
        )

        result = contract.verify_claim(claim_id)

        assert result == "REJECTED"

        claim = contract.get_claim(claim_id)

        assert claim["status"] == "REJECTED"
        assert claim["decision"] == "REJECTED"
        assert len(claim["evidence"]) == 1


def test_claim_verifier_insufficient_evidence():
    vm = VMContext()

    with vm.activate():
        contract = deploy_with_mock(
            vm,
            {
                "decision": "INSUFFICIENT",
                "reason": "The evidence is insufficient to support the claim.",
            },
        )

        claim_id = contract.submit_claim(
            "This company will become the largest company in the world."
        )

        contract.add_evidence(
            claim_id,
            "The company was founded recently.",
        )

        result = contract.verify_claim(claim_id)

        assert result == "INSUFFICIENT"

        claim = contract.get_claim(claim_id)

        assert claim["status"] == "INSUFFICIENT"
        assert claim["decision"] == "INSUFFICIENT"


def test_claim_verifier_consistency():
    vm = VMContext()

    with vm.activate():
        contract = deploy_with_mock(
            vm,
            {
                "decision": "VERIFIED",
                "reason": "Evidence supports the claim.",
            },
        )

        claim = (
            "Water freezes at 0 degrees Celsius "
            "under standard atmospheric pressure."
        )

        evidence = (
            "Under standard atmospheric pressure, "
            "water freezes at 0 degrees Celsius."
        )

        results = []

        for _ in range(5):
            claim_id = contract.submit_claim(claim)

            contract.add_evidence(
                claim_id,
                evidence,
            )

            results.append(
                contract.verify_claim(claim_id)
            )

        assert results == [
            "VERIFIED",
            "VERIFIED",
            "VERIFIED",
            "VERIFIED",
            "VERIFIED",
        ]
