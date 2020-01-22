# Image pipeline 

## The software 
This software is a server for image processing with a REST API. It it currently implemented with a FloydHub backend demoing some deep learning code. It currently uses the shell to process the workload but so it could be any program.

### Features

The API features:
 - upload of a picture
 - download of a picture
 - download of the image after processing
 - user creation
 - user login
 - user based pemissioning

## The code

### License

The software is free but copyrighted. It is copyrighted under the [JRL license](https://en.wikipedia.org/wiki/Java_Research_License), commercial or proprietary use is forbidden but research and academic use are allowed.

The deep learning code comes from https://github.com/wxs/subjective-functions and has its own license (check Github).

### Implementation details

The server is a Django server with a PostgreSQL database.
