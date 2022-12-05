# Travelsite Django Project

The project was created as Django project to 
show off skills. It uses some code from one of 
the free HTML, CSS, and JS templates. The entire website is loosely oriented around travel. 


## Setup

1. Rename `.env.sample` to `.env` and replace the values.
2. Run in your terminal `docker-compose up`.
3. Run `docker ps` and get the ID of "travelsite-web" container.
4. Run `docker exec -it <container ID> bash`
5. Now in bash run `python manage.py load_fixtures` 
to load sample data.
6. Now everything should be set up and the website ready
to use on  `http://localhost:8000/`

### Additional information
Additional information about docker can bo found on
`https://docs.docker.com/get-started/`

