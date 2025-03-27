@echo off
echo Deploying to Razorhost via GitHub...
echo.

:: Add all changes
git add .

:: Commit changes
set /p commit_msg="Enter commit message: "
git commit -m "%commit_msg%"

:: Push to GitHub
echo Pushing to GitHub...
git push origin main

echo.
echo Your code has been pushed to GitHub.
echo.
echo To deploy to Razorhost:
echo 1. Login to your cPanel
echo 2. Navigate to 'Git Version Control'
echo 3. Click 'Create' to create a new deployment
echo 4. Use your GitHub repository URL: https://github.com/RANJ1234/RemoteJobNexus.git
echo 5. Set the deployment path to: public_html
echo 6. Click 'Create' to set up the deployment
echo.
echo Once set up, you can click 'Manage' and then 'Update' to deploy the latest code.
echo.
pause 