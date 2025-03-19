import json
import os
from datetime import datetime
import pytz
import streamlit as st

from src.components.google_drive import save_files

class ActivityLogger:
    def __init__(self): 
        self.config = st.session_state.config
        if self.config.logging_enabled:
            os.makedirs(self.config.get_logging_handlers()['file']['path'], exist_ok=True)

    def save_activity(self, user_id: str, activity_data: dict):
        if not self.config.logging_enabled:
            return
        
        os.makedirs('./', exist_ok=True)
        if "user_timestamp" not in activity_data:
            user_timestamp = datetime.now(pytz.timezone(self.config.logging_format['timezone']))
            user_timestamp = user_timestamp.strftime(self.config.logging_format['timestamp_format'])

            activity_data = {
                    **activity_data,
                    "user_timestamp": user_timestamp
                }
        if self.config.file_handler['enabled']:
            filename = self.config.get_filename_template(
                user_id=user_id,
                timestamp=activity_data['user_timestamp']
            )

        with open(filename, 'w') as file:
            json.dump(activity_data, file, default=str, indent=self.config.file_handler['indent'])

        if self.config.google_drive_enabled:
                save_files(user_id, filename)