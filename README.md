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

I would recommend using the whole list but `IDLE`, `FINISHED`, and maybe `READY` and `STOPPED`. Here's what I've been using:

```yaml
snapshot_states:
- BUSY
- READY
- PRINTING
- PAUSED
- ERROR
- ATTENTION
```

### Handlers
The handler system is plugable, since every camera works a little differently. Below is a list of the included handlers and their options:

#### ImageUrlHandler
A simple handler that will fetch an image file from a url. Useful for some security cams and [Wyze Bridge](https://github.com/mrlt8/docker-wyze-bridge).

Import path: `Camera.ImageUrl.ImageUrlHandler`

Option | Required? | Description
-------|-----------|------------
`url`  |    Yes    | URL of the image to capture

#### VideoCaptureHandler
This use's [OpenCV's videoio system](https://docs.opencv.org/4.x/d0/da7/videoio_overview.html) to capture a variety of video sources. Can use several backends depending on what's available on your system.

Import path: `Camera.VideoUrl.VideoCaptureHandler`

Option | Required? | Description
-------|-----------|------------
`url`  |    Yes    | URL of the video stream. E.G. `rtsp://0.0.0.0:8445/printer`

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

It's pretty common for people to use Wyze Cameras to keep an eye on their printer. Prusa Connect doesn't support those cameras offically, so we can use this server and [Wyze Bridge](https://github.com/mrlt8/docker-wyze-bridge) to get it in the panel. This tutorial will assume that you have Wyze Bridge up and running, and a working install of Docker.

1. Set up a clean folder to work in.
2. Download this repo's [docker-compose.yaml](docker-compose.yaml) to that folder
3. Remove the `build:` block from the yaml file. This is only needed if you want to make custom changes to the source code.
4. Choose to configure with either `APP_CONFIG` environmental variable or a file you'll mount into the container.

> An example of the config file can be found [here](src/prusacameraconnect/example-config.yaml)

5. Update the config values to match your setup. You can make multiple camera entries to cover multiple printer/camera combos.

- Just randomly generate a longish string for fingerprint
- You can get token from the camera tab of Prusa Connect. Click "Add new other camera" then copy the token of the new entry.
![Screenshot of the section in Prusa Connect where you can create a new camera](docs/images/prusa%20connect%20camera%20creation.png)
- Pick a handler based on what feeds you get out of your camera. For example, Wyze Brige exposes a snapshot url that `Camera.ImageUrl.ImageUrlHandler` can scrape. You can find the url by hovering over the "Streams" button of the camera, then copying the url from the "RTSP Snapshot" menu option.
![Screenshot of Wyze Bridge showing where the link is](docs/images/wyze%20rtsp%20stream.png)
- `printer_link` is optional. Not providing it will cause the server to constantly relay snapshots to prusa cloud. I prefer to only have it update when the printer is in use, ready, or requires intervention or attention. Use the credentials in your printer's settings, url will most likely be http:// + ip address of your printer.

5. Start the server with `docker compose up`. To start in background, use `-d`.

6. You should start seeing snapshots in the Prusa Connect dashboard.