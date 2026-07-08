"""Named domain constants (P-10).

Replaces magic numbers and copy-pasted literal lists that were previously
inlined across the route handlers.
"""

# Task status
VALID_TASK_STATUSES = ["pending", "in_progress", "done", "cancelled"]
# A task in one of these states is never considered overdue.
TERMINAL_STATUSES = ["done", "cancelled"]
DEFAULT_TASK_STATUS = "pending"

# Task priority
MIN_PRIORITY = 1
MAX_PRIORITY = 5
DEFAULT_PRIORITY = 3
HIGH_PRIORITY_THRESHOLD = 2  # priority <= this counts as "high priority"

# Task title
MIN_TITLE_LENGTH = 3
MAX_TITLE_LENGTH = 200

# Users
VALID_USER_ROLES = ["user", "admin", "manager"]
DEFAULT_USER_ROLE = "user"
MIN_PASSWORD_LENGTH = 4

# Categories
DEFAULT_CATEGORY_COLOR = "#000000"

# Reporting
RECENT_ACTIVITY_DAYS = 7

# Validation
EMAIL_REGEX = r"^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$"
