# Ticket Maker

### Configuring Poetry to Use Gemfury

For security reasons, avoid hardcoding your Gemfury access token in `pyproject.toml`. Instead, configure Poetry to authenticate with Gemfury dynamically:

Run the following command to configure poetry to use our core package:
```bash
poetry config repositories.gemfury https://jake-pixelum.fury.site/pypi
poetry config http-basic.gemfury $GEMFURY_TOKEN NOPASS
```

1. **Add Gemfury as a Repository**:

    Configure Gemfury as a custom repository. Replace `USERNAME` with your Gemfury username.

    ```bash
    poetry config repositories.gemfury https://jake-pixelum.fury.site/pypi
    ```

2. **Authenticate with Gemfury**:

    ```bash
    poetry config http-basic.gemfury $GEMFURY_TOKEN NOPASS
    ```

### Installing Packages

Once Gemfury is configured as a repository, you can install packages as you normally would:

```bash
poetry install
```