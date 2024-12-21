from infra.cloud_sql.user import find_users
from infra.logger import log_info

if __name__ == "__main__":
    log_info("hello world")
    users = find_users()
    for user in users:
        log_info(f"user: {user.id}, {user.name}, {user.created_at}")
