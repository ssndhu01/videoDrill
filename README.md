## Project Overview
VideoDrill is a tool designed to perform basic operations on video files. It provides functionalities such as trimming, merging, and converting video formats.

## Features
- **Trim Videos**: Cut out specific parts of a video.
- **Merge Videos**: Combine multiple video files into one.
- **Generate sharable Links**: Generate public link for sharing video for a limited time.


## Installation
To Run, Clone the repository and install the required dependencies:
```sh
git clone https://github.com/ssndhu01/videoDrill.git
cd videoDrill
docker-compose build 
docker-compose up -d 
```
OR<br>
Install python3.12 with pip for setting up the project locally.
```sh
git clone https://github.com/ssndhu01/videoDrill.git
cd videoDrill
python3.12 -m pip install virtualenv --user
python3.12 -m virtualenv -p python3.12 .venv
source .venv/bin/activate
pip3 install -r requirements.txt
cd videoSvc
python3 manage.py runserver 0.0.0.0:8000
```
To stop service
```sh
docker-compose stop
# or
Press Ctrl + C if running locally.
```

For running production grade application server, make below changes
```
Make DEBUG=False in settings.py
Remove the command in compose file: python3 manage.py runserver 0.0.0.0:8000
Command: gunicorn --bind 0.0.0.0:8000 -w4 --threads 4 videoSvc.wsgi:application
```
`w` and `threads` has to be changed according the container or server configuration.

For creating user for admin panel, this will work only when container is up.
```sh
docker exec -it videoSvc python3 manage.py createsuperuser
```
Access to admin panel
```
Open http://localhost:8000/admin in browser.
```

## Running Tests
To run test in docker environment, make sure docker container is running<br>
```sh
docker exec -it videoSvc python3 manage.py test
```
Above command is w.r.t. container start with docker-compose command.

To run test in local setup.
```sh
cd <repo path>/videoSvc
python3 manage.py test
```

## Usage
1) Create user for admin panel.
2) Make relevant entries for valid video formats for attaching to specific accounts.
3) Create an account for providing access to file management APIs.
4) Generate a token for API authentication.
5) Copy token and set `token` variable in postman environment.
6) Set `host` variable in postman environment. Kind set it to `http://localhost:8000` for running local APIs.
7) Import `postman collection` commited into the Repo for API.

## Assumptions & Considerations
Currently considered Django admin panel to Token generation and configuration managements.
<br>Stored API token in plain format. Hashing to be implemented for security purposes.
<br>Considered Min and Max duration can be between 1 to 300 seconds. Changable in settings.py
<br>Considered Maximum size can be below 50MB. Can be changed in settings.py.

### Video uploads
- Multiple files can be uploaded.
- Video formats to be allowed through admin panel in Accounts table.
- File stored outside application root. Can be stored on central location like AWS S3 or SFTP.
- Response will be a text message along with an ID. This <b>ID</b> to be used for subsequent API calls for different video operations.

### Video Trimming
- File id is considered as Input.
- Trim duration considered as integer value containing seconds. 
- `trim_from` parameter has two possible value ["start", "end"].

### Video Merging
- File ids is considered as Input.
- Atleast 2 ids to be passed.
- Considering codec of first video passed in the input.
- Using compose format for merging videos.
- `ffmpeg` could be used for transcoding videos before merging for better experience. 

### Sharable Public Links
- File ids is considered as Input.
- Considered HMAC token for signing public URL for validation and expiry time.



