"""
Unit and Integration Tests for Cryptographic Model Provenance
Part of SIH26117 — Sovereign On-Premise Agentic AI Workbench (MRPL Smart Automation)
P2 — Model Infrastructure Engineer
"""

import hashlib
import tempfile
import unittest
from pathlib import Path

from model_router.provenance import (
    ProvenanceVerifier,
    TamperedModelWeightError,
)


class TestModelProvenance(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.ledger_file = Path(self.test_dir) / "provenance_ledger.json"
        self.verifier = ProvenanceVerifier(ledger_path=str(self.ledger_file))

        # Create a synthetic model weight file
        self.weight_file = Path(self.test_dir) / "qwen_weights_test.safetensors"
        self.weight_content = b"MRPL_SOVEREIGN_AUTHENTIC_MODEL_WEIGHT_STREAM_1234567890"
        self.weight_file.write_bytes(self.weight_content)
        self.expected_hash = hashlib.sha256(self.weight_content).hexdigest()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_calculate_file_hash(self):
        """Test streaming cryptographic SHA-256 calculation."""
        computed_hash = self.verifier.calculate_file_hash(self.weight_file, algorithm="sha256")
        self.assertEqual(computed_hash, self.expected_hash)

    def test_register_and_verify_genuine_model(self):
        """Test registering a valid model and verifying integrity."""
        record = self.verifier.register_model_hash(
            model_id="test_model_genuine",
            file_path=str(self.weight_file),
            expected_hash=self.expected_hash,
            signed_by="MRPL-Security-Ops",
        )
        self.assertEqual(record["status"], "VERIFIED_GENUINE")

        # Verify via ledger
        res = self.verifier.verify_model("test_model_genuine")
        self.assertEqual(res["status"], "VERIFIED_GENUINE")
        self.assertEqual(res["digest"], self.expected_hash)

    def test_tampered_model_weight_rejection(self):
        """Verify strict refusal when model weights have been tampered with."""
        # Register genuine hash
        self.verifier.register_model_hash(
            model_id="test_model_tamper",
            file_path=str(self.weight_file),
            expected_hash=self.expected_hash,
        )

        # Alter 1 byte in the weight file to simulate hostile tampering
        tampered_content = b"MRPL_SOVEREIGN_MALICIOUS_BACKDOORED_WEIGHTS_1234567890"
        self.weight_file.write_bytes(tampered_content)

        # Verification must raise TamperedModelWeightError and refuse execution
        with self.assertRaises(TamperedModelWeightError) as ctx:
            self.verifier.verify_model("test_model_tamper")

        err = ctx.exception
        self.assertEqual(err.model_id, "test_model_tamper")
        self.assertEqual(err.expected_hash, self.expected_hash)
        self.assertNotEqual(err.actual_hash, self.expected_hash)
        self.assertIn("tampering or corruption detected", str(err).lower())


if __name__ == "__main__":
    unittest.main()
