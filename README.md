# PrusaCameraConnect

A small server application to relay images to Prusa Connect.

## Configuration
The server is configured via a yaml file loaded from either the `APP_CONFIG` environmental variable or from a `config.yaml` file next to the `main.py`. Look at `example-config.yaml` for an example configuration file with comments to explain options.

### Printer Link
This server has the capability to snoop on your printer's status via PrusaLink. It's an optional feature that can be used to limit snapshot updates to only specific printer statuses, so you aren't uploading snapshots whenever the printer is idle. Here's the statuses that we can watch for:

- `IDLE`
- `BUSY`
- `READY`
- `PRINTING`
- `PAUSED`
- `FINISHED`
- `STOPPED`
- `ERROR`
- `ATTENTION`

I would recommend using the whole list but `IDLE`, `FINISHED`, and maybe `READY` and `STOPPED`.

### Handlers
The handler system is plugable, since every camera works a little differently. Below is a list of the included handlers and their options:

#### ImageUrlHandler
A simple handler that will fetch an image file from a url. Useful for some security cams and [Wyze Bridge](https://github.com/mrlt8/docker-wyze-bridge).

Import path: `Camera.ImageUrl.ImageUrlHandler`

Option | Required? | Description
-------|-----------|------------
`url`  |    Yes    | URL of the image to capture

## Deployment

This server is a simple python application that uses PDM to manage dependencies. A Docker image has been provided for some user's convenience.

### Docker

A Docker container has been provided at `ghcr.io/privatebutts/prusacameraconnect:main`. I've put an example Docker Compose file in the project repo as well.

Either method will require passing the config yaml into the container. You can do this with either a volume mount to `/app/config.yaml` or via the `APP_CONFIG` env. If both a file and env is present, the application will only look at the env.

### Manual

If you'd prefer to have more control over the deployment, you can install the application manually like any other pdm backed project. You'll need Python 3.11 and PDM installed before your start, then run this command to install all the dependencies:

```shell
pdm sync --prod
```

Then you can start the server with:

```shell
pdm run python main.py
```

from the `src/prusacameraconnect` directory.

A justfile has been provided for either reference or convenience.

## Example Tutorial, Wyze Camera

It's pretty common for people to use Wyze Cameras to keep an eye on their printer. Prusa Connect doesn't support those cameras offically, so we can use this server and [Wyze Bridge](https://github.com/mrlt8/docker-wyze-bridge) to get it in the panel.
