"""
Email utility functions for TutorConnect application.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app, url_for

def send_email(to_email, subject, html_body, text_body=None):
    """
    Send an email using the configured SMTP settings.
    
    Args:
        to_email (str): Recipient email address
        subject (str): Email subject
        html_body (str): HTML email body
        text_body (str, optional): Plain text email body
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = current_app.config['MAIL_DEFAULT_SENDER']
        msg['To'] = to_email
        
        # Add text body if provided
        if text_body:
            text_part = MIMEText(text_body, 'plain')
            msg.attach(text_part)
        
        # Add HTML body
        html_part = MIMEText(html_body, 'html')
        msg.attach(html_part)
        
        # Connect to SMTP server and send email
        with smtplib.SMTP(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT']) as server:
            if current_app.config['MAIL_USE_TLS']:
                server.starttls()
            
            if current_app.config['MAIL_USERNAME'] and current_app.config['MAIL_PASSWORD']:
                server.login(current_app.config['MAIL_USERNAME'], current_app.config['MAIL_PASSWORD'])
            
            server.send_message(msg)
        
        return True
        
    except Exception as e:
        current_app.logger.error(f"Failed to send email: {str(e)}")
        return False

def send_password_reset_email(email, reset_token):
    """
    Send a password reset email to the user.
    
    Args:
        email (str): User's email address
        reset_token (str): The password reset token
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    # Generate reset URL
    reset_url = url_for('auth.reset_password', token=reset_token, _external=True)
    
    subject = "Reset Your TutorConnect Password"
    
    # HTML email body
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Reset Your Password</title>
        <style>
            body {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f8fafc;
            }}
            .container {{
                background-color: #ffffff;
                border-radius: 8px;
                padding: 40px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                text-align: center;
                margin-bottom: 40px;
            }}
            .logo {{
                color: #22d3ee;
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 10px;
            }}
            .title {{
                color: #1e293b;
                font-size: 28px;
                font-weight: bold;
                margin-bottom: 10px;
            }}
            .subtitle {{
                color: #64748b;
                font-size: 16px;
            }}
            .content {{
                margin-bottom: 30px;
            }}
            .button {{
                display: inline-block;
                background: linear-gradient(135deg, #22d3ee 0%, #3b82f6 100%);
                color: white;
                text-decoration: none;
                padding: 14px 28px;
                border-radius: 8px;
                font-weight: 600;
                text-align: center;
                margin: 20px 0;
            }}
            .button:hover {{
                transform: translateY(-1px);
                box-shadow: 0 4px 8px rgba(34, 211, 238, 0.3);
            }}
            .footer {{
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #e2e8f0;
                font-size: 14px;
                color: #64748b;
                text-align: center;
            }}
            .warning {{
                background-color: #fef3c7;
                border: 1px solid #f59e0b;
                border-radius: 6px;
                padding: 16px;
                margin: 20px 0;
                color: #92400e;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">TutorConnect</div>
                <h1 class="title">Reset Your Password</h1>
                <p class="subtitle">We received a request to reset your password</p>
            </div>
            
            <div class="content">
                <p>Hello,</p>
                <p>You recently requested to reset your password for your TutorConnect account. Click the button below to reset your password:</p>
                
                <div style="text-align: center;">
                    <a href="{reset_url}" class="button">Reset Password</a>
                </div>
                
                <div class="warning">
                    <strong>⚠️ Security Notice:</strong> This link will expire in 1 hour for your security. If you did not request this password reset, please ignore this email and your password will remain unchanged.
                </div>
                
                <p>If the button above doesn't work, copy and paste the following link into your browser:</p>
                <p style="word-break: break-all; color: #3b82f6;">{reset_url}</p>
            </div>
            
            <div class="footer">
                <p>If you didn't request this password reset, you can safely ignore this email.</p>
                <p>Best regards,<br>The TutorConnect Team</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Plain text fallback
    text_body = f"""
    Reset Your TutorConnect Password
    
    Hello,
    
    You recently requested to reset your password for your TutorConnect account.
    
    Click the following link to reset your password:
    {reset_url}
    
    This link will expire in 1 hour for your security.
    
    If you did not request this password reset, please ignore this email and your password will remain unchanged.
    
    Best regards,
    The TutorConnect Team
    """
    
    return send_email(email, subject, html_body, text_body)