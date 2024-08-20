# Opensource Dashboard Backend

Welcome to Opensource Dashboard, a.k.a. [Donut Dashboard](https://donutdashboard.netlify.app/), where devs receive virtually sweet rewards for contributions to opensource projects. 

Built with Django utilizing PostgreSQL, the backend manages data interactions and API services for [the frontend](https://github.com/Open-Source-Dashboard/osd-frontend).


### Authors
- [Tammy Do](https://github.com/tammytdo)
- [Andrea Riley(Thiel)](https://github.com/ariley215)
- [Lana Zumbrunn](https://github.com/lana-z) 

## Links and Resources

- For more details on the project's features, acknowledgments, how to contribute and more, refer to the [Opensource Dashboard frontend](https://github.com/Open-Source-Dashboard/osd-frontend) repository's README. 
- Deployed site: [donutdashboard.netlify.app](https://donutdashboard.netlify.app/)

- Deployed server: [osd-backend-td.vercel.app](https://osd-backend-td.vercel.app/)

## Setup
Set up the backend environment with these steps:

1. Clone the repository
2. Navigate to the project directory
3. Create and activate a virtual environment 

```
python3 -m venv .venv
source .venv/bin/activate   # Linux/Mac
source .venv/Scripts/activate   # Windows
```

4. Install dependencies:
```
pip install -r requirements.txt
```

5. Initialize and run the application
```
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

## Acknowledgments
See the [frontend](https://github.com/Open-Source-Dashboard/osd-frontend) README for a comprehensive list of tools and acknowledgments.

## Contributing
Contributions are encouraged. Refer to the [frontend](https://github.com/Open-Source-Dashboard/osd-frontend) README for guidelines on contributing to the project.
