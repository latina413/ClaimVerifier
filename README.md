# GenLayer ClaimVerifier

An Intelligent Contract prototype for evaluating whether evidence supports a given claim using AI-assisted reasoning.

## Overview

ClaimVerifier is a GenLayer Intelligent Contract that evaluates a claim against provided evidence.

The contract asks an AI model to determine whether the evidence supports the claim.

The result has two possible decisions:

- VERIFIED — the evidence supports the claim.
- REJECTED — the evidence does not sufficiently support the claim.

The contract uses GenLayer's comparative equivalence principle so that validators should reach the same decision, while the explanation may differ.

## Project Structure

```text
genlayer-builder/
├── contracts/
│   └── claim_verifier.py
├── tests/
│   └── direct/
│       └── test_claim_verifier.py
└── README.md
```

## How the Contract Works

The contract receives two inputs:

- `claim`
- `evidence`

The processing flow is:

```text
Claim + Evidence
       │
       ▼
   AI Prompt
       │
       ▼
Validator / AI evaluation
       │
       ▼
Comparative Equivalence
       │
       ▼
VERIFIED / REJECTED
```

## Example

### Claim

The Earth orbits the Sun.

### Evidence

Astronomical observations show that Earth revolves around the Sun.

### Expected Result

```text
VERIFIED
```

## AI Prompt

The contract uses the following instruction for the AI:

```text
You are a claim verification assistant.

Evaluate whether the evidence supports the claim.

Claim:
{claim}

Evidence:
{evidence}

Return ONLY valid JSON in exactly this format:

{
    "decision": "VERIFIED" or "REJECTED",
    "reason": "short explanation"
}
```

## Consensus Principle

The contract uses GenLayer's comparative equivalence principle:

```python
gl.eq_principle.prompt_comparative(
    evaluate,
    principle="The decision must be the same. The explanation may differ.",
)
```

## Contract Validation

The contract was checked using `genvm-lint`.

```text
✓ Lint passed
✓ Validation passed

Contract: ClaimVerifier
Methods: 1 (0 view, 1 write)
```

## Direct Mode Testing

The project uses Direct Mode testing with mocked LLM responses.

Four scenarios are currently tested:

1. Supported claim
2. Contradicted claim
3. Insufficient evidence
4. Consistency

## Test Result

Command:

```bash
pytest -q tests/direct/
```

Expected result:

```text
4 passed
```

## Testing Limitation

The current tests use mocked LLM responses.

They demonstrate that the contract logic works correctly and produces the expected decisions under the test conditions.

They do not yet demonstrate real validator consensus or AI consistency across independent validators.

Real network testing is required for that.

## Current Status

```text
[✓] Intelligent Contract designed
[✓] Contract implemented
[✓] GenVM lint passed
[✓] Contract validation passed
[✓] Contract schema generated
[✓] Direct Mode tests implemented
[✓] VERIFIED scenario tested
[✓] REJECTED scenario tested
[✓] Insufficient evidence scenario tested
[✓] Consistency scenario tested
[ ] Test on GenLayer Asimov
[ ] Test on GenLayer Bradbury
[ ] Document real testnet results
[ ] Collect community feedback
```

## Future Improvements

Possible improvements include:

- testing more ambiguous claims;
- testing contradictory evidence;
- testing malformed AI responses;
- testing different prompt formulations;
- recording validator inconsistencies;
- testing the contract on GenLayer Asimov;
- testing the contract on GenLayer Bradbury;
- documenting real testnet observations;
- improving the prompt based on testnet results.

## Goal

This project demonstrates a simple Intelligent Contract combining:

```text
Smart-contract logic
        +
AI-assisted evaluation
        +
Validator agreement
```
