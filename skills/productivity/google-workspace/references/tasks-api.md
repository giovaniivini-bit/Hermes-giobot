# Google Tasks API Quick Reference

## Service Build
```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
creds = Credentials.from_authorized_user_file('/path/to/google_token.json')
service = build('tasks', 'v1', credentials=creds)
```

## Common Operations

### List task lists
```python
lists = service.tasklists().list().execute()
# Returns: [{id, title, updated}]
```

### Create task
```python
task = {'title': 'My Task', 'notes': 'Details', 'due': '2026-06-16T05:00:00Z'}
result = service.tasks().insert(tasklist='@default', body=task).execute()
```

### List tasks from default list
```python
tasks = service.tasks().list(tasklist='@default').execute()
```

### Mark complete
```python
service.tasks().patch(tasklist='@default', task=TASK_ID, body={'status': 'completed'}).execute()
```

### Update task
```python
service.tasks().patch(tasklist='@default', task=TASK_ID, body={'title': 'New Title'}).execute()
```

### Delete task
```python
service.tasks().delete(tasklist='@default', task=TASK_ID).execute()
```

## Due Date Format
ISO 8601 with timezone: `2026-06-16T05:00:00Z`

## Pitfalls
- Use `tasklist='@default'` for the user's default task list
- Tasks API must be enabled in Google Cloud Console (separate from OAuth scopes)
- `HttpError 403: accessNotConfigured` → user must enable at:
  https://console.developers.google.com/apis/api/tasks.googleapis.com/overview