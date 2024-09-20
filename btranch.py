import boto3
import subprocess
import os
import paramiko
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

# Initialize AWS Transfer Family and IAM client
transfer_client = boto3.client('transfer')
iam_client = boto3.client('iam')

# Function to create a new AWS Transfer Family SFTP user
def create_transfer_user(user_name, role_arn, home_directory):
    response = transfer_client.create_user(
        ServerId='s-xxxxxxxxxx',  # Replace with your server ID
        UserName=user_name,
        Role=role_arn,
        HomeDirectory=home_directory
    )
    return response

# Function to generate SSH key pair
def generate_ssh_key(user_name):
    key = paramiko.RSAKey.generate(2048)
    private_key = f"{user_name}_private_key.pem"
    public_key = f"{user_name}_public_key.pub"

    # Save private key
    key.write_private_key_file(private_key)

    # Get public key
    public_key_str = f"ssh-rsa {key.get_base64()}"

    with open(public_key, 'w') as pub_file:
        pub_file.write(public_key_str)

    return private_key, public_key_str

# Function to assign IAM role and attach policies
def assign_iam_role(user_name, policy_arn):
    role_name = f"{user_name}_sftp_role"
    
    # Create the role
    iam_client.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument=json.dumps({
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Effect': 'Allow',
                    'Principal': {
                        'Service': 'transfer.amazonaws.com'
                    },
                    'Action': 'sts:AssumeRole'
                }
            ]
        })
    )
    
    # Attach policy to the role
    iam_client.attach_role_policy(
        RoleName=role_name,
        PolicyArn=policy_arn
    )
    
    return f"arn:aws:iam::xxxxxxxxxx:role/{role_name}"

# Function to set FSx permissions (Linux server)
def set_fsx_permissions(user_name):
    user_home_dir = f"/fsx/{user_name}"
    
    # Mount FSx (if not already mounted)
    mount_command = "sudo mount -t nfs4 fs-xxxxxxxxxx.efs.aws-region.amazonaws.com:/ /fsx"
    subprocess.run(mount_command, shell=True)
    
    # Create user directory and set ownership/permissions
    subprocess.run(f"sudo mkdir {user_home_dir}", shell=True)
    subprocess.run(f"sudo chown {user_name}:{user_name} {user_home_dir}", shell=True)
    subprocess.run(f"sudo chmod 700 {user_home_dir}", shell=True)

    return user_home_dir

# Function to send SSH key via email (SMTP)
def send_ssh_key_via_email(admin_email, user_name, private_key_path):
    msg = MIMEMultipart()
    msg['From'] = "noreply@yourdomain.com"
    msg['To'] = admin_email
    msg['Subject'] = f"SFTP Credentials for {user_name}"

    body = f"Attached is the private SSH key for user {user_name}.\n\n"
    msg.attach(MIMEText(body, 'plain'))

    with open(private_key_path, 'r') as file:
        private_key = file.read()

    attachment = MIMEText(private_key)
    attachment.add_header('Content-Disposition', 'attachment', filename=Path(private_key_path).name)
    msg.attach(attachment)

    # Send the email
    server = smtplib.SMTP('smtp.your-email-provider.com', 587)
    server.starttls()
    server.login("youremail@yourdomain.com", "your-email-password")
    server.send_message(msg)
    server.quit()

    print(f"SSH key sent to {admin_email}")

# Main function to onboard a new user
def onboard_user(user_name, admin_email):
    try:
        # Generate SSH key for the user
        private_key, _ = generate_ssh_key(user_name)
        
        # Assign IAM role and policy
        role_arn = assign_iam_role(user_name, 'arn:aws:iam::aws:policy/AmazonS3FullAccess')

        # Create the user in AWS Transfer Family
        create_transfer_user(user_name, role_arn, f"/fsx/{user_name}")

        # Set up FSx permissions on Linux
        user_home_dir = set_fsx_permissions(user_name)

        # Send SSH key to admin
        send_ssh_key_via_email(admin_email, user_name, private_key)

        print(f"User {user_name} onboarded successfully with home directory {user_home_dir}")

    except Exception as e:
        print(f"Error onboarding user {user_name}: {str(e)}")

# Example usage
onboard_user("new_vendor_user", "admin@yourcompany.com")

def set_fsx_permissions(user_name):
    f"/fsx/{user_name}"
    
    mount_command = "sudo mount -t nfs4 fs -xxxxxxxx.efs.aws-region.amazonaws.com: / /fsx"
    subprocess.run(mount_command , shell=True)





#NEW LINES ADDED TO THE FILES OF THE BTRANCH.py WHICH ARE JUST SOME COMMENTS TO CHECK THE COMMITS.

        