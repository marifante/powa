# Power Warden application

This application is designed to monitor and control power domains using the Power Warden HAT, whose design can be found at: <https://github.com/marifante/rpi_power_warden_hat>.

## How it works

Originally, this application was designed to be used as a server that listens for commands and acts on them.
The server will monitor periodically the power domains, checking if current consumption is within the limits set by the user.
If the current consumption exceeds the limits, the server will turn off the power domain and set up a flag to indicate that the power domain was turned off due to overconsumption.

A client can send a request to the server to turn on the power domain through a REST API. Or if you like, you can connect using a web browser to the web interface that the application provides and control the power domains from there.

So, we can divide the application in the following components: the server and the web interface.

### Server

### Web interface

## Usage

This application is distributed as a python pip package and as a docker image.

If you want to install it as a python pip package just run: To install it just run: `pip install git+https://github.com/marifante/powa.git`.

On the other hand, you could also download the docker image that brings the application pre-installed in an ubuntu image. To do so, you can run: `docker pull ghcr.io/marifante/powa:latest` or use the tag that you like.

## Testing

We have 2 types of tests for this application: unit tests and integration tests.

### Unit Testing

The unit-tests of this application are made with pytest. To run them you can run `make unit-tests` or `pytest` from the root directory of the project.

### Integration Testing

![Power Warden Character](doc/powa_char.png)
