# Security Policy

## Supported Versions

We currently support the following versions with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

We take the security of Cloud Connectors seriously. If you discover a security vulnerability, please follow these steps:

### 1. **Do Not** Open a Public Issue

Security vulnerabilities should **not** be reported via public GitHub issues, as this could put users at risk.

### 2. Report Privately

Please report security vulnerabilities by emailing:

**Email:** jon@jonbogaty.com

Include in your report:
- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact
- Any suggested fixes (if available)

### 3. Response Timeline

- **Initial Response:** Within 48 hours of receiving your report
- **Status Update:** Within 7 days with assessment and planned fix timeline
- **Fix Release:** Depends on severity and complexity
  - **Critical:** 1-3 days
  - **High:** 1-2 weeks
  - **Medium:** 2-4 weeks
  - **Low:** Next scheduled release

### 4. Disclosure Policy

- We request that you **do not publicly disclose** the vulnerability until we've released a fix
- Once a fix is released, we will:
  - Credit you in the release notes (unless you prefer to remain anonymous)
  - Publish a security advisory on GitHub
  - Notify users via release notes and documentation

## Security Best Practices

When using Cloud Connectors, follow these security best practices:

### Credential Management

1. **Never hardcode credentials** in your code
2. **Use environment variables** for sensitive data:
   ```python
   import os
   connector = AWSConnector(
       execution_role_arn=os.getenv("AWS_ROLE_ARN")
   )
   ```

3. **Use secret management services:**
   - AWS Secrets Manager
   - HashiCorp Vault (VaultConnector)
   - Azure Key Vault
   - Google Secret Manager

4. **Rotate credentials regularly**

### Access Control

1. **Follow principle of least privilege:**
   - Grant only necessary permissions
   - Use role-based access control (RBAC)
   - Limit scope of API tokens

2. **For AWS:**
   - Use IAM roles instead of access keys when possible
   - Enable MFA for sensitive operations
   - Use STS temporary credentials (AWSConnector handles this)

3. **For Google Cloud:**
   - Use service accounts with minimal scopes
   - Implement domain-wide delegation carefully
   - Audit service account usage regularly

4. **For GitHub:**
   - Use fine-grained personal access tokens
   - Limit token scope to required repositories
   - Set token expiration dates

### Network Security

1. **Use HTTPS** for all API communications (connectors default to HTTPS)
2. **Validate SSL certificates** (enabled by default)
3. **Use VPN or private endpoints** when available for cloud services

### Logging and Monitoring

1. **Enable audit logging:**
   ```python
   connector = AWSConnector(
       verbose=True,
       log_file_name="audit.log"
   )
   ```

2. **Never log sensitive data:**
   - Credentials are automatically masked in logs
   - Review logs before sharing publicly

3. **Monitor for suspicious activity:**
   - Unusual API call patterns
   - Failed authentication attempts
   - Access from unexpected locations

### Dependency Management

1. **Keep dependencies up to date:**
   ```bash
   pip install --upgrade cloud-connectors
   ```

2. **Audit dependencies regularly:**
   ```bash
   pip-audit
   ```

3. **Pin dependency versions** in production:
   ```txt
   cloud-connectors==0.1.0
   boto3==1.34.0
   ```

## Known Security Considerations

### Authentication Caching

- Connectors cache authenticated sessions for performance
- Cached sessions may contain sensitive credentials
- Sessions are stored in memory only (not persisted to disk)
- Consider session expiration in long-running applications

### Error Messages

- Error messages may contain sensitive information
- Use appropriate log levels (ERROR/WARNING vs INFO/DEBUG)
- Review error messages before sharing publicly
- Sanitize error logs in production environments

### Input Validation

- Connectors perform basic input validation
- Always validate and sanitize user inputs before passing to connectors
- Be cautious with file paths and URLs from untrusted sources

## Security Updates

Security updates are released as soon as possible after a vulnerability is confirmed. Users are notified through:

1. **GitHub Security Advisories**
2. **Release Notes** (CHANGELOG.md)
3. **PyPI Release** with security tag

Subscribe to repository notifications to receive security alerts.

## Compliance

Cloud Connectors is designed to support compliance with:

- **GDPR:** Through proper credential and data handling
- **SOC 2:** Via audit logging and access controls
- **HIPAA:** When used with compliant cloud services
- **PCI DSS:** Through secure credential management

However, **compliance is a shared responsibility**. Ensure your implementation follows relevant regulations and best practices.

## Security Checklist for Contributions

Before submitting code that handles:
- [ ] Credentials are never hardcoded
- [ ] Sensitive data is not logged
- [ ] Input validation is performed
- [ ] SSL/TLS verification is enabled
- [ ] Temporary credentials are cleaned up
- [ ] Error messages don't leak sensitive info
- [ ] Dependencies are up to date
- [ ] Tests include security scenarios

## Contact

For security concerns or questions:
- **Email:** jon@jonbogaty.com
- **GitHub:** @jbcom

Thank you for helping keep Cloud Connectors secure! 🔒
