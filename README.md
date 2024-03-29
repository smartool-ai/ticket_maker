# Ticket Maker

# Configure poetry to use our core package
Run the following command to configure poetry to use our core package:
```bash
poetry config repositories.gemfury https://jake-pixelum.fury.site/pypi
poetry config http-basic.gemfury $GEMFURY_TOKEN NOPASS
```