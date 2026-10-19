Project3Studios V2.2.2 — complete app and deployment package

1. Save any current sculpt project before updating.
2. Extract this ZIP. Upload ALL of its files and folders into your existing V2 repository root. Keep index.html at the root, alongside engine/ and vendor/. Upload the contents, not the ZIP itself. Include .github/workflows/deploy.yml; replace the existing deploy.yml with this copy.
3. In the V2 repository, choose Settings > Pages > Source > GitHub Actions.
4. In Actions, keep "Deploy V2 to GitHub Pages" as your publishing workflow. Disable duplicate Jekyll/static Pages workflows through their workflow menu. This ZIP does not remove existing workflows from your repository.
5. Commit the upload to main. The new workflow runs automatically. It also supports Actions > Deploy V2 to GitHub Pages > Run workflow.
6. Open the latest run. After a successful deployment, open its published URL and refresh the app. Confirm release 2.2.2 in the app diagnostics.

This package retains the stronger brushes and the fixed Alpha Stamp Strength control. It includes local graphics dependencies, the Wasm worker, icons, and a deployment workflow with required-file checks.

Queued jobs:
A fresh package does not necessarily clear GitHub runner queues, account restrictions, required approvals, or service delays. Old queued runs remain in the repository. Cancel superseded runs if desired. The latest workflow cancels older runs that share its concurrency group; other workflow groups remain independent. If the latest run stays queued, inspect its runner/approval message rather than repeatedly uploading.

The workflow was checked locally; it has not been run in your GitHub account by this chat. V1 files/settings are separate.

Reference: https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages
