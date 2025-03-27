@echo off
echo Deploying to Razorhost...
echo.

:: Add all changes
git add .

:: Commit changes
set /p commit_msg="Enter commit message: "
git commit -m "%commit_msg%"

:: Create and update a zip file of the project
echo Creating deployment package...
powershell -Command "Compress-Archive -Path * -DestinationPath deploy.zip -Force"

echo.
echo Your deployment package is ready: deploy.zip
echo.
echo Next steps:
echo 1. Upload deploy.zip to your Razorhost cPanel using File Manager
echo 2. Extract the contents to your public_html folder
echo.
echo Deployment package created successfully!
pause 