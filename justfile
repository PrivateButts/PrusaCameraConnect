default:
    setup


setup:
    pdm sync --prod
    cp -n src/prusacameraconnect/example-config.yaml src/prusacameraconnect/config.yaml
    @echo "\nSetup complete. Please edit src/prusacameraconnect/config.yaml to your liking."
    @echo "Then run 'just run' to start the program."

setup-dev:
    pdm sync --dev
    pdm run pre-commit install


run:
    cd src/prusacameraconnect && pdm run python main.py


pre-commit:
    pdm run pre-commit run --all-files
