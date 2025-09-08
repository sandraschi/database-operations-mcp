# DXT Package Builder

This directory contains the build and test infrastructure for creating DXT packages for the Database Operations MCP.

## Directory Structure

```
dxt/
├── build.ps1         # Main build script for creating DXT packages
├── tests/            # Test files for DXT package validation
│   └── test_dxt_package.py
└── README.md         # This file
```

## Prerequisites

- Python 3.9+
- DXT CLI installed (`pip install dxt`)
- PowerShell 5.1+

## Building the DXT Package

To build the DXT package, run the following command from the project root:

```powershell
# From project root
.\dxt\build.ps1
```

The built package will be placed in the `dist` directory with a `.dxt` extension.

## Testing

Run the DXT package tests with:

```bash
# Run all tests
pytest dxt/tests/

# Run a specific test file
pytest dxt/tests/test_dxt_package.py -v
```

## CI/CD Integration

The `.github/workflows/dxt-ci.yml` file defines the GitHub Actions workflow for building and testing the DXT package. It runs on:
- Push to `main` or `develop` branches
- Pull requests targeting `main` or `develop`

## Best Practices

1. **Versioning**: Update the version in `manifest.json` for each release
2. **Testing**: Add tests for new DXT package features
3. **Documentation**: Update this README when making significant changes
4. **Validation**: Always validate the manifest before building

## Troubleshooting

- If the build fails, check the output of `build.ps1` for errors
- Ensure all required files are included in the package (check `manifest.json`)
- Verify that the DXT CLI is installed and in your PATH
