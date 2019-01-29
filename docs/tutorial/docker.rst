Docker Container
--------------------

Running a flask app in a docker container is a comfortable way to avoid dependency installation.

Build Container
^^^^^^^^^^^^^^^

Change into flask-unchained source folder. Then run docker build command:

.. code:: bash

   docker build -t briancappello/flask-unchained .

The container will be built and tagged with the name briancappello/flask-unchained.

Run Container
^^^^^^^^^^^^^

Change into your project folder created with 'flask new project PROJECT'.
Then run a container mounting your project's folder:

.. code:: bash

   docker run -d --name PROJECT -p 5000:5000 -v "$(pwd)":/flask/src briancappello/flask-unchained

Your app runs now on localhost:5000.

Build Custom Container
^^^^^^^^^^^^^^^^^^^^^^

If you want dockerize your project you can create a Dockerfile in your project's folder.

.. code:: docker

   # Dockerfile

   FROM briancappello/flask-unchained
   COPY . .
   RUN pip install -r requirements-dev.txt && pip install -r requirements.txt

Then you can build and run your custom container as described above.

.. code:: bash

   docker build -t PROJECT .
   docker run -d --name PROJECT -p 5000:5000 -v "$(pwd)":/flask/src PROJECT

Docker Compose
^^^^^^^^^^^^^^

Docker Compose is a tool to configure containers, mountpoints and ports.
A simple compose file for an flask-unchained project is following:

.. code:: yaml

   # docker-compose.yml

   version: '3'
    services:
        postgres:
            image: postgres:9.6.5
        
        redis:
            image: redis:3.2-alpine
            command: redis-server
            expose:
            - 6379

        app:
            build:
                context: .
                dockerfile: Dockerfile
            links:
            - postgres
            - redis
            environment:
            - FLASK_DATABASE_HOST=postgres
            - FLASK_REDIS_HOST=redis
            command: flask run --host 0.0.0.0 --port 5000
            ports:
            - 5000:5000
            volumes:
            - .:/flask/src

This file in project's folder and a simple command 'docker-compose up' starts
the app.
In this example next to the app container, one for postgres database and one for redis are started too.
They are available through their hostnames postgres and redis within the app container.