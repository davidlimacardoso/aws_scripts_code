# AWS Lambda Function Setup

This guide will help you set up an AWS Lambda function with the necessary dependencies.

## Steps to Create and Deploy Your Lambda Function

1. **Create a new directory for your Lambda function:**
```bash
   mkdir my_lambda_function
```
2. Navigate into the directory:
```bash
cd my_lambda_function
```
3. Create a virtual environment:
```bash
python3 -m venv venv
```
4. Activate the virtual environment:
```bash
source venv/bin/activate  # For Linux/Mac
# venv\Scripts\activate  # For Windows
```
5. Install the requests package:
```bash
pip install requests
```
6. Copy the installed packages to the current directory:
```bash
cp -r venv/lib/python3.10/site-packages/* .
```
7. Zip the contents for upload to AWS Lambda:
```bash
zip -r my_lambda_function.zip .
```
8. Deploying to AWS Lambda
After creating the ZIP file, you can upload it to your AWS Lambda function through the AWS Management Console or using the AWS CLI.

Notes
Make sure to replace python3.10 with the version you are using if it's different.
Ensure that you have the necessary AWS credentials configured to deploy your function.
