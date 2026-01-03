# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for receiving such patches depends on the CVSS v3.0 Rating:

| Version | Supported          |
| ------- | ------------------ |
| 0.2.x   | :white_check_mark: |
| 0.1.x   | :x:                |
| < 0.1   | :x:                |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to: **security@zo.xyz**

You should receive a response within 48 hours. If for some reason you do not, please follow up via email to ensure we received your original message.

Please include the following information (as much as you can provide) to help us better understand the nature and scope of the possible issue:

- Type of issue (e.g., buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit the issue

This information will help us triage your report more quickly.

## Security Best Practices for Users

### 1. Credential Management

- **Never hardcode API keys** or credentials in your code
- Use environment variables or secure secret management systems
- Rotate credentials regularly

```python
# Good
import os
client_key = os.environ.get("ZO_CLIENT_KEY")

# Bad
client_key = "your-actual-key-here"  # Never do this!
```

### 2. Storage Security

- **Use encrypted storage** for production environments
- Protect encryption keys with appropriate permissions
- Consider using OS keyring for storing encryption keys

```python
from zopassport import EncryptedFileStorageAdapter

# Use password-based encryption
storage = EncryptedFileStorageAdapter(
    file_path="session.enc",
    password=os.environ["SESSION_PASSWORD"]
)
```

### 3. Session Management

- **Implement proper logout** functionality
- Clear sensitive data when no longer needed
- Set appropriate session timeouts

```python
try:
    # Your application code
    pass
finally:
    await sdk.logout()  # Always cleanup
```

### 4. Network Security

- **Always use HTTPS** (default in the SDK)
- Verify SSL certificates (enabled by default)
- Implement rate limiting in your application

### 5. Input Validation

- **Validate all user inputs** before processing
- Sanitize data before logging
- Use parameterized queries for databases

### 6. Logging

- **Never log sensitive information**:
  - Access tokens
  - Refresh tokens
  - OTP codes
  - Passwords
  - Personal information

```python
# Good - Log without sensitive data
logger.info("User authenticated", extra={"user_id": user.id})

# Bad - Don't log tokens
logger.info(f"Token: {access_token}")  # Never do this!
```

### 7. Dependencies

- Keep dependencies up to date
- Monitor for security advisories
- Use tools like `safety` to check for known vulnerabilities

```bash
# Check for vulnerable dependencies
safety check
```

### 8. Error Handling

- Don't expose sensitive information in error messages
- Use generic error messages for authentication failures
- Log detailed errors server-side only

## Known Security Considerations

### Token Storage

- Tokens are stored in files by default
- Use `EncryptedFileStorageAdapter` for sensitive environments
- File permissions are set to `0o600` (owner read/write only)

### Device Credentials

- Device credentials are generated randomly
- They are stored alongside session data
- Consider them sensitive and protect accordingly

### Rate Limiting

- The SDK handles rate limiting automatically
- Implement additional application-level rate limiting as needed
- Monitor for unusual API usage patterns

## Security Updates

Security updates will be released as soon as possible after a vulnerability is confirmed. Users will be notified via:

- GitHub Security Advisories
- Email (if registered)
- Release notes

## Responsible Disclosure

We kindly ask that security researchers:

- Give us reasonable time to respond to your report before public disclosure
- Make a good faith effort to avoid privacy violations and disruption of services
- Don't access or modify data that doesn't belong to you

We commit to:

- Respond to your report within 48 hours
- Keep you informed about our progress
- Credit you in our security advisories (unless you prefer to remain anonymous)

## Security Checklist for Developers

When contributing code, ensure:

- [ ] No hardcoded credentials or secrets
- [ ] Input validation for all user inputs
- [ ] Proper error handling without information leakage
- [ ] Sensitive data is not logged
- [ ] Dependencies are up to date and secure
- [ ] Tests include security-relevant scenarios
- [ ] Documentation includes security considerations

## Contact

For security concerns, contact: **security@zo.xyz**

For general questions: **dev@zo.xyz**

---

Thank you for helping keep ZoPassport and its users safe!
