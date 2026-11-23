# Install or update 0.5.2

Use the README for prerequisites and the offline route on restricted devices. The existing installer still uses GitHub CLI and Python; making the repository public alone does not remove those requirements.

```powershell
npx.cmd -y github:Mahmoud-Elgendi/fo-data-atlas-2#v0.5.2 install --tag v0.5.2
npx.cmd -y github:Mahmoud-Elgendi/fo-data-atlas-2#v0.5.2 update --tag v0.5.2
npx.cmd -y github:Mahmoud-Elgendi/fo-data-atlas-2#v0.5.2 check --tag v0.5.2
```

Git-backed acquisition remains subject to npm package-source policy, including EALLOWGIT. Follow host activation instructions after setup. Existing matching metadata is reused.
