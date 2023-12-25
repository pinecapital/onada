#!/bin/bash

# Start Gunicorn with the specified configuration
sudo gunicorn -w 4 -b 0.0.0.0:80 main:app
