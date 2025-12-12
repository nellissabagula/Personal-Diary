"""
Personal Diary/Blog System
Main Application File
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a more secure key in production
DATA_FILE = 'data.json'


class DiaryEntry:
    def __init__(self, title, content, date=None, tags=None):
        self.id = None
        self.title = title
        self.content = content
        self.date = date or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.tags = tags or []
        self.is_private = False
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'date': self.date,
            'tags': self.tags,
            'is_private': self.is_private
        }


class UserManager:
    def __init__(self):
        self.data_file = DATA_FILE
        self.load_data()
    
    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {'users': {}, 'entries': []}
    
    def save_data(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=4)
    
    def create_user(self, username, password):
        if username in self.data['users']:
            return False
        
        hashed_pw = generate_password_hash(password)
        self.data['users'][username] = {
            'password': hashed_pw,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.save_data()
        return True
    
    def authenticate_user(self, username, password):
        if username in self.data['users']:
            stored_password = self.data['users'][username]['password']
            return check_password_hash(stored_password, password)
        return False
    
    def add_entry(self, entry):
        if not self.data['entries']:
            entry.id = 1
        else:
            max_id = max([e['id'] for e in self.data['entries']])
            entry.id = max_id + 1
        
        entry_dict = entry.to_dict()
        self.data['entries'].append(entry_dict)
        self.save_data()
        return entry.id
    
    def get_entries(self, user=None, limit=None, tag_filter=None):
        entries = self.data['entries']
        
        if tag_filter:
            entries = [e for e in entries if tag_filter.lower() in [tag.lower() for tag in e['tags']]]
        
        entries.sort(key=lambda x: x['date'], reverse=True)
        
        if limit:
            entries = entries[:limit]
        
        return entries
    
    def get_entry_by_id(self, entry_id):
        for entry in self.data['entries']:
            if entry['id'] == entry_id:
                return entry
        return None
    
    def update_entry(self, entry_id, title, content, tags, is_private):
        for i, entry in enumerate(self.data['entries']):
            if entry['id'] == entry_id:
                self.data['entries'][i]['title'] = title
                self.data['entries'][i]['content'] = content
                self.data['entries'][i]['tags'] = tags
                self.data['entries'][i]['is_private'] = is_private
                self.save_data()
                return True
        return False
    
    def delete_entry(self, entry_id):
        for i, entry in enumerate(self.data['entries']):
            if entry['id'] == entry_id:
                del self.data['entries'][i]
                self.save_data()
                return True
        return False


# Initialize user manager
um = UserManager()


@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Get all entries or apply filters
    tag_filter = request.args.get('tag', '')
    entries = um.get_entries(tag_filter=tag_filter)
    
    return render_template('index.html', entries=entries, username=session['username'])


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if um.authenticate_user(username, password):
            session['username'] = username
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials')
    
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if len(password) < 6:
            flash('Password must be at least 6 characters')
        elif um.create_user(username, password):
            flash('Registration successful')
            return redirect(url_for('login'))
        else:
            flash('Username already exists')
    
    return render_template('register.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/entry/new', methods=['GET', 'POST'])
def new_entry():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        tags_input = request.form.get('tags', '')
        tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
        is_private = 'is_private' in request.form
        
        entry = DiaryEntry(title=title, content=content, tags=tags)
        entry.is_private = is_private
        entry_id = um.add_entry(entry)
        
        return redirect(url_for('view_entry', entry_id=entry_id))
    
    return render_template('create_entry.html')


@app.route('/entry/<int:entry_id>')
def view_entry(entry_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    entry = um.get_entry_by_id(entry_id)
    if not entry:
        flash('Entry not found')
        return redirect(url_for('index'))
    
    return render_template('view_entry.html', entry=entry)


@app.route('/entry/<int:entry_id>/edit', methods=['GET', 'POST'])
def edit_entry(entry_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    entry = um.get_entry_by_id(entry_id)
    if not entry:
        flash('Entry not found')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        tags_input = request.form.get('tags', '')
        tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
        is_private = 'is_private' in request.form
        
        success = um.update_entry(entry_id, title, content, tags, is_private)
        if success:
            flash('Entry updated successfully')
            return redirect(url_for('view_entry', entry_id=entry_id))
        else:
            flash('Failed to update entry')
    
    return render_template('edit_entry.html', entry=entry)


@app.route('/entry/<int:entry_id>/delete', methods=['POST'])
def delete_entry(entry_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    success = um.delete_entry(entry_id)
    if success:
        flash('Entry deleted successfully')
    else:
        flash('Failed to delete entry')
    
    return redirect(url_for('index'))


@app.route('/search')
def search():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    query = request.args.get('q', '').lower()
    entries = um.get_entries()
    
    filtered_entries = []
    for entry in entries:
        if query in entry['title'].lower() or query in entry['content'].lower():
            filtered_entries.append(entry)
    
    return render_template('search_results.html', entries=filtered_entries, query=query)


if __name__ == '__main__':
    app.run(debug=True)