# GitHub Workflows for create-ragbits-app

## PyPI Publishing Workflow

The `publish-pypi.yml` workflow publishes the `create-ragbits-app` package to PyPI.

### Triggering the workflow

This workflow can be triggered remotely from the main ragbits repository or manually from the GitHub UI.

#### Remote trigger from ragbits repository

From the ragbits repository, you can trigger this workflow using the GitHub CLI or API:

```bash
# Using GitHub CLI - Auto-increment patch version
gh workflow run publish-pypi.yml \
  --repo deepsense-ai/create-ragbits-app \
  --field release_type="patch"

# Using GitHub CLI - Manual version
gh workflow run publish-pypi.yml \
  --repo deepsense-ai/create-ragbits-app \
  --field manual_version="0.0.12"

# Using GitHub CLI - Dry run with minor version bump
gh workflow run publish-pypi.yml \
  --repo deepsense-ai/create-ragbits-app \
  --field release_type="minor" \
  --field dry_run="true"

# Or using curl with GitHub API - Auto-increment patch
curl -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/deepsense-ai/create-ragbits-app/actions/workflows/publish-pypi.yml/dispatches \
  -d '{"ref":"main","inputs":{"release_type":"patch","create_github_release":"true","dry_run":"false"}}'

# Using curl with manual version
curl -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/deepsense-ai/create-ragbits-app/actions/workflows/publish-pypi.yml/dispatches \
  -d '{"ref":"main","inputs":{"manual_version":"0.0.12","create_github_release":"true","dry_run":"false"}}'
```

#### Manual trigger from GitHub UI

1. Go to Actions tab in the create-ragbits-app repository
2. Select "Publish create-ragbits-app to PyPI" workflow
3. Click "Run workflow"
4. Configure the options:
   - **Release type**: Choose `patch`, `minor`, `major`, or `none` (auto-increments version)
   - **Manual version**: Optionally specify exact version (e.g., "0.0.12") - overrides release type
   - **Create GitHub release**: Whether to create a GitHub release (default: true)
   - **Dry run**: Build only without publishing (default: false)
5. Click "Run workflow"

#### Manual Trigger Options

- **Automatic versioning**: Select a release type (patch/minor/major) to auto-increment from current version
- **Manual versioning**: Specify exact version number (overrides release type)
- **Dry run mode**: Test the build process without actually publishing to PyPI
- **GitHub release**: Control whether to create a GitHub release with artifacts

### Required Secrets

The following secrets must be set in the repository settings:

- `PYPI_TOKEN`: PyPI API token for publishing packages
  - Go to https://pypi.org/manage/account/token/
  - Create a new API token with scope for the `create-ragbits-app` project
  - Copy the token (starts with `pypi-`)
  - Add it as a repository secret

### What the workflow does

1. **Determines version**: Either uses manual version or auto-increments based on release type (patch/minor/major)
2. **Updates version**: Modifies the version in `pyproject.toml` with the determined version
3. **Builds package**: Uses `uv build` to create wheel and source distributions
4. **Publishes to PyPI**: Uses `twine upload` to publish the package (skipped in dry-run mode)
5. **Creates git tag**: Tags the commit with the version number (skipped in dry-run mode)
6. **Creates GitHub release**: Creates a GitHub release with built artifacts (optional, skipped in dry-run mode)

#### Dry Run Mode

When `dry_run` is enabled, the workflow will:
- Build the package and verify it's correct
- Show what version would be published
- Skip actual publishing to PyPI
- Skip creating git tags and GitHub releases
- Provide a summary of what would happen in a real run

### Prerequisites

- The workflow requires Python 3.11+ and uses `uv` for package management
- The repository must have the `PYPI_TOKEN` secret configured
- The user triggering the workflow must have appropriate permissions

### Troubleshooting

- **Permission denied**: Ensure the `PYPI_TOKEN` secret is correctly set
- **Version already exists**: PyPI doesn't allow re-uploading the same version
- **Build failures**: Check that the `pyproject.toml` file is valid and all dependencies are available
