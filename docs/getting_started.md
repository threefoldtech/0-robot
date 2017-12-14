# Getting started

## Install ZeroRobot
TODO: block on jumspcale install

## Start the robot:
```
# zrobot --help
Usage: zrobot [OPTIONS]

Options:
  -D, --data-repo TEXT      URL of the git repository where to save the data
                            of the zero robot  [required]
  -T, --template-repo TEXT  list of templare repository URL
  -L, --listen TEXT         listen address
  -R, --robots TEXT         address of reachable robots
  --help                    Show this message and exit.
```
Options details:

- `--data-repo`: The URL of a git repository where the data of your services will be stored. When starting, the robot also loads all the services present in this repository.
This parameter is required for the robot to starts.

- `--temlate-repo` The URL of a repository that contains templates. You can give multiple template repository by give multiple time the parameter.
- `--listen`: The interface and port on which the robot REST API need to listen to. Has to be under the form `host:port`  
e.g: `0.0.0.0:8080`
- `--robots` The URL of any other robots that needs to be reachable from this robot. You can give multiple robot URL by give multiple time the parameter.

### example:
```bash
zrobot --listen :6601 --template-repo https://github.com/jumpscale/zerorobot.git --data-repo https://github.com/user/zrobot1.git --robots http://localhost:6602
```