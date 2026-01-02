# Security Policy

## Reporting Security Vulnerabilities

The Iltero team takes security vulnerabilities seriously. We appreciate your efforts to responsibly disclose your findings.

**Please do NOT report security vulnerabilities through public GitHub issues.**

### How to Report

To report a security vulnerability, please email:

**security@iltero.com**

Include the following information:
- Type of vulnerability
- Full paths of source file(s) related to the vulnerability
- Location of the affected source code (tag/branch/commit or direct URL)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the vulnerability, including how an attacker might exploit it

### What to Expect

- **Acknowledgment**: We will acknowledge receipt of your vulnerability report within 48 hours.
- **Updates**: We will provide regular updates on the progress of addressing the vulnerability.
- **Disclosure Timeline**: We aim to address critical vulnerabilities within 90 days.
- **Credit**: With your permission, we will publicly credit you for responsibly disclosing the vulnerability.

## Supported Versions

We release security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

**Note:** As this project is in early development (pre-1.0), only the latest minor version receives security updates.

## Security Best Practices

### Token Storage

The Iltero CLI stores authentication tokens securely using your system's native credential manager:

- **macOS**: Keychain
- **Linux**: Secret Service (gnome-keyring, kwallet)
- **Windows**: Windows Credential Manager

**Never commit tokens to version control.**

### Environment Variables

While the CLI supports environment variables for configuration, we recommend:

1. **CI/CD**: Use encrypted secrets (GitHub Actions secrets, GitLab CI/CD variables)
2. **Local Development**: Use `iltero auth set-token` for keyring storage
3. **Temporary Use**: Unset `ILTERO_TOKEN` after use if set in shell

### Token Rotation

We recommend rotating tokens regularly:

- **Personal tokens**: Every 90 days
- **Service tokens**: Every 180 days
- **Pipeline tokens**: Rotate immediately if exposed

### Least Privilege

Use tokens with the minimum required permissions:

- **Read-only operations**: Use read-only tokens
- **CI/CD pipelines**: Use pipeline-specific tokens with scoped permissions
- **Production**: Use service tokens with restricted scope

## Known Security Considerations

### Token Prefix Detection

The CLI uses token prefixes (`itk_p_`, `itk_u_`, `itk_s_`, `itk_r_`) to identify token types. This is for convenience and does not provide security.

### API Communication

All API communication uses HTTPS. The CLI will refuse to communicate with non-HTTPS endpoints unless explicitly configured for local development.

### Debug Mode

When `--debug` is enabled, the CLI may log sensitive information. **Never enable debug mode in production or share debug logs publicly without redacting sensitive data.**

## Security Updates

Security updates will be announced through:

- GitHub Security Advisories
- Release notes
- Email (for users who opt-in)

## Compliance

The Iltero CLI is designed to support compliance requirements:

- **SOC 2**: Token security, audit logging
- **ISO 27001**: Secure credential storage
- **GDPR**: No PII stored locally without consent

For enterprise security questionnaires, contact: security@iltero.io

## Bug Bounty

We do not currently have a formal bug bounty program. However, we deeply appreciate security researchers who responsibly disclose vulnerabilities and will acknowledge contributions publicly (with permission).

---

**Last Updated**: November 27, 2025
