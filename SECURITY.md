Describe here all the security policies in place on this repository to help your contributors to handle security issues efficiently.

## Goods practices to follow

:warning:**You must never store credentials information into source code or config file in a GitHub repository**
- Block sensitive data being pushed to GitHub by git-secrets or its likes as a git pre-commit hook
- Audit for slipped secrets with dedicated tools
- Use environment variables for secrets in CI/CD (e.g. GitHub Secrets) and secret managers in production

# Security Policy

## Supported Versions

Only latest version is being supported with security updates.

## Reporting a Vulnerability

If you find a security vulnerability, please contact oss@thalesgroup.com.

## Disclosure policy

In your report, please consider providing with:
1. The version you are working with (that can be found with git log)
2. If you have found the first commit that introduced the vulnerability, please
provide with the commit number.
3. If you found a fix to the vulnerability, please use a pull request, as in the
[contributing](/CONTRIBUTING.md)

## Security Update policy

We will update by replying as soon as possible to the person who has found a
security issue.

## Security related configuration

If you intend to use PASCAL cloud, you will have to provide with credentials:
1. PASQAL account username
2. PASQAL project token
3. PASQAL password.

It is recommended to provide the password when it is asked by the cloud API,
instead of storing it somewhere.
In our experiments, we stored the data in an environment variable in order to
run multiple graphs sequentially without providing the password each time.

## Known security gaps & future enhancements

None

