# Replace the GitHub repository contents from Windows

## Important

Do **not** delete the hidden `.git` folder. That folder contains the connection to GitHub.

## Safe replacement

1. Close VS Code.
2. Rename the current project folder to:

   `hamradio-pi-64ultimate-old`

3. Create a new folder named:

   `hamradio-pi-64ultimate`

4. Extract the clean project ZIP into that new folder.
5. Copy the hidden `.git` folder from the old folder into the new folder.
6. Open the new folder in VS Code.
7. In the VS Code terminal run:

```powershell
git status
git add -A
git commit -m "Replace repository with clean complete project"
git push
```

This replaces all repository files while preserving Git history.

## If GitHub rejects the push

First run:

```powershell
git pull --rebase
```

Then repeat:

```powershell
git push
```

Avoid `git push --force` unless you intentionally want to rewrite history.
