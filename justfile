default:
    setup


setup:
    pdm sync --prod
    cp -n src/prusacameraconnect/example-config.yaml src/prusacameraconnect/config.yaml
    @echo "\nSetup complete. Please edit src/prusacameraconnect/config.yaml to your liking."
    @echo "Then run 'just run' to start the program."


run:
    cd src/prusacameraconnect && pdm run python main.py
