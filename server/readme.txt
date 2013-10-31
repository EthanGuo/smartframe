sudo apt-get install libssl-dev python-dev libevent-dev
sudo apt-get install python-pip
sudo pip install -r requirements.txt --use-mirrors
sudo apt-get install mongodb
sudo apt-get install memcached
sudo apt-get install redis-server

Start web server,
One way to start server, 
MONGODB_URI=mongodb://localhost:27017 REDIS_URI=redis://localhost:6379 MEMCACHED_URI=localhost:11211 WEB_PORT=8080 python app.py

The other way,
MONGODB_URI=mongodb://localhost:27017 REDIS_URI=redis://localhost:6379/0 MEMCACHED_URI=localhost:11211 gunicorn -k "geventwebsocket.gunicorn.workers.GeventWebSocketWorker" --workers=2 --bind=localhost:8080 app:app --daemon --pid /tmp/smart-web.pid

Start worker server,
One node server,
REDIS_URI=redis://localhost:6379/0 celery worker --app=smartserver.worker:worker

Cocurrent pool server,
REDIS_URI=redis://localhost:6379/0 celery worker --app=smartserver.v2.worker:worker -P gevent -c 1000

Multi nodes server(4 in this example),
REDIS_URI=redis://localhost:6379/0 celery multi start 4 --app=smartserver.worker:worker -P gevent -l info -c:1-4 1000

Start scheduled tasks,
REDIS_URI=redis://localhost:6379/0 celery beat --app=smartserver.worker:worker --pid=/tmp/periodic_task.pid --detach

Start daemon,
python sessionWatcher