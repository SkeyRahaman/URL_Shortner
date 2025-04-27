
# URL Shortner

A simple FastAPI application to shorten URLs.

## Table of Contents

- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
  - [Running the Application](#running-the-application)
  - [Authentication](#authentication)
  - [User Endpoints](#user-endpoints)
  - [URL Endpoints](#url-endpoints)
- [License](#license)

## Getting Started

This section will guide you on how to get the URL Shortner application running on your local machine.

### Prerequisites

- Python 3.8+

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/your-repository.git
   ```

2. Navigate to the project directory:

   ```bash
   cd your-repository
   ```

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the Application

To run the application, use the following command:

```bash
uvicorn app.main:app --reload
```

> _Assuming your main application file is named `main.py` and your FastAPI application instance is named `app`._

### Authentication

**POST** `/auth/token`  
_Description_: Get an authentication token.  
> You’ll need to provide login credentials (e.g., username and password) in the request body. The response will include a JWT token for authenticated access.

### User Endpoints

**POST** `/user/new_user`  
_Description_: Create a new user.  
_Expected Body_:  
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

**POST** `/user/update_user`  
_Description_: Update an existing user.  
_Expected Body_:  
```json
{
  "username": "your_username",
  "new_data": {
    "email": "new_email@example.com"
  }
}
```

### URL Endpoints

**POST** `/url/create_short_url`  
_Description_: Create a new short URL.  
_Expected Body_:  
```json
{
  "original_url": "https://example.com"
}
```

**GET** `/url/get_url_object/{short_url}`  
_Description_: Retrieve the details of a shortened URL object using its short URL identifier.

**GET** `/url/{short_url}`  
_Description_: Redirect to the original URL associated with the provided short URL.
