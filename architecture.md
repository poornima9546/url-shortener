# URL Shortener Architecture

```text
                         USER
                          |
                          | HTTP :8080
                          v
                 +-------------------+
                 |       NGINX       |
                 |  Reverse Proxy    |
                 +---------+---------+
                           |
                           | HTTP :5000
                           v
                 +-------------------+
                 |   Python Flask    |
                 |   URL Shortener   |
                 |     appuser        |
                 +----+---------+----+
                      |         |
               MySQL  |         |  Redis
                      |         |
                      v         v
              +-----------+  +-----------+
              |   MySQL   |  |   Redis   |
              |    8.0    |  | 7-alpine  |
              +-----+-----+  +-----+-----+
                    |              |
                    v              v
              MySQL Volume    Redis Volume


        All services connected through:

             url-shortener-network
                  (bridge)
Communication Flow
User sends HTTP requests to Nginx on port 8080.
Nginx forwards requests to the Python Flask application.
The application communicates with MySQL using mysql:3306.
The application communicates with Redis using redis:6379.
MySQL stores persistent application data.
Redis provides caching and URL lookup support.
MySQL and Redis are not directly exposed to the host.
All containers communicate through the Docker bridge network.
Containers
Container	Service	Purpose
url-shortener-nginx	Nginx	Reverse proxy
url-shortener-app	Python Flask	Application
url-shortener-mysql	MySQL 8.0	Database
url-shortener-redis	Redis 7 Alpine	Cache
Network
url-shortener-network
        |
        +-- nginx
        +-- app
        +-- mysql
        +-- redis
