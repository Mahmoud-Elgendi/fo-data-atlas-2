# Install and update 0.5.1

Requires the prerequisites and private GitHub access listed in the root README. Run in the intended project folder:

```powershell
npx.cmd --yes --package="git+https://github.com/Mahmoud-Elgendi/fo-data-atlas-2.git#v0.5.1" fo-data-atlas install --tag v0.5.1
npx.cmd --yes --package="git+https://github.com/Mahmoud-Elgendi/fo-data-atlas-2.git#v0.5.1" fo-data-atlas update --tag v0.5.1
npx.cmd --yes --package="git+https://github.com/Mahmoud-Elgendi/fo-data-atlas-2.git#v0.5.1" fo-data-atlas check --tag v0.5.1
```

Follow the wizard and host activation instructions. Existing metadata is reused when compatible. For EALLOWGIT or missing online prerequisites, use the documented browser-download/local-pack route; a new version does not remove device restrictions.
