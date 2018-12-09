import secret  # Create this file locally.


def get_redis_config():
    return {
        'host': '142.93.160.67',
        'password': secret.REDIS_PASSWORD,
        'port': 6379,
    }


def get_db_config():
    return {
        'host': 'pythonweekend.cikhbyfn2gm8.eu-west-1.rds.amazonaws.com',
        'database': 'pythonweekend',
        'user': 'shareduser',
        'password': secret.DB_PASSWORD,
    }
