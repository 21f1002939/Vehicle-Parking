from app import celery, app
from models import db, User, ParkingLot, Reservation
from datetime import datetime, timedelta, timezone
from sqlalchemy import func
import csv
import io
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

@celery.task
def send_daily_reminder():
    """
    Daily reminder job - Check users who haven't booked and send notification
    Runs every day at 6 PM
    """
    try:
        today = datetime.now(timezone.utc).date()
        users = User.query.filter_by(is_admin=False, is_active=True).all()
        
        inactive_users = []
        for user in users:
            last_reservation = Reservation.query.filter_by(user_id=user.id).order_by(
                Reservation.created_at.desc()
            ).first()
            
            if not last_reservation or last_reservation.created_at.date() < today:
                inactive_users.append(user)
        
        if inactive_users:
            for user in inactive_users:
                send_reminder_notification(user)
        
        return f"Daily reminders sent to {len(inactive_users)} users"
    
    except Exception as e:
        return f"Error: {str(e)}"


@celery.task
def generate_monthly_report():
    """
    Monthly activity report - Generate and send report to all users
    Runs on 1st of every month at 9 AM
    """
    try:
        users = User.query.filter_by(is_admin=False, is_active=True).all()
        
        last_month = datetime.utcnow().replace(day=1) - timedelta(days=1)
        month_start = last_month.replace(day=1)
        month_end = last_month.replace(day=1) + timedelta(days=32)
        month_end = month_end.replace(day=1) - timedelta(days=1)
        
        reports_sent = 0
        for user in users:
            reservations = Reservation.query.filter(
                Reservation.user_id == user.id,
                Reservation.created_at >= month_start,
                Reservation.created_at <= month_end
            ).all()
            
            if reservations:
                report_html = generate_report_html(user, reservations, last_month)
                send_email_report(user, report_html, last_month)
                reports_sent += 1
        
        return f"Monthly reports sent to {reports_sent} users"
    
    except Exception as e:
        return f"Error: {str(e)}"


@celery.task
def export_user_parking_history(user_id):
    """
    Export user parking history to CSV - User triggered async job
    Sends email with CSV attachment using MailHog
    """
    try:
        with app.app_context():
            user = User.query.get(user_id)
            if not user:
                return {"status": "error", "message": "User not found"}
            
            reservations = Reservation.query.filter_by(user_id=user_id).order_by(
                Reservation.created_at.desc()
            ).all()
            
            if not reservations:
                return {"status": "error", "message": "No parking history found"}
            
            csv_content = generate_csv_export(reservations)
            
            # Send email with CSV attachment
            send_csv_notification(user, csv_content)
            
            return {
                "status": "success",
                "message": f"CSV export completed for {user.username}",
                "records_exported": len(reservations)
            }
    
    except Exception as e:
        return {"status": "error", "message": f"Export failed: {str(e)}"}


def send_reminder_notification(user):
    """
    Send reminder notification to user
    Can use email, SMS, or Google Chat webhook
    """
    subject = "Parking Reminder - Book Your Spot Today!"
    
    message = f"""
    Hello {user.username},
    
    We noticed you haven't booked a parking spot today.
    
    Don't miss out! Book your parking spot now and enjoy hassle-free parking.
    
    Available parking lots are waiting for you.
    
    Best regards,
    Vehicle Parking Management System
    """
    
    send_email(user.email, subject, message)


def generate_report_html(user, reservations, month):
    """
    Generate HTML monthly activity report
    """
    total_bookings = len(reservations)
    total_spent = sum(r.parking_cost or 0 for r in reservations)
    total_hours = sum(r.get_duration_hours() for r in reservations)
    
    lot_usage = {}
    for res in reservations:
        lot_name = res.parking_spot.parking_lot.prime_location_name
        lot_usage[lot_name] = lot_usage.get(lot_name, 0) + 1
    
    most_used_lot = max(lot_usage.items(), key=lambda x: x[1])[0] if lot_usage else "N/A"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background: #667eea; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; }}
            .stat-box {{ display: inline-block; margin: 10px; padding: 15px; background: #f0f0f0; border-radius: 5px; }}
            .stat-label {{ font-size: 12px; color: #666; }}
            .stat-value {{ font-size: 24px; font-weight: bold; color: #333; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #667eea; color: white; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Monthly Parking Activity Report</h1>
            <p>{month.strftime('%B %Y')}</p>
        </div>
        <div class="content">
            <h2>Hello {user.username},</h2>
            <p>Here's your parking activity summary for {month.strftime('%B %Y')}:</p>
            
            <div style="text-align: center;">
                <div class="stat-box">
                    <div class="stat-label">Total Bookings</div>
                    <div class="stat-value">{total_bookings}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Total Hours</div>
                    <div class="stat-value">{total_hours:.1f}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Total Spent</div>
                    <div class="stat-value">₹{total_spent:.2f}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Most Used Lot</div>
                    <div class="stat-value" style="font-size: 16px;">{most_used_lot}</div>
                </div>
            </div>
            
            <h3>Booking History</h3>
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Parking Lot</th>
                        <th>Spot</th>
                        <th>Duration (hrs)</th>
                        <th>Cost (₹)</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for res in reservations[:10]:
        html += f"""
                    <tr>
                        <td>{res.parking_timestamp.strftime('%d %b %Y')}</td>
                        <td>{res.parking_spot.parking_lot.prime_location_name}</td>
                        <td>{res.parking_spot.spot_number}</td>
                        <td>{res.get_duration_hours():.1f}</td>
                        <td>₹{res.parking_cost or 0:.2f}</td>
                    </tr>
        """
    
    html += """
                </tbody>
            </table>
            <p style="margin-top: 20px; color: #666;">
                Thank you for using our parking management system!
            </p>
        </div>
    </body>
    </html>
    """
    
    return html


def generate_csv_export(reservations):
    """
    Generate CSV export of parking history
    """
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow([
        'Reservation ID', 'Parking Lot', 'Spot Number', 'Vehicle Number',
        'Parked At', 'Left At', 'Duration (hrs)', 'Cost', 'Status'
    ])
    
    for res in reservations:
        writer.writerow([
            res.id,
            res.parking_spot.parking_lot.prime_location_name,
            res.parking_spot.spot_number,
            res.vehicle_number,
            res.parking_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            res.leaving_timestamp.strftime('%Y-%m-%d %H:%M:%S') if res.leaving_timestamp else 'Active',
            f"{res.get_duration_hours():.2f}",
            f"{res.parking_cost or 0:.2f}",
            res.status
        ])
    
    return output.getvalue()


def send_email(to_email, subject, body, html_body=None, attachment=None):
    """
    Send email using MailHog SMTP for local testing
    MailHog runs on localhost:1025 and provides a web UI at localhost:8025
    """
    try:
        # MailHog SMTP Configuration
        SMTP_SERVER = 'localhost'
        SMTP_PORT = 1025
        SENDER_EMAIL = 'parking-system@localhost'
        
        msg = MIMEMultipart('alternative')
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        
        if html_body:
            part1 = MIMEText(body, 'plain')
            part2 = MIMEText(html_body, 'html')
            msg.attach(part1)
            msg.attach(part2)
        else:
            msg.attach(MIMEText(body, 'plain'))
        
        if attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment)
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename=parking_history.csv')
            msg.attach(part)
        
        # Connect to MailHog SMTP (no authentication needed)
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.send_message(msg)
        
        return True
        
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False
def send_email_report(user, html_content, month):
    """
    Send monthly report via email
    """
    subject = f"Your Parking Activity Report - {month.strftime('%B %Y')}"
    plain_text = f"Hello {user.username}, Your monthly parking report is attached."
    
    send_email(user.email, subject, plain_text, html_content)


def send_csv_notification(user, csv_content):
    """
    Send CSV export via email
    """
    subject = "Your Parking History Export"
    body = f"Hello {user.username},\n\nYour parking history export is ready and attached to this email."
    
    send_email(user.email, subject, body, attachment=csv_content.encode())
