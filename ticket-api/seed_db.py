"""
One-time script to create the Tickets table in Azure SQL and seed it with
the sample ticket data that used to live in function_app.py as MOCK_TICKETS.

Usage:
    SQL_CONN_STRING="Driver={ODBC Driver 18 for SQL Server};Server=tcp:<server>.database.windows.net,1433;Database=<db>;Uid=<user>;Pwd=<password>;Encrypt=yes;" python seed_db.py
"""
import os

import pyodbc

MOCK_TICKETS = [
    {"id": "1", "title": "Cannot login to email", "description": "User is unable to access their email account and receives an 'incorrect password' error despite resetting their password twice this week.", "status": "Open", "priority": "High"},
    {"id": "2", "title": "Laptop screen flickering", "description": "The laptop screen flickers intermittently, especially when the device is moved or the lid is adjusted, suggesting a possible display cable issue.", "status": "In Progress", "priority": "Medium"},
    {"id": "3", "title": "Request for keyboard replacement", "description": "Employee has requested a replacement keyboard as several keys have stopped responding after a coffee spill.", "status": "Closed", "priority": "Low"},
    {"id": "4", "title": "Wi-Fi disconnects frequently in conference room B", "description": "Employees report the Wi-Fi connection drops every 10-15 minutes during meetings in Conference Room B, disrupting video calls.", "status": "Open", "priority": "Medium"},
    {"id": "5", "title": "Password reset needed for VPN account", "description": "User is locked out of the VPN after multiple failed login attempts and needs an administrator to reset their credentials.", "status": "Open", "priority": "High"},
    {"id": "6", "title": "New hire laptop setup - Sarah Chen", "description": "IT needs to image and configure a new laptop for incoming employee Sarah Chen, including standard software installs and account provisioning, before her start date.", "status": "In Progress", "priority": "Medium"},
    {"id": "7", "title": "Printer on 3rd floor out of toner", "description": "The shared printer near the 3rd floor break room is displaying a 'low toner' warning and needs a replacement cartridge.", "status": "Open", "priority": "Low"},
    {"id": "8", "title": "Outlook crashes when opening large attachments", "description": "Outlook consistently crashes when the user tries to open PDF attachments larger than 10MB, forcing a restart of the application.", "status": "Open", "priority": "Medium"},
    {"id": "9", "title": "Request for additional monitor", "description": "Employee is requesting a second monitor to improve productivity while working with multiple applications simultaneously.", "status": "In Progress", "priority": "Low"},
    {"id": "10", "title": "VPN connection drops during video calls", "description": "The VPN connection repeatedly disconnects during Teams video calls, causing the user to miss parts of meetings.", "status": "Open", "priority": "High"},
    {"id": "11", "title": "Software license expired for Adobe Photoshop", "description": "The design team's Adobe Photoshop license expired over the weekend, blocking access until renewal was processed.", "status": "Closed", "priority": "Medium"},
    {"id": "12", "title": "Locked out of Salesforce account", "description": "User is unable to log into Salesforce after their account was automatically locked following several incorrect password attempts.", "status": "Open", "priority": "High"},
    {"id": "13", "title": "Laptop won't power on", "description": "Employee's laptop no longer turns on even when connected to a charger; no lights or fan activity observed.", "status": "Open", "priority": "High"},
    {"id": "14", "title": "Request for admin rights to install software", "description": "Developer needs local administrator privileges temporarily to install and test a new IDE plugin.", "status": "In Progress", "priority": "Medium"},
    {"id": "15", "title": "Mouse not connecting via Bluetooth", "description": "Wireless mouse fails to pair with laptop despite multiple attempts; suspect low battery or driver issue.", "status": "Closed", "priority": "Low"},
    {"id": "16", "title": "Shared drive permissions incorrect", "description": "User cannot access the Finance shared drive after a recent reorganization, despite still needing it for reporting.", "status": "Open", "priority": "Medium"},
    {"id": "17", "title": "Email signature update request", "description": "Employee has a new job title and needs their email signature updated to reflect the change.", "status": "Closed", "priority": "Low"},
    {"id": "18", "title": "Zoom audio not working", "description": "During Zoom calls, other participants cannot hear the user despite the microphone showing as active and unmuted.", "status": "Open", "priority": "Medium"},
    {"id": "19", "title": "Laptop fan making loud noise", "description": "The cooling fan on the employee's laptop has become unusually loud, especially under load, suggesting dust buildup or a failing component.", "status": "In Progress", "priority": "Medium"},
    {"id": "20", "title": "Request for external hard drive", "description": "Employee needs an external hard drive to back up large video files that exceed available cloud storage.", "status": "Closed", "priority": "Low"},
    {"id": "21", "title": "Two-factor authentication not receiving codes", "description": "User is not receiving SMS codes for two-factor authentication, preventing them from logging into any company systems.", "status": "Open", "priority": "High"},
    {"id": "22", "title": "SharePoint site access request", "description": "New team member needs access granted to the Marketing SharePoint site to collaborate on campaign documents.", "status": "Open", "priority": "Low"},
    {"id": "23", "title": "Blue screen error on Windows laptop", "description": "Laptop repeatedly crashes with a blue screen error referencing a memory management fault, occurring several times a day.", "status": "Open", "priority": "High"},
    {"id": "24", "title": "Docking station not detecting monitors", "description": "When the laptop is connected to the docking station, external monitors are not detected despite cables being properly connected.", "status": "In Progress", "priority": "Medium"},
    {"id": "25", "title": "Request to join distribution list", "description": "Employee has asked to be added to the 'All-Engineering' distribution list for team announcements.", "status": "Closed", "priority": "Low"},
    {"id": "26", "title": "Slow internet speeds on 2nd floor", "description": "Multiple employees on the 2nd floor report significantly slower internet speeds compared to other floors, especially in the afternoon.", "status": "Open", "priority": "Medium"},
    {"id": "27", "title": "Application crashes on startup on macOS", "description": "The internal reporting application crashes immediately after launch on macOS, though it works fine on Windows machines.", "status": "Open", "priority": "Medium"},
    {"id": "28", "title": "Request for standing desk cable relocation", "description": "Employee has requested facilities coordinate with IT to relocate monitor cabling for a new standing desk setup.", "status": "Closed", "priority": "Low"},
    {"id": "29", "title": "VPN certificate expired", "description": "Employee cannot connect to the VPN because their client certificate expired and needs to be reissued by IT.", "status": "Open", "priority": "High"},
    {"id": "30", "title": "Phishing email reported", "description": "User forwarded a suspicious email requesting login credentials; IT confirmed it was phishing and blocked the sender domain.", "status": "Closed", "priority": "High"},
    {"id": "31", "title": "OneDrive sync stuck at 99%", "description": "OneDrive has been stuck syncing a folder at 99% for several days, and files are not updating across devices.", "status": "In Progress", "priority": "Medium"},
    {"id": "32", "title": "Request for noise-cancelling headset", "description": "Employee working in an open office area has requested a noise-cancelling headset to reduce distractions during calls.", "status": "Closed", "priority": "Low"},
    {"id": "33", "title": "Laptop battery draining quickly", "description": "Laptop battery drops from full charge to under 20% within two hours of light use, indicating possible battery degradation.", "status": "Open", "priority": "Medium"},
    {"id": "34", "title": "Access badge not working at main entrance", "description": "Employee's access badge is no longer recognized at the main entrance turnstile, preventing building entry.", "status": "Open", "priority": "High"},
    {"id": "35", "title": "Request for software installation - Slack", "description": "New employee needs the Slack desktop client installed on their company laptop.", "status": "Closed", "priority": "Low"},
    {"id": "36", "title": "Database connection timeout in reporting tool", "description": "The internal reporting tool intermittently fails with a database connection timeout error, disrupting daily report generation.", "status": "Open", "priority": "High"},
    {"id": "37", "title": "Calendar invites not syncing to phone", "description": "Meeting invites accepted on desktop Outlook are not appearing on the employee's mobile calendar app.", "status": "In Progress", "priority": "Low"},
    {"id": "38", "title": "Request for VPN access for remote contractor", "description": "A newly onboarded contractor needs VPN access provisioned to work remotely on the client project.", "status": "Open", "priority": "Medium"},
    {"id": "39", "title": "Monitor showing no signal", "description": "External monitor displays 'no signal' even though the laptop is powered on and the cable is connected; swapping the cable resolved the issue.", "status": "Closed", "priority": "Medium"},
    {"id": "40", "title": "Spam emails bypassing filter", "description": "User continues to receive a high volume of spam emails despite the spam filter being enabled, some appearing to bypass filtering rules entirely.", "status": "Open", "priority": "Medium"},
    {"id": "41", "title": "Request for laptop upgrade due to performance issues", "description": "Employee's laptop struggles to run current business applications smoothly and is requesting an upgrade to a newer model.", "status": "In Progress", "priority": "Medium"},
    {"id": "42", "title": "Teams call quality poor with echo", "description": "During Teams calls, other participants report hearing an echo of their own voice, likely caused by speaker/microphone feedback.", "status": "Open", "priority": "Medium"},
    {"id": "43", "title": "Request for encrypted USB drive", "description": "Employee handling sensitive client data has requested an IT-approved encrypted USB drive for secure file transport.", "status": "Closed", "priority": "Low"},
    {"id": "44", "title": "Laptop keyboard keys sticking", "description": "Several keys on the employee's laptop keyboard stick or require extra force to register a keystroke.", "status": "Open", "priority": "Low"},
    {"id": "45", "title": "Request to reset MFA device", "description": "Employee lost their phone and needs their multi-factor authentication method reset to regain access to company accounts.", "status": "Open", "priority": "High"},
    {"id": "46", "title": "File share mapped drive disconnected", "description": "The mapped network drive used by the accounting team has been disconnecting randomly throughout the day, requiring frequent reconnections.", "status": "In Progress", "priority": "Medium"},
    {"id": "47", "title": "Request for conference room AV troubleshooting", "description": "The display in the main conference room would not accept input from laptops during a client presentation; IT confirmed it was an HDMI switch failure and replaced the unit.", "status": "Closed", "priority": "Medium"},
    {"id": "48", "title": "Software update failed to install", "description": "A routine Windows update failed partway through installation, leaving the laptop stuck on a restart loop.", "status": "Open", "priority": "Low"},
    {"id": "49", "title": "Request for shared mailbox access", "description": "Employee joining the support team needs access to the shared 'support@company.com' mailbox.", "status": "Closed", "priority": "Low"},
    {"id": "50", "title": "VPN client won't launch", "description": "The VPN client fails to open when clicked, with no error message displayed, preventing remote access to internal systems.", "status": "Open", "priority": "Medium"},
    {"id": "51", "title": "Request for name change on account", "description": "Employee recently got married and has requested their display name and email alias be updated to reflect their new last name.", "status": "Closed", "priority": "Low"},
    {"id": "52", "title": "Laptop overheating during video calls", "description": "Laptop becomes noticeably hot and throttles performance during extended video calls, causing lag and occasional freezing.", "status": "Open", "priority": "Medium"},
    {"id": "53", "title": "Request for firewall rule to allow external API", "description": "Engineering team needs a firewall rule added to allow outbound traffic to a third-party API required for a new integration.", "status": "In Progress", "priority": "High"},
    {"id": "54", "title": "Scanner not detected by computer", "description": "The office scanner is not recognized by the connected computer after a recent software update; reinstalling the driver resolved the issue.", "status": "Closed", "priority": "Low"},
    {"id": "55", "title": "Request for static IP address", "description": "The server room requires a static IP assignment for a new network-attached storage device being installed.", "status": "Open", "priority": "Medium"},
    {"id": "56", "title": "Outlook calendar showing duplicate events", "description": "User's Outlook calendar is displaying duplicate copies of recurring meetings, cluttering their schedule view.", "status": "Open", "priority": "Low"},
    {"id": "57", "title": "Request for offboarding equipment collection", "description": "Departing employee's laptop and access badge need to be collected and deprovisioned as part of the standard offboarding process.", "status": "Closed", "priority": "Medium"},
    {"id": "58", "title": "Wireless headset audio cutting out", "description": "Employee's wireless headset intermittently loses audio for a few seconds during calls, suspected to be a Bluetooth interference issue.", "status": "In Progress", "priority": "Low"},
    {"id": "59", "title": "Request for VDI performance investigation", "description": "Employees using the virtual desktop environment report significant lag and slow application load times throughout the day.", "status": "Open", "priority": "Medium"},
    {"id": "60", "title": "Malware alert on workstation", "description": "Antivirus software flagged a potential malware infection on an employee's workstation and quarantined the affected files pending IT review.", "status": "Open", "priority": "High"},
    {"id": "61", "title": "Request for external monitor for home office", "description": "Remote employee has requested a company-issued external monitor to be shipped to their home office.", "status": "Closed", "priority": "Low"},
    {"id": "62", "title": "Cannot print to network printer", "description": "Print jobs sent to the 4th floor network printer are stuck in the queue and never complete, requiring manual intervention.", "status": "Open", "priority": "Medium"},
    {"id": "63", "title": "Request for software license renewal - AutoCAD", "description": "The engineering team's AutoCAD license is set to expire next week and needs to be renewed to avoid workflow interruption.", "status": "In Progress", "priority": "Medium"},
    {"id": "64", "title": "Laptop trackpad unresponsive", "description": "The built-in trackpad on the employee's laptop has stopped responding to touch input, though an external mouse works fine.", "status": "Open", "priority": "Low"},
    {"id": "65", "title": "Request for guest Wi-Fi access", "description": "Front desk has requested guest Wi-Fi credentials be generated for visiting clients attending a meeting.", "status": "Closed", "priority": "Low"},
    {"id": "66", "title": "VPN slow when accessing shared drives", "description": "Accessing files on the shared network drive over VPN is significantly slower than usual, taking several minutes to open documents.", "status": "Open", "priority": "Medium"},
    {"id": "67", "title": "Request for mobile device enrollment", "description": "New employee's personal phone needs to be enrolled in the company's mobile device management system to access corporate email.", "status": "Closed", "priority": "Low"},
    {"id": "68", "title": "Application freezing when exporting reports", "description": "The finance reporting application freezes whenever a user attempts to export a report to Excel, requiring a force close.", "status": "In Progress", "priority": "Medium"},
    {"id": "69", "title": "Request for new employee email account", "description": "HR has requested a new email account be created ahead of an upcoming employee's start date next Monday.", "status": "Closed", "priority": "Medium"},
    {"id": "70", "title": "Laptop charger not working", "description": "Employee's laptop charger no longer supplies power; the cable appears frayed near the connector.", "status": "Open", "priority": "Medium"},
    {"id": "71", "title": "Request for access to legacy inventory system", "description": "Warehouse employee needs access credentials for the legacy inventory management system to perform stock audits.", "status": "Open", "priority": "Low"},
    {"id": "72", "title": "Webcam not working during video calls", "description": "Employee's built-in webcam displayed a black screen during video calls; updating the camera driver resolved the issue.", "status": "Closed", "priority": "Low"},
    {"id": "73", "title": "Request for VPN split tunneling configuration", "description": "Remote employee is requesting split tunneling be enabled on their VPN connection so local network devices remain accessible.", "status": "In Progress", "priority": "Medium"},
    {"id": "74", "title": "Excel macro throwing runtime error", "description": "A frequently used Excel macro for monthly reporting is throwing a runtime error after a recent Office update.", "status": "Open", "priority": "Medium"},
    {"id": "75", "title": "Request for replacement laptop bag", "description": "Employee's company-issued laptop bag has a broken zipper and they are requesting a replacement.", "status": "Closed", "priority": "Low"},
    {"id": "76", "title": "Cannot access internal wiki", "description": "User receives a 'permission denied' error when trying to access the internal engineering wiki despite having access previously.", "status": "Open", "priority": "Low"},
    {"id": "77", "title": "Request for dual-band Wi-Fi router in remote office", "description": "The small satellite office has requested a new dual-band router be installed to replace the aging single-band unit causing connectivity issues.", "status": "In Progress", "priority": "Medium"},
    {"id": "78", "title": "Laptop screen has dead pixels", "description": "Employee noticed a cluster of dead pixels in the corner of their laptop screen; the display panel was replaced under warranty.", "status": "Closed", "priority": "Low"},
    {"id": "79", "title": "Request for backup restoration of deleted files", "description": "User accidentally deleted an important project folder from the shared drive and is requesting IT restore it from the most recent backup.", "status": "Open", "priority": "High"},
    {"id": "80", "title": "VPN prompting for password repeatedly", "description": "The VPN client repeatedly prompts the user to re-enter their password every few minutes, even after successful authentication.", "status": "Open", "priority": "Medium"},
    {"id": "81", "title": "Request for software installation - Visual Studio Code", "description": "Developer needs Visual Studio Code installed on their new workstation for daily development work.", "status": "Closed", "priority": "Low"},
    {"id": "82", "title": "Slack notifications not appearing on desktop", "description": "Desktop notifications for Slack have stopped appearing despite notification settings being enabled correctly.", "status": "Open", "priority": "Low"},
    {"id": "83", "title": "Request for network drive space increase", "description": "The design team has nearly filled their allocated network drive storage and is requesting additional space to continue working.", "status": "In Progress", "priority": "Medium"},
    {"id": "84", "title": "Laptop randomly restarting", "description": "Employee's laptop restarts unexpectedly several times a day without any error message, disrupting ongoing work.", "status": "Open", "priority": "High"},
    {"id": "85", "title": "Request for temporary loaner laptop", "description": "Employee's laptop is being repaired and they have requested a temporary loaner device to remain productive in the meantime.", "status": "Closed", "priority": "Medium"},
    {"id": "86", "title": "DNS resolution failing for internal sites", "description": "Employees are unable to reach internal company websites by name, though the sites are reachable directly by IP address.", "status": "Open", "priority": "Medium"},
    {"id": "87", "title": "Request for access card reprogramming after role change", "description": "Employee moved to a new department and needs their access card reprogrammed to grant entry to the new floor.", "status": "Closed", "priority": "Low"},
    {"id": "88", "title": "Outlook rules not triggering automatically", "description": "An email rule set up to automatically file newsletters into a folder has stopped working without any recent changes made.", "status": "Open", "priority": "Low"},
    {"id": "89", "title": "Request for dual monitor arm installation", "description": "Employee has requested a monitor arm be installed at their desk to free up space and improve ergonomics.", "status": "In Progress", "priority": "Low"},
    {"id": "90", "title": "Company phone screen cracked", "description": "Employee's company-issued phone has a cracked screen after being dropped and needs to be sent for repair or replacement.", "status": "Closed", "priority": "Medium"},
    {"id": "91", "title": "Request for elevated access to production database", "description": "Senior developer requires temporary elevated access to the production database to investigate a critical customer-reported bug.", "status": "Open", "priority": "High"},
    {"id": "92", "title": "Laptop won't connect to office Wi-Fi", "description": "Laptop successfully connects to other Wi-Fi networks but fails to authenticate on the office network with a generic error.", "status": "Open", "priority": "Medium"},
    {"id": "93", "title": "Request for software uninstall - trial version", "description": "Employee is requesting an expired trial software be uninstalled as it is generating repeated popup reminders.", "status": "Closed", "priority": "Low"},
    {"id": "94", "title": "Backup job failing on file server", "description": "The nightly backup job for the main file server has failed for the past three nights, risking data loss if not resolved.", "status": "Open", "priority": "High"},
    {"id": "95", "title": "Request for keyboard with numeric keypad", "description": "Accounting employee has requested a full-size keyboard with a numeric keypad to speed up data entry.", "status": "Closed", "priority": "Low"},
    {"id": "96", "title": "VPN blocking access to local printer", "description": "When connected to VPN, the employee's laptop can no longer see or print to their local home office printer.", "status": "Open", "priority": "Low"},
    {"id": "97", "title": "Request for SSL certificate renewal on internal portal", "description": "The SSL certificate for the internal employee portal is expiring in three days and needs to be renewed to avoid browser warnings.", "status": "In Progress", "priority": "High"},
    {"id": "98", "title": "Laptop microphone not picking up voice", "description": "The built-in microphone on the employee's laptop was not registering their voice during calls; disabling and re-enabling the audio driver fixed the issue.", "status": "Closed", "priority": "Low"},
    {"id": "99", "title": "Request for guest access to shared calendar", "description": "An external consultant needs temporary guest access to the project team's shared calendar to coordinate meeting times.", "status": "Open", "priority": "Low"},
    {"id": "100", "title": "Server room temperature alert", "description": "The server room's temperature monitoring system triggered an alert indicating the room is running hotter than the safe operating threshold.", "status": "Open", "priority": "High"}
]


def main():
    conn_string = os.environ.get("SQL_CONN_STRING")
    if not conn_string:
        raise SystemExit("SQL_CONN_STRING environment variable is not set")

    conn = pyodbc.connect(conn_string)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Tickets' AND xtype='U')
            CREATE TABLE Tickets (
                Id INT PRIMARY KEY,
                Title NVARCHAR(500) NOT NULL,
                Description NVARCHAR(MAX) NOT NULL,
                Status NVARCHAR(50) NOT NULL,
                Priority NVARCHAR(50) NOT NULL
            )
        """)
        conn.commit()

        for ticket in MOCK_TICKETS:
            cursor.execute(
                """
                MERGE Tickets AS target
                USING (SELECT ? AS Id) AS source
                ON target.Id = source.Id
                WHEN MATCHED THEN
                    UPDATE SET Title = ?, Description = ?, Status = ?, Priority = ?
                WHEN NOT MATCHED THEN
                    INSERT (Id, Title, Description, Status, Priority)
                    VALUES (?, ?, ?, ?, ?);
                """,
                int(ticket["id"]),
                ticket["title"], ticket["description"], ticket["status"], ticket["priority"],
                int(ticket["id"]), ticket["title"], ticket["description"], ticket["status"], ticket["priority"],
            )
        conn.commit()
        print(f"Seeded {len(MOCK_TICKETS)} tickets into the Tickets table.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
