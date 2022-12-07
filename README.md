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

## Features
+ **Accounts** app containing all user-related functionalities
such as: 
  + Registration, 
  + Logging in,
  + Resetting passwords,
  + Managing a user profile,
  + Subscribing to the newsletter.

+ **Chats** app - right now used only for chatting with
support. In the near future will be extended and used
in the forum app to manage contact between users.

+ **Ecommerce** app is the biggest part of this project 
and contains functionalities such as:
  + Browsing products:
    - Main page - randomly chosen categories and all products on sale,
    - Products by category.
  + Filters that can be applied while browsing.
  + Search functionalities based on elastic search and **Search** app
  + Cart functionalities (adding to cart, removing a single product or all of them)
  + Order history
+ **Search** app. At the moment used only to set up API and
elastic search but in the near future will be used also in the **Forum** app.

+ **Forum** app is being developed.
+ **Blog** app will be developed after the **Forum** app.

### Additional information
Additional information about docker can bo found on
`https://docs.docker.com/get-started/`

