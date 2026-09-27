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

        result = contract.verify_claim(
            "The Earth orbits the Sun.",
            "Astronomical observations show that Earth revolves around the Sun.",
        )

        assert result == "VERIFIED"


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

        result = contract.verify_claim(
            "The Earth is flat.",
            "Satellite observations show that Earth is approximately spherical.",
        )

        assert result == "REJECTED"


def test_claim_verifier_insufficient_evidence():
    vm = VMContext()

    with vm.activate():
        contract = deploy_with_mock(
            vm,
            {
                "decision": "REJECTED",
                "reason": "The evidence is insufficient to support the claim.",
            },
        )

        result = contract.verify_claim(
            "This company will become the largest company in the world.",
            "The company was founded recently.",
        )

        assert result == "REJECTED"

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

        claim = "Water freezes at 0 degrees Celsius under standard atmospheric pressure."
        evidence = "Under standard atmospheric pressure, water freezes at 0 degrees Celsius."

        results = [
            contract.verify_claim(claim, evidence)
            for _ in range(5)
        ]

        assert results == ["VERIFIED"] * 5
