"""Dexcom G7 macOS Menubar Application"""

import rumps
import logging
import sys
from datetime import datetime, timedelta
from typing import Optional

from dexcom_menubar.dexcom_api import DexcomShareAPI, DexcomAPIError, DexcomAuthenticationError
from dexcom_menubar.credentials import CredentialManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"{rumps.application_support('DexcomMenubar')}/dexcom_menubar.log")
    ]
)

logger = logging.getLogger(__name__)


class DexcomMenubarApp(rumps.App):
    """Dexcom G7 Menubar Application"""

    def __init__(self):
        super(DexcomMenubarApp, self).__init__(
            "Dexcom",
            title="Loading...",
            quit_button=None
        )

        self.api: Optional[DexcomShareAPI] = None
        self.current_reading = None
        self.recent_readings = []
        self.update_interval = 300  # 5 minutes in seconds
        self.last_notification_time = None  # Track when we last sent a notification
        self.last_notification_condition = None  # Track what condition triggered last notification

        # Menu items
        self.menu = [
            rumps.MenuItem("Current Reading", callback=None),
            rumps.separator,
            rumps.MenuItem("Recent Readings", callback=None),
            rumps.separator,
            rumps.MenuItem("Refresh Now", callback=self.refresh_now),
            rumps.MenuItem("Settings", callback=self.show_settings),
            rumps.separator,
            rumps.MenuItem("Quit", callback=self.quit_app)
        ]

        # Initialize API
        self.initialize_api()

        # Start the update timer
        if self.api:
            self.timer = rumps.Timer(self.update_glucose, self.update_interval)
            self.timer.start()
            # Initial update
            self.update_glucose(None)
        else:
            self.title = "⚠ Not Configured"

    def initialize_api(self) -> bool:
        """Initialize Dexcom API with stored credentials"""
        try:
            username, password, region = CredentialManager.get_credentials()

            if not username or not password:
                logger.warning("No credentials found")
                rumps.alert(
                    title="Dexcom Menubar - Setup Required",
                    message="Please configure your Dexcom Share credentials.",
                    ok="OK"
                )
                self.prompt_for_credentials()
                username, password, region = CredentialManager.get_credentials()

            if username and password:
                self.api = DexcomShareAPI(username, password, region)
                logger.info("Dexcom API initialized")
                return True
            else:
                logger.error("Failed to initialize API: no credentials")
                return False

        except Exception as e:
            logger.error(f"Failed to initialize API: {e}")
            rumps.alert(
                title="Error",
                message=f"Failed to initialize Dexcom API: {str(e)}",
                ok="OK"
            )
            return False

    def update_glucose(self, sender):
        """Update glucose reading from Dexcom Share"""
        if not self.api:
            logger.warning("API not initialized, skipping update")
            return

        try:
            logger.info("Fetching glucose reading...")
            reading = self.api.get_current_glucose()

            if reading:
                self.current_reading = reading
                logger.info(f"Updated glucose: {reading['value']} {reading['trend_arrow']}")

                # Check if we need to send a notification
                self.check_and_notify(reading)

                # Get recent readings for the dropdown
                self.recent_readings = self.api.get_glucose_readings(max_count=12)

                # Update menu first, then update the title
                self.update_recent_readings_menu()
                self.update_menubar_title(reading)
            else:
                logger.warning("No glucose reading available")
                self.title = "⚠ No Data"

        except DexcomAuthenticationError as e:
            logger.error(f"Authentication error: {e}")
            self.title = "⚠ Auth Error"
            rumps.alert(
                title="Authentication Error",
                message="Failed to authenticate with Dexcom Share. Please check your credentials.",
                ok="OK"
            )
        except DexcomAPIError as e:
            logger.error(f"API error: {e}")
            self.title = "⚠ API Error"
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            self.title = "⚠ Error"

    def check_and_notify(self, reading):
        """Check if we should send a notification based on glucose trend"""
        value = reading['value']
        trend = reading['trend']
        trend_arrow = reading['trend_arrow']

        # Determine if we should notify
        should_notify = False
        notification_message = None
        condition_key = None
        alert_title = "⚠️ Glucose Alert"

        # LOW GLUCOSE ALERTS
        # SingleDown (trend 6) below 130
        if trend == 6 and value < 130:
            should_notify = True
            notification_message = f"Glucose falling: {value} mg/dL ⬇"
            condition_key = f"single_down_{value//10}"  # Group by 10s to avoid spam

        # DoubleDown (trend 7) below 160
        elif trend == 7 and value < 160:
            should_notify = True
            notification_message = f"Glucose dropping quickly: {value} mg/dL ⬇⬇"
            condition_key = f"double_down_{value//10}"

        # HIGH GLUCOSE ALERTS
        # FortyFiveUp (trend 3) above 200
        elif trend == 3 and value > 200:
            should_notify = True
            notification_message = f"Glucose rising: {value} mg/dL ↗"
            condition_key = f"forty_five_up_{value//10}"
            alert_title = "📈 High Glucose Alert"

        # Any glucose above 250
        elif value > 250:
            should_notify = True
            notification_message = f"Glucose elevated: {value} mg/dL {trend_arrow}"
            condition_key = f"high_{value//20}"  # Group by 20s to reduce spam
            alert_title = "📈 High Glucose Alert"

        if should_notify:
            # Check if we should actually send the notification
            # Don't send if we sent the same condition in the last 15 minutes
            now = datetime.now()
            should_send = True

            if self.last_notification_time and self.last_notification_condition == condition_key:
                time_since_last = (now - self.last_notification_time).total_seconds() / 60
                if time_since_last < 15:
                    should_send = False
                    logger.info(f"Skipping notification (sent {time_since_last:.1f} min ago)")

            if should_send:
                logger.info(f"Sending notification: {notification_message}")
                rumps.notification(
                    title=alert_title,
                    subtitle=notification_message,
                    message="Check your glucose and consider taking action."
                )
                self.last_notification_time = now
                self.last_notification_condition = condition_key

    def update_menubar_title(self, reading):
        """Update the menubar title with current glucose value and trend"""
        value = reading['value']
        trend_arrow = reading['trend_arrow']
        color_indicator = self.get_glucose_color_indicator(value)

        # Show color indicator, value, and trend arrow in menubar
        self.title = f"{color_indicator} {value} {trend_arrow}"

        # Update the "Current Reading" menu item
        timestamp = reading['timestamp']
        time_ago = self.get_time_ago(timestamp)
        range_name = self.get_glucose_range_name(value)

        self.menu["Current Reading"].title = (
            f"Current: {color_indicator} {value} mg/dL {trend_arrow}\n"
            f"Status: {range_name}\n"
            f"Updated: {time_ago}"
        )

    @staticmethod
    def get_glucose_color_indicator(value: int) -> str:
        """Get color indicator emoji based on glucose value"""
        if value < 70:
            return "🔴"  # Red - Low (hypoglycemia)
        elif value <= 180:
            return "🟢"  # Green - In range
        elif value <= 250:
            return "🟠"  # Orange - High
        else:
            return "🟡"  # Yellow - Very high

    @staticmethod
    def get_glucose_range_name(value: int) -> str:
        """Get descriptive name for glucose range"""
        if value < 70:
            return "Low"
        elif value <= 180:
            return "In Range"
        elif value <= 250:
            return "High"
        else:
            return "Very High"

    def update_recent_readings_menu(self):
        """Update the recent readings submenu"""
        if not self.recent_readings:
            return

        try:
            # Build list of new menu items
            new_items = []

            # Add current reading (will be updated by update_menubar_title)
            new_items.append(rumps.MenuItem("Current Reading", callback=None))
            new_items.append(rumps.separator)

            # Recent readings header
            new_items.append(rumps.MenuItem("Recent Readings", callback=None))
            new_items.append(rumps.separator)

            # Add recent readings
            for reading in self.recent_readings[:12]:
                value = reading['value']
                trend_arrow = reading['trend_arrow']
                timestamp = reading['timestamp']
                time_str = timestamp.strftime('%H:%M')
                time_ago = self.get_time_ago(timestamp)
                color_indicator = self.get_glucose_color_indicator(value)

                title = f"{time_str} - {color_indicator} {value} mg/dL {trend_arrow} ({time_ago})"
                new_items.append(rumps.MenuItem(title, callback=None))

            # Add static items at the end
            new_items.append(rumps.separator)
            new_items.append(rumps.MenuItem("Refresh Now", callback=self.refresh_now))
            new_items.append(rumps.MenuItem("Settings", callback=self.show_settings))
            new_items.append(rumps.separator)
            new_items.append(rumps.MenuItem("Quit", callback=self.quit_app))

            # Clear and rebuild
            self.menu.clear()
            for item in new_items:
                self.menu.add(item)

        except Exception as e:
            logger.error(f"Error updating recent readings menu: {e}", exc_info=True)

    @staticmethod
    def get_time_ago(timestamp) -> str:
        """Get human-readable time ago string"""
        now = datetime.now()
        delta = now - timestamp

        if delta < timedelta(minutes=1):
            return "just now"
        elif delta < timedelta(hours=1):
            minutes = int(delta.total_seconds() / 60)
            return f"{minutes}m ago"
        elif delta < timedelta(days=1):
            hours = int(delta.total_seconds() / 3600)
            return f"{hours}h ago"
        else:
            days = delta.days
            return f"{days}d ago"

    @rumps.clicked("Refresh Now")
    def refresh_now(self, _):
        """Manually refresh glucose reading"""
        logger.info("Manual refresh triggered")
        self.update_glucose(None)
        rumps.notification(
            title="Dexcom Menubar",
            subtitle="Refreshed",
            message=f"Current: {self.current_reading['value']} {self.current_reading['trend_arrow']}" if self.current_reading else "No data available"
        )

    @rumps.clicked("Settings")
    def show_settings(self, _):
        """Show settings dialog"""
        response = rumps.alert(
            title="Dexcom Menubar Settings",
            message="What would you like to do?",
            ok="Update Credentials",
            cancel="Cancel",
            other="Clear Credentials"
        )

        if response == 1:  # OK - Update credentials
            self.prompt_for_credentials()
            self.initialize_api()
            if self.api:
                self.update_glucose(None)
        elif response == 0:  # Other - Clear credentials
            CredentialManager.delete_credentials()
            rumps.alert(
                title="Credentials Cleared",
                message="Dexcom Share credentials have been removed from keychain.",
                ok="OK"
            )

    def prompt_for_credentials(self):
        """Prompt user to enter Dexcom Share credentials"""
        # Show instructions to use terminal-based setup
        response = rumps.alert(
            title="Credential Setup",
            message="Due to macOS limitations, please use the terminal to set up credentials.\n\n"
                    "In your terminal, run:\n"
                    "python -m dexcom_menubar.setup\n\n"
                    "Or use environment variables (.env file).\n\n"
                    "Would you like to see the setup instructions?",
            ok="Show Instructions",
            cancel="Cancel"
        )

        if response == 1:
            import subprocess
            import os
            readme_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "README.md")
            subprocess.run(["open", readme_path])

        logger.info("User directed to terminal-based credential setup")

    @rumps.clicked("Quit")
    def quit_app(self, _):
        """Quit the application"""
        logger.info("Application shutting down")
        rumps.quit_application()


def main():
    """Main entry point"""
    try:
        app = DexcomMenubarApp()
        app.run()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
