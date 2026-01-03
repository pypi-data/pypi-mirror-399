# Publishing Guide: CLI Todo App to PyPI

This guide will help you publish `cli-todo-app` to PyPI so users can install it globally using `pip` or `uv`.

## Prerequisites

1. **PyPI Account**: Create an account at https://pypi.org/account/register/
2. **API Token**: Generate an API token at https://pypi.org/manage/account/token/
   - Create a new token
   - Scope: "Entire account" (for first publish) or specific project
   - Save the token - you'll only see it once!

3. **Install Required Tools**:
   ```bash
   pip install build twine
   # OR with uv
   uv pip install build twine
   ```

## Update GitHub Repository URLs

Before publishing, update the repository URLs in `pyproject.toml`:

```toml
[project.urls]
Homepage = "https://github.com/YOUR_USERNAME/Hackthon-II-Todo-App"
Repository = "https://github.com/YOUR_USERNAME/Hackthon-II-Todo-App"
Issues = "https://github.com/YOUR_USERNAME/Hackthon-II-Todo-App/issues"
```

Replace `YOUR_USERNAME` with your actual GitHub username.

## Build Distribution Packages

Run this command to build the distribution packages:

```bash
python -m build
```

This creates:
- `dist/cli_todo_app-0.1.0.tar.gz` (source distribution)
- `dist/cli_todo_app-0.1.0-py3-none-any.whl` (wheel)

## Test Build Locally

Before publishing, test the built package:

```bash
# Install the built package
pip install dist/cli_todo_app-0.1.0-py3-none-any.whl

# Test it works
todo --help
todo add "Test task"
todo list

# Uninstall after testing
pip uninstall cli-todo-app
```

## Step 1: Publish to TestPyPI (Recommended First)

TestPyPI is a separate instance of PyPI for testing. Always test here first!

### 1. Upload to TestPyPI

```bash
python -m twine upload --repository testpypi dist/*
```

Enter your username and password/API token when prompted.

### 2. Install from TestPyPI

```bash
# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ cli-todo-app

# Test it
todo --help

# Uninstall
pip uninstall cli-todo-app
```

### 3. Fix Any Issues

If there are problems, make changes, rebuild, and upload again:
```bash
# Update version in pyproject.toml
# Rebuild
python -m build
# Re-upload
python -m twine upload --repository testpypi dist/*
```

## Step 2: Publish to Production PyPI

Once everything works on TestPyPI, publish to the real PyPI!

### Option A: Upload with Username/Password

```bash
python -m twine upload dist/*
```

### Option B: Use API Token (Recommended)

Save your token to `~/.pypirc` (create if doesn't exist):

```ini
[pypi]
  username = __token__
  password = pypi-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

[testpypi]
  username = __token__
  password = pypi-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Then upload:
```bash
python -m twine upload dist/*
```

## Verify Publication

1. Check https://pypi.org/project/cli-todo-app/
2. Verify all metadata appears correctly
3. Try installing from PyPI:

```bash
pip install cli-todo-app
# OR with uv
uv pip install cli-todo-app

# Test it
todo --help
```

## Commit and Push to GitHub

After successful PyPI publication, push your code to GitHub:

```bash
# Add all changes
git add .

# Commit
git commit -m "Publish cli-todo-app v0.1.0 to PyPI

- Add README.md with installation and usage instructions
- Add LICENSE file (MIT)
- Update pyproject.toml with PyPI metadata
- Build distribution packages
- Publish to PyPI"

# Push to remote
git push origin main
```

## Publishing Future Versions

When you want to release a new version:

1. **Update version in `pyproject.toml`**:
   ```toml
   version = "0.2.0"  # Follow semantic versioning
   ```

2. **Update `CHANGELOG.md`** (create one if you don't have it)

3. **Build and upload**:
   ```bash
   python -m build
   python -m twine upload dist/*
   ```

4. **Commit and push**:
   ```bash
   git add .
   git commit -m "Release v0.2.0"
   git push origin main
   ```

## Troubleshooting

### "Package already exists"

If you get an error that the package name is taken:
1. Choose a different name (e.g., `hackathon-todo-cli`, `simple-todo-app`)
2. Update `name` in `pyproject.toml`
3. Rebuild and try again

### "403 Forbidden"

- Check that your API token has correct permissions
- Ensure you're using the correct username/password combination

### "File already exists"

PyPI doesn't allow re-uploading the same version. You must:
1. Increment the version number in `pyproject.toml`
2. Rebuild
3. Upload again

### Upload Hangs

- Check your internet connection
- Try using the verbose flag: `python -m twine upload --verbose dist/*`

## Security Best Practices

1. ✅ Use API tokens instead of passwords
2. ✅ Never commit `.pypirc` to git
3. ✅ Use TestPyPI first for all releases
4. ✅ Verify package checksums: `python -m twine check dist/*`
5. ✅ Use `--skip-existing` to skip already uploaded files
6. ✅ Keep your API tokens secure and rotate them regularly

## Automated Publishing (Optional)

For automated publishing with GitHub Actions, create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - name: Install build dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build twine
      - name: Build package
        run: python -m build
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}
```

Set `PYPI_API_TOKEN` in GitHub repository secrets.

## Resources

- [PyPI Packaging Tutorial](https://packaging.python.org/tutorials/packaging-projects/)
- [PyPI User Guide](https://docs.pypi.org/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [PEP 621: Project Metadata](https://peps.python.org/pep-0621/)
