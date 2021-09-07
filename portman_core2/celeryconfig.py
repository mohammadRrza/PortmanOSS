broker_url = 'amqp://'
result_backend = 'redis://'
include = ['portman_core2.tasks']

task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'Asia/Tehran'
enable_utc = True
