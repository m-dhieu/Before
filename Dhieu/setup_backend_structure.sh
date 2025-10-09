#!/bin/bash

# Define base backend directory
BACKEND_DIR="backend"

# Create directories
mkdir -p $BACKEND_DIR/{models,controllers,routes,services,utils,tests}

# Create files
touch $BACKEND_DIR/app.py
touch $BACKEND_DIR/config.py
touch $BACKEND_DIR/database.py
touch $BACKEND_DIR/models/trip.py
touch $BACKEND_DIR/controllers/trip_controller.py
touch $BACKEND_DIR/routes/trip_routes.py
touch $BACKEND_DIR/services/data_cleaning.py
touch $BACKEND_DIR/utils/logger.py
touch $BACKEND_DIR/tests/test_trip.py
touch $BACKEND_DIR/requirements.txt
touch $BACKEND_DIR/README.md

echo "Backend structure (folders and files) created successfully."
