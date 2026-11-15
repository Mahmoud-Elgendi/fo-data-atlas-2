# Install and update

Requirements and offline alternatives are described in the repository README. Authenticate with `gh auth login` and `gh auth setup-git` before private Git-backed acquisition.

```powershell
npx.cmd --yes --package="git+https://github.com/Mahmoud-Elgendi/fo-data-atlas-2.git#v0.5.0" fo-data-atlas install --tag v0.5.0
npx.cmd --yes --package="git+https://github.com/Mahmoud-Elgendi/fo-data-atlas-2.git#v0.5.0" fo-data-atlas update --tag v0.5.0
npx.cmd --yes --package="git+https://github.com/Mahmoud-Elgendi/fo-data-atlas-2.git#v0.5.0" fo-data-atlas check --tag v0.5.0
```

Main plus latest published stable tools:

```powershell
npx.cmd --yes --package="git+https://github.com/Mahmoud-Elgendi/fo-data-atlas-2.git#main" fo-data-atlas update
```

A blocked Git-package source or missing prerequisites prevents this route; use the documented browser/local-pack method rather than bypassing restrictions. Native host activation follows setup.
