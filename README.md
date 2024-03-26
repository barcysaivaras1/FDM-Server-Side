# FDM Expenses Application Server
ECS506-Group3 FDM Expenses Server

## Getting Started

### Installation

Clone the repository, then install the dependencies by running the following command:

```
$ pip install -r requirements.txt
```

### Usage

Enter your PostgreSQL database URI in a .env file in the following format:

```env
DATABASE_URI=postgresql+psycopg://user:password@host:port/database_name
```

Also, enter a mail username and password in the .env file in the following format:

```env
MAIL_USERNAME=YOUR_EMAIL_ADDRESS
MAIL_PASSWORD=YOUR_EMAIL_PASSWORD
```

Run the following to start the application:

```
$ flask run
```

Use the ```--debug``` flag for debugging mode.