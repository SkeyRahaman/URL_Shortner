# URL Shortener

[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688.svg)](https://fastapi.tiangolo.com/)
[![MySQL](https://img.shields.io/badge/Database-MySQL%2FSQLite-orange.svg)](https://www.mysql.com/)
[![Docker](https://img.shields.io/badge/Deployment-Docker-blue.svg)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/Orchestration-Kubernetes-326CE5.svg)](https://kubernetes.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

## 📝 Project Description

This is a basic URL shortener application designed to provide shortened URLs for longer web addresses. It features a robust backend built with FastAPI, offering essential functionalities like user authentication and login using JSON Web Tokens (JWT). The application is designed to be database-agnostic, leveraging SQLAlchemy as its ORM, which allows seamless integration with various databases, including MySQL (for production) and SQLite (ideal for testing). It provides a comprehensive set of API endpoints to shorten, edit, retrieve details, and manage URLs, all secured with token-based authentication. The project also includes a comprehensive test suite written with Pytest to ensure reliability and correctness.

## 📸 Screenshots

1. Swagger Docs
    ![alt text](<screenshots/swager.png>)
2. ReDocs
    ![alt text](<screenshots/redoc.png>)

## ⚙️ Installation Guide

You can set up and run this application using various methods:

### a. Direct Installation on Your System

1.  **Prerequisites:** Ensure you have Python 3.8+ installed on your system.
2.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/SkeyRahaman/URL_Shortner](https://github.com/SkeyRahaman/URL_Shortner)
    cd URL_Shortner
    ```
3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Environment Variables:** Create a `.env` file in the root directory of the project and add the following environment variables. Adjust values as per your setup.

    ```dotenv
    URL_PREFIX=/api/v2

    # Database Configuration (for MySQL)
    MYSQL_ROOT_PASSWORD=secret_root
    DATABASE_PROTOCOL=mysql+pymysql
    DATABASE_USER=admin
    DATABASE_PASSWORD=secret
    DATABASE_HOSTNAME=database
    DATABASE_PORT=3306
    DATABASE_NAME=url_shortner

    # For SQLite (uncomment and use this for testing, comment out MySQL settings)
    # DATABASE_PROTOCOL=sqlite:///./sql_app.db
    # DATABASE_USER=
    # DATABASE_PASSWORD=
    # DATABASE_HOSTNAME=
    # DATABASE_PORT=
    # DATABASE_NAME=
    ```
    * **Note for SQLite:** To use SQLite for testing, change `DATABASE_PROTOCOL` to `sqlite:///./sql_app.db` and leave other `DATABASE_` variables empty.
5.  **Run the Application:**
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    ```
    The application will be accessible at `http://localhost:8000`.

### b. Docker Compose

1.  **Prerequisites:** Ensure Docker and Docker Compose are installed on your system.
2.  **Edit Environment File:** Copy `sample.env` to `.env` and edit the variables as per your requirements.
3.  **Spin Up Services:**
    ```bash
    docker-compose up --build -d
    ```
    This will build the Docker images and spin up the application and database services. The application will typically be available at `http://localhost:8000`.

### c. Kubernetes Deployment

1.  **Prerequisites:** Ensure you have `kubectl` installed and a Kubernetes cluster (e.g., Minikube, Docker Desktop Kubernetes) configured.
2.  **Navigate to Kubernetes Folder:**
    ```bash
    cd Kubernetes
    ```
    (Ensure this `Kubernetes` directory contains the following files: `api-deployment.yaml`, `api-service.yaml`, `configMap.yaml`, `database-deployment.yaml`, `database-service.yaml`, `pvc.yaml`, `pv.yaml`, `secrets.yaml`)
3.  **Apply Kubernetes Manifests:**
    ```bash
    kubectl apply -f ./
    ```
4.  **Get Service URL (for Minikube):**
    If you are using Minikube, you can get the service URL using:
    ```bash
    minikube service api-service
    ```

## 🚀 Tech Stack

* **Database:** MySQL, SQLite (or any other database compatible with SQLAlchemy)
* **Backend:** FastAPI, SQLAlchemy (ORM), JWT (for authentication), Python
* **Testing:** Pytest
* **CI/CD & Orchestration:** Docker, Kubernetes

## ✅ Tests

This project includes a suite of unit and integration tests written using `pytest`. To run the tests:

1.  Ensure you have followed the "Direct Installation on Your System" steps.
2.  Install the test dependencies:
    ```bash
    pip install -r requirements.txt
    pip install -r requirements_test.txt
    ```
3.  Navigate to the root directory of the project.
4.  Run the tests using the `pytest` command:
    ```bash
    pytest
    ```
    This will discover and run all tests in the project.

## 📚 API Endpoints

| Method | Endpoint | Description |
| :----- | :---------------------------------------- | :------------------------------------ |
| `POST` | `/api/v2/auth/token` | Get JWT access token |
| `POST` | `/api/v2/users` | Create a new user account |
| `GET` | `/api/v2/users/me` | Get current authenticated user |
| `PUT` | `/api/v2/users/me` | Update current authenticated user |
| `DELETE` | `/api/v2/users/me` | Delete current authenticated user |
| `POST` | `/api/v2/urls/create_short_url` | Create a short URL |
| `GET` | `/api/v2/urls/{short_url}` | Redirect to original URL |
| `PUT` | `/api/v2/urls/{short_url}` | Update short URL |
| `DELETE` | `/api/v2/urls/{short_url}` | Delete short URL |
| `GET` | `/api/v2/urls/{short_url}/details` | Get short URL details |
| `GET` | `/api/v2/urls/` | List all short URLs by the user |
| `GET` | `/api/v2/health` | Health check |

## 🤝 Contributing Guidelines

We welcome contributions to this project! If you'd like to contribute, please follow these steps:

1.  **Fork** the repository.
2.  **Create a new branch** for your feature or bug fix: `git checkout -b feature/your-feature-name` or `bugfix/issue-description`.
3.  **Make your changes** and ensure your code adheres to the project's coding standards.
4.  **Write clear, concise commit messages.**
5.  **Push your branch** to your forked repository.
6.  **Open a Pull Request** to the `main` branch of this repository, describing your changes in detail.

For more detailed contributing guidelines, please refer to the `CONTRIBUTING.md` file (if available in the repository).

## 📞 Contact / Support

If you have any questions, suggestions, or encounter issues, feel free to reach out:

* **GitHub Profile:** [SkeyRahaman](https://github.com/SkeyRahaman/URL_Shortner)
* **Email:** [sakibmondal7@gmail.com](mailto:sakibmondal7@gmail.com)

Please feel free to open an issue on the [GitHub Issues page](https://github.com/SkeyRahaman/URL_Shortner/issues) for any bugs or feature requests.

You can also find more about my work on my portfolio: [http://sakibmondal7.pythonanywhere.com/](http://sakibmondal7.pythonanywhere.com/)