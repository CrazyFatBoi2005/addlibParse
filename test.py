from flask import Flask, jsonify
from celery import Celery

app = Flask(__name__)

# Настройка Celery
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'  # URL Redis сервера
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'  # URL Redis сервера

# Создание экземпляра Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)


# Простая задача Celery
@celery.task
def add(x, y):
    return x + y


@app.route('/')
def home():
    result = add.delay(4, 6)  # Вызов задачи Celery
    return jsonify({'message': 'Task submitted', 'task_id': result.id})


if __name__ == '__main__':
    app.run()