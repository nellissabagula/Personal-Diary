# Personal Diary/Blog System

A simple, secure, and user-friendly web application for maintaining a personal diary or blog.

## Features

- User registration and authentication
- Create, read, update, and delete diary entries
- Tagging system for organizing entries
- Privacy settings for individual entries
- Search functionality
- Responsive design for use on any device

## Requirements

- Python 3.7+
- Flask
- Werkzeug

## Installation

1. Clone or download this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python app.py
   ```
4. Open your browser and go to `http://localhost:5000`

## Usage

1. Register for a new account or log in if you already have one
2. Create new diary entries with titles, content, tags, and privacy settings
3. View, edit, or delete your existing entries
4. Search for entries by content or filter by tags

## File Structure

- `app.py`: Main application file containing routes and business logic
- `data.json`: Local storage file for user accounts and diary entries
- `/templates/`: HTML templates for the web interface
- `/static/`: Static files like CSS stylesheets
- `requirements.txt`: Python dependencies

## Security

- Passwords are securely hashed using Werkzeug's security utilities
- Session-based authentication keeps users logged in during their visit
- Private entries are only accessible to the owner

## Data Storage

The application stores all data in a JSON file (`data.json`) in a structured format:
- Users and their hashed passwords
- Diary entries with metadata (title, content, date, tags, privacy setting)

## Customization

Feel free to customize the application to suit your needs:
- Modify the CSS in `/static/style.css` for styling changes
- Add new features in `app.py`
- Extend the data model as needed

## License

This project is open source and available under the MIT License.