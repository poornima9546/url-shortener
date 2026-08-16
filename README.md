# URL Shortener

A production-style URL Shortener application built using Python, MySQL, Redis, Docker, Nginx, and GitHub Actions.

## Project Objective

The objective of this project is to design, develop, containerize, test, scan, and deploy a URL Shortener application using Docker and CI/CD practices.

The project demonstrates:

- Python application development
- MySQL database integration
- Redis caching
- Nginx reverse proxy
- Docker Compose
- Docker networking
- Persistent Docker volumes
- Non-root container execution
- Health checks
- Docker Hub image publishing
- Docker image vulnerability scanning
- GitHub Actions CI/CD
- Unit testing and linting

---

## Application Architecture

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
                 |   Application     |
                 |    appuser        |
                 +----+---------+----+
                      |         |
             MySQL    |         |    Redis
                      |         |
                      v         v
              +-----------+  +-----------+
              |   MySQL   |  |   Redis   |
              |    8.0    |  | 7-alpine  |
              +-----------+  +-----------+
                    |              |
                    v              v
               Persistent      Persistent
                 Volume          Volume

All containers communicate through the Docker bridge network:

url-shortener-network

Technology Stack
Component	Technology
Application	Python / Flask
Database	MySQL 8.0
Cache	Redis 7 Alpine
Reverse Proxy	Nginx
Containerization	Docker
Orchestration	Docker Compose
CI/CD	GitHub Actions
Image Scanning	Trivy
Image Registry	Docker Hub
Testing	Pytest
Linting	Flake8
Project Structure
url-shortener/
├── app/
│   ├── app.py
│   └── requirements.txt
│
├── nginx/
│   └── nginx.conf
│
├── tests/
│   └── test_app.py
│
├── .github/
│   └── workflows/
│       └── ci-cd.yml
│
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
Application Features

The application provides:

URL shortening
Short URL generation
Redirect from short URL to original URL
URL statistics
Click counting
Redis caching
MySQL persistence
Nginx reverse proxy

Example:

Original URL:
https://www.google.com


Short URL:
http://localhost:8080/PtdIsx

Opening the short URL redirects the user to the original URL.

Docker Configuration
Docker Compose Services

The application uses four containers:

1. Application
Container: url-shortener-app
Image: url-shortener:v1.0
Port: 5000
User: appuser
2. MySQL
Container: url-shortener-mysql
Image: mysql:8.0
Port: 3306

The MySQL port is not published to the host.

3. Redis
Container: url-shortener-redis
Image: redis:7-alpine
Port: 6379

The Redis port is also not published to the host.

4. Nginx
Container: url-shortener-nginx
Image: nginx:latest
Host Port: 8080
Container Port: 80

Nginx receives requests from the host and forwards them to the Flask application.

Docker Network

All application containers use the following Docker network:

url-shortener-network

Network type:

bridge

The containers communicate using Docker service names instead of hard-coded IP addresses.

Examples:

app:5000
mysql:3306
redis:6379
Docker Networking Verification

The project requires verification that the containers can communicate with each other.

Inspect Docker Network
docker network inspect url-shortener-network

The inspection confirms that the following containers are connected:

url-shortener-app
url-shortener-mysql
url-shortener-redis
url-shortener-nginx
Nginx → Application

The application was tested through Nginx:

docker exec url-shortener-app python -c "import urllib.request; r=urllib.request.urlopen('http://nginx/'); print('Nginx → Application: SUCCESS', r.status)"

Expected result:

Nginx → Application: SUCCESS 200
Application → MySQL
docker exec url-shortener-app python -c "import socket; s=socket.create_connection(('mysql',3306),5); print('Application → MySQL: SUCCESS'); s.close()"

Expected result:

Application → MySQL: SUCCESS
Application → Redis
docker exec url-shortener-app python -c "import socket; s=socket.create_connection(('redis',6379),5); print('Application → Redis: SUCCESS'); s.close()"

Expected result:

Application → Redis: SUCCESS
Database Security

MySQL is not directly exposed to the host.

Verification:

docker inspect url-shortener-mysql --format='Name={{.Name}} | Ports={{json .NetworkSettings.Ports}}'

Expected result:

Name=/url-shortener-mysql | Ports={"3306/tcp":null,"33060/tcp":null}

This confirms that MySQL is available only inside the Docker network.

Redis is also not directly exposed to the host:

docker inspect url-shortener-redis --format='Name={{.Name}} | Ports={{json .NetworkSettings.Ports}}'

Expected result:

Name=/url-shortener-redis | Ports={"6379/tcp":null}
Non-Root Container Execution

The application container runs using a dedicated non-root user.

Verification:

docker inspect url-shortener-app --format='Name={{.Name}} | User={{.Config.User}}'

Expected result:

User=appuser

This improves container security by preventing the application from running as root.

Health Checks

Health checks are configured for the application, MySQL, and Redis containers.

Check container health:

docker compose ps

Expected status:

url-shortener-app      Up (healthy)
url-shortener-mysql    Up (healthy)
url-shortener-redis    Up (healthy)
url-shortener-nginx    Up
Persistent Storage

MySQL uses a persistent Docker volume:

url-shortener_mysql_data

Redis uses:

url-shortener_redis_data

These volumes allow data to persist even when containers are recreated.

Docker Hub

The application image is published to Docker Hub.

Repository:

poornimab03/url-shortener

Published tags:

poornimab03/url-shortener:v1.0
poornimab03/url-shortener:latest
Pull Image From Docker Hub

Another machine can download the image using:

docker pull poornimab03/url-shortener:v1.0

Successful verification:

Status: Downloaded newer image for poornimab03/url-shortener:v1.0
Verify Non-Root User From Pulled Image
docker inspect poornimab03/url-shortener:v1.0 --format='User={{.Config.User}}'

Expected:

User=appuser
CI/CD Pipeline

GitHub Actions is used to automate the application build and deployment process.

The pipeline follows:

Checkout
   |
   v
Install Dependencies
   |
   v
Lint
   |
   v
Unit Tests
   |
   v
Build Docker Image
   |
   v
Scan Docker Image
   |
   v
Login to Docker Hub
   |
   v
Tag Docker Image
   |
   v
Push to Docker Hub

Workflow file:

.github/workflows/ci-cd.yml
CI/CD Stages
1. Checkout

GitHub Actions checks out the repository using:

actions/checkout@v4
2. Python Setup

Python 3.12 is configured using:

actions/setup-python@v5
3. Install Dependencies

The pipeline installs application dependencies and Flake8.

4. Lint

Flake8 checks the application and test code:

flake8 app tests
5. Unit Tests

Pytest runs the application tests:

pytest tests/

Current test result:

2 passed
6. Docker Build

The Docker image is built using:

docker build -t url-shortener:${{ github.sha }} .
7. Security Scan

The Docker image is scanned using Trivy.

The workflow checks for:

CRITICAL
HIGH

severity vulnerabilities.

8. Docker Hub Login

GitHub Actions logs into Docker Hub using GitHub Secrets.

The following secrets are required:

DOCKERHUB_USERNAME
DOCKERHUB_TOKEN
9. Image Tagging

The image is tagged as:

poornimab03/url-shortener:v1.0
poornimab03/url-shortener:latest
10. Push

The images are pushed to Docker Hub:

docker push poornimab03/url-shortener:v1.0
docker push poornimab03/url-shortener:latest
Testing

Unit tests are located in:

tests/test_app.py

Run tests locally:

pytest tests/

Expected result:

2 passed

Run linting:

flake8 app tests

Expected result:

No output

No output from Flake8 means there are no linting errors.

Running the Application

Clone the repository:

git clone https://github.com/poornima9546/url-shortener.git

Enter the project directory:

cd url-shortener

Create the environment file:

cp .env.example .env

Start the application:

docker compose up -d

Check containers:

docker compose ps

Access the application:

http://localhost:8080
Useful Docker Commands

Check running containers:

docker ps

Check Compose services:

docker compose ps

View application logs:

docker logs url-shortener-app

View Nginx logs:

docker logs url-shortener-nginx

Inspect application container:

docker inspect url-shortener-app

Inspect network:

docker network inspect url-shortener-network

Enter application container:

docker exec -it url-shortener-app /bin/sh

Stop the application:

docker compose down

Start again:

docker compose up -d
URL Shortening Verification

Test the home page:

curl -i http://localhost:8080/

Expected:

HTTP/1.1 200 OK

Test a short URL:

curl -i http://localhost:8080/PtdIsx

Expected:

HTTP/1.1 302 FOUND
Location: https://www.google.com

Test URL statistics:

curl http://localhost:8080/stats/PtdIsx

The statistics page displays:

Original URL
Short URL
Creation time
Click count
Screenshots

The following screenshots should be included as project evidence.

Screenshot 1 — Application Running

Show:

docker compose ps

The screenshot should show all four containers running and healthy.

Screenshot 2 — Docker Network

Show:

docker network inspect url-shortener-network

The screenshot should show all four containers connected to the network.

Screenshot 3 — Nginx → Application

Show the successful command:

docker exec url-shortener-app python -c "import urllib.request; r=urllib.request.urlopen('http://nginx/'); print('Nginx → Application: SUCCESS', r.status)"

Expected:

Nginx → Application: SUCCESS 200
Screenshot 4 — Application → MySQL

Show:

docker exec url-shortener-app python -c "import socket; s=socket.create_connection(('mysql',3306),5); print('Application → MySQL: SUCCESS'); s.close()"
Screenshot 5 — Application → Redis

Show:

docker exec url-shortener-app python -c "import socket; s=socket.create_connection(('redis',6379),5); print('Application → Redis: SUCCESS'); s.close()"
Screenshot 6 — Database Not Exposed

Show:

docker inspect url-shortener-mysql --format='Name={{.Name}} | Ports={{json .NetworkSettings.Ports}}'

The result should show:

3306/tcp:null
Screenshot 7 — Non-Root User

Show:

docker inspect url-shortener-app --format='Name={{.Name}} | User={{.Config.User}}'

Expected:

User=appuser
Screenshot 8 — Docker Hub Image

Show Docker Hub repository containing:

v1.0
latest
Screenshot 9 — Docker Pull

Show:

docker pull poornimab03/url-shortener:v1.0
Screenshot 10 — GitHub Actions

Show the successful GitHub Actions workflow with a green check mark.

The workflow should demonstrate:

Checkout
Lint
Unit Test
Build
Scan
Docker Hub Login
Tag
Push
Security Features

The project implements several security practices:

Application runs as non-root user
Database is not exposed to host
Redis is not exposed to host
Docker image is scanned for vulnerabilities
Secrets are stored in GitHub Actions Secrets
MySQL and Redis use health checks
Services communicate using an isolated Docker network
Project Deliverables

The project includes:

 GitHub repository
 Python URL Shortener application
 Dockerfile
 Docker Compose configuration
 .env.example
 MySQL database
 Redis cache
 Nginx reverse proxy
 Docker networking
 Health checks
 Non-root container execution
 Docker Hub repository
 v1.0 image
 latest image
 GitHub Actions workflow
 Linting
 Unit tests
 Docker image build
 Vulnerability scanning
 Docker Hub push
 Architecture diagram
 Screenshots
 README documentation
Final Verification

The project successfully demonstrates:

Nginx
   |
   +----> Application       SUCCESS
              |
              +----> MySQL  SUCCESS
              |
              +----> Redis  SUCCESS

The application image is available on Docker Hub as:

poornimab03/url-shortener:v1.0
poornimab03/url-shortener:latest

The CI/CD pipeline automatically performs:

Checkout
   ↓
Lint
   ↓
Unit Test
   ↓
Build Docker Image
   ↓
Scan Image
   ↓
Push Docker Hub
Author

Poornima B

Cloud & DevOps Project
