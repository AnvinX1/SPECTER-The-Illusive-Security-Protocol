#!/usr/bin/env python3
# SPECTER test fixture — file containing fake/example secrets for secret_grep tests
# These are intentionally fake secrets for testing pattern detection only

# Fake AWS credentials — not real values
FAKE_AWS_KEY = "AKIAIOSFODNN7EXAMPLE"
FAKE_AWS_SECRET = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"  # noqa

# Fake OpenAI key pattern
FAKE_OPENAI_KEY = "sk-abc123def456ghi789jkl012mno345pqr678stu"

# Fake private key header (partial, not a real key)
FAKE_PRIVATE_KEY_MARKER = "-----BEGIN RSA PRIVATE KEY-----"

# Fake bearer token in assignment context
FAKE_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.signature"

# These should NOT be flagged (test false-positive suppression)
example_token = "example_bearer_token_for_demo"
test_password = "test_password_only"
sample_api_key = "sample_key_for_documentation"
