# Install and verify 0.4.1

After the stable release is published, an authorized user with Node.js 22+, Git, Python 3.10+ and authenticated GitHub CLI can run:

```powershell
npx --yes --package="git+https://github.com/Mahmoud-Elgendi/fo-data-atlas-2.git#v0.4.1" fo-data-atlas install --tag v0.4.1
```

Run gh auth login and gh auth setup-git once when GitHub access is not configured. Choose host/scope/profile in the wizard, then follow native activation instructions. Compatible caches are reused. Per-project Fabric schema and source choices remain the recipient's configuration. Metadata helpers are offline; acquiring uncached packages and AI inference are separate connectivity requirements.

Read-only release check:

```powershell
npx --yes --package="git+https://github.com/Mahmoud-Elgendi/fo-data-atlas-2.git#v0.4.1" fo-data-atlas check --tag v0.4.1
```

The SQLite fixture suite is run with python -m unittest discover -s tests -v. It does not compile templates in Fabric. Configure every SQL template parameter against recipient evidence before use. No recipient endpoint, user, document identifier or actual live result belongs in the reusable release.
