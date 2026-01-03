# Security Policy

## Reporting Security Vulnerabilities

We take security seriously. If you discover a security vulnerability in this project, **please** open a public GitHub issue. Instead, please report it responsibly by:

### Private Disclosure
- **Email**: Contact the repository maintainer privately with details about the vulnerability
- **GitHub Security Advisory**: Use [GitHub's private vulnerability reporting feature](https://github.com/beanapologist/seed/security/advisories)
- Include steps to reproduce and potential impact assessment

### What to Include
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if available)

## Scope

This security policy covers:
- Binary seed files integrity
- Documentation accuracy
- Supply chain security
- Dependency vulnerabilities (if any)

## Out of Scope

The following are **not** considered security vulnerabilities:
- Educational/documentation improvements
- Code style or formatting issues
- Feature requests

## Security Features

### Binary Integrity
All released binaries include cryptographic checksums for verification:

**v1.0.0 Checksums:**
```
golden_seed_16.bin:
  SHA256: 87f829d95b15b08db9e5d84ff06665d077b267cfc39a5fa13a9e002b3e4239c5
  SHA512: 6c1e6ffdcfa8a1e4cfcfaeedb8b3b4f64a8de3d1b690e61e7ce48e80da9bcd7127bc890a3e74bb3d1c92bc5052b1076c0fe9b86eff210f497ecd0104eb544483

golden_seed_32.bin:
  SHA256: 096412ca0482ab0f519bc0e4ded667475c45495047653a21aa11e2c7c578fa6f
  SHA512: fcfdc7392214fa5bc36c7a9edaa725fa366bb83f7bc2e4d5006688e4d0b07c56eea2c2d3fcb5fbf6c63e0217973d05ed358e7b8ad71df1812f1fb212c6ac8498

golden_seed.hex:
  SHA256: 9569db82634b232aebe75ef131dc00bdd033b8127dfcf296035f53434b6c2ccd
  SHA512: 6203cf0086ed52854deb4e6ba83ea1eba2054430ad7a9ee52510a6f730db7a122d96858c2f4d9ff657a0451d3a9ff36285b7d3f9454206fc0e20d7d6a2bb695f
```

### Verify Downloads
To verify the integrity of downloaded files:

**Linux/macOS:**
```bash
sha256sum -c <<EOF
87f829d95b15b08db9e5d84ff06665d077b267cfc39a5fa13a9e002b3e4239c5  golden_seed_16.bin
096412ca0482ab0f519bc0e4ded667475c45495047653a21aa11e2c7c578fa6f  golden_seed_32.bin
9569db82634b232aebe75ef131dc00bdd033b8127dfcf296035f53434b6c2ccd  golden_seed.hex
EOF
```

**Python:**
```python
import hashlib

def verify_file(filepath, expected_sha256):
    with open(filepath, 'rb') as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
    return file_hash == expected_sha256
```

## Security Best Practices

### For Users
1. **Verify checksums** before using downloaded binaries
2. **Use from official releases** only (https://github.com/beanapologist/seed/releases)
3. **Keep your systems updated** to benefit from security patches
4. **Report suspicious behavior** through proper channels

### For Contributors
1. **Don't commit secrets** - use `.gitignore` for sensitive files
2. **Review code** before submitting pull requests
3. **Test thoroughly** - especially with different byte orders and platforms
4. **Document security implications** of changes

## Release Signing

We sign release artifacts with GPG to provide provenance and integrity guarantees.

To enable automatic signing during GitHub Actions releases, add the following secret to the repository:

- `GPG_PRIVATE_KEY`: Base64-encoded ASCII-armored private key used to sign release artifacts.

The repository includes a workflow `.github/workflows/sign-release.yml` that:

- Generates `checksums.txt` (SHA256 + SHA512) for published assets using `scripts/generate_checksums.sh`.
- Imports the `GPG_PRIVATE_KEY` on the runner (if provided), creates an ASCII-armored detached signature `checksums.txt.sig`.
- Uploads `checksums.txt` and `checksums.txt.sig` to the GitHub Release.

If you prefer not to store a private key on GitHub, you can generate checksums locally and sign them yourself before uploading them to the release.

## No Warranties

This project is provided "as-is" without warranties or guarantees. Users are responsible for validating the appropriateness of this seed for their use cases, especially in security-critical applications.

## Acknowledgments

We appreciate responsible vulnerability disclosure and security research that helps improve this project.

---

**Last Updated:** December 30, 2025
