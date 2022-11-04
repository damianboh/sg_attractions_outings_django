# Singapore Attractions Outings Django Webapp
 
Currently deployed on <a href='https://sg-attractions-outings.up.railway.app/'>https://sg-attractions-outings.up.railway.app/</a> with a PostgreSQL database on railway.app.
 
 ![image](https://user-images.githubusercontent.com/9307190/199877457-8d721bdb-f0b3-4ca8-990f-5ca6bd75a960.png)

## Overview

Django Webapp that allows users to:

- search for attractions in Singapore
- create outings to any attraction
- invite other users for the outings
- access REST API endpoints to pull information and perform tasks (JWT authorization mechanism)

The <a href='https://tih-dev.stb.gov.sg/api-products-documentation'>Singapore Tourism Info Hub API</a> is used to populate attractions data in the internal SQL database.

**Celery**, Celery Beat, and Django signals can be used for sending and scheduling email reminders, updates and invites to users. (Celery can be turned on by setting USE_CELERY to True in settings.py, currently deployment is with Celery turned off.)

**REST API** is implemented with Django REST Framework for users to query for attractions, outings and outing invites.


## 1. Custom Authentication and User Profile

- Under custom\_auth app, **custom UserManager** and **User model** is created to implement the following:
  - Users register with their email address and a password, instead of the default username and password, an additional field of the user's name is also required when registering.
  - Users **log in with email address** instead of the default username.
- Custom **Profile model** is created that has a one to one relationship with the User model. This is to allow additional fields such as 'About' which is a paragraph describing the user.
  - **Django signals** are used to **sync between changes** to User and Profile models, e.g. when Profile instance is updated with a new email, corresponding User instance is also updated etc.


## 2. Pulling Data from Singapore Tourism Info Hub API to Internal Database

- _external\_api/tourism\_hub\_client.py_: **Standalone External Tourism Hub API Client** is included to pull data from Singapore Tourism Hub and map it to a Python object. _Client is a standalone from Django Project_, feel free to use this client in any of your Python projects.
- **Tourism Hub Integration module** (integrated with Django project) uses the above client to populate database subject to certain conditions to implement the features in the next section.


## 3. Searching and Adding Attractions to Favourites

![image](https://user-images.githubusercontent.com/9307190/199877660-d6a72489-b252-4a9a-8bd8-2f0eb609a3e2.png)

- Users can search for an attraction by a search term (e.g. museum, park, zoo etc.)
- After a search happens, the attraction data will be **retrieved from Singapore Tourism Hub** ONLY IF the term **has not been searched in the past 24 hours**.
- The API will return data that consists of details of different attractions. Corresponding Attraction objects will be created in the database, populated by data from the API.
  - **Only a few fields of each database will be populated** after the search to prevent overloading.
  - This fields populated are 'uuid', 'name', 'attraction\_type' and 'summary'. Fields with larger size such as 'full\_description' or fields that require the creation of other objects such as 'tags' will not be populated at this stage.
  - **Only populate these other fields for a full record** of attraction if a user clicks on a particular attraction to **view the attraction in detail**.
- If a user searches for a term that has been searched before (by any user) **in the last 24 hours** , the attraction results are **returned from the internal database** for a smoother experience. External API will not be queried.
- Users can save attractions to favourites.

![image](https://user-images.githubusercontent.com/9307190/199877890-0a4b1d3b-29cf-4d9a-8895-eeb3c8dbe777.png)


## 4. Creating an Outing and Inviting Other Users

- Users can **create an outing** to visit any attraction, specifying the start date and time.
- Once an outing is created, **other users can be invited** by the creator via their emails.
- Users can **confirm their attendance** by choosing whether they are attending or not. They can switch back and forth between these states.
- Only invited users or creator can access the outing detail page, and they can comment on the page.

![image](https://user-images.githubusercontent.com/9307190/199940057-3a094461-43fb-4a77-8e27-49608c00d120.png)

![image](https://user-images.githubusercontent.com/9307190/199940716-c34d4291-5bf2-40aa-ac25-b77b5fc2c3cf.png)

![image](https://user-images.githubusercontent.com/9307190/199943410-78cea10c-5912-44a8-8250-b91412246def.png)

## 5. Email Notifications and Async Processes

- Celery is used when email notifications are sent via an async process.
- Django signal is sent when an invitation is sent by the outing creator, and when a user updates attendance, to implement the following:
  - Users will **receive an invitation email when they're invited** to an outing.
  - Creator of the outing will **receive an update email when invitees change their attendance** status.
- Django Celery Beat is used for task scheduling to implement the following:
  - Half an hour before an outing is starting, all the confirmed attendees, and the creator, are **emailed a reminder notification**.
- To turn on Celery, set USE_CELERY to True in settings.py. Note that with Celery turned off, all email notifications will still be sent, except for reminder emails.

![image](https://user-images.githubusercontent.com/9307190/199947236-99557290-f5f5-4662-83a8-908081ab33f6.png)

![image](https://user-images.githubusercontent.com/9307190/199947510-2776e278-fbac-4bdb-a974-1dbd265ee446.png)

## 6. Models

Models created for this app, as well as a brief description and how they are related among each other are shown below.

- **SearchTerm**
  - standalone object which captures when a term is searched with a method that returns True if it is searched recently
- **Tag**
  - to tag different attractions
- **Attraction**
  - dynamically populated with information from Singapore Tourism Hub API when user searches for attractions
  - '_tags'_ field has Many to Many Relationship with Tag objects
  - '_saved\_by'_ field has Foreign Key Profile (profile of user who saved attraction)
- **Outing**
  - '_attraction'_ field has Foreign Key Attraction (outing is to visit this attraction)
  - '_creator'_ field has Foreign Key Profile (creator/organizer's user profile)
- **OutingInvitation**
  - '_outing'_ field has Foreign Key Outing (user is invited to this outing)
  - '_invitee'_ field has Foreign Key Profile (invitee's user profile)
- **Comment**
  - '_outing'_ field has Foreign Key Outing (comment shows up in detail page of this outing)
  - '_creator'_ field has Foreign Key Profile (user profile of person who commented)
- **User**
  - custom authentication model built on AbstractUser
  - log in is changed to email instead of username
- **Profile**
  - Attribute user has One to One Relationship with User object (profile extends on the User object to include more fields such as 'about')
  - signals are used to sync between changes in profile and user so their names and emails are synced up (using post\_save signals)
  
  ![image](https://user-images.githubusercontent.com/9307190/199954914-47ae167b-c0cb-4dc2-b6e7-e1166af66ebd.png)

## 7. Configurations

- Django Configurations and logging are set up to work as a 12-Factor app.


## 8. REST API is implemented via Django REST Framework

- Users can query for profiles, attractions, attraction tags, outings and outing invites via the **REST API**.
- Users can send invites for outings.
- Users have to be authenticated to use some of the endpoints here.
- Authentication is done through token authentication and with simple-jwt integration.
- A list of endpoints is available on Swagger UI <a href='https://sg-attractions-outings.up.railway.app/api/v1/swagger/'>https://sg-attractions-outings.up.railway.app/api/v1/swagger/</a>.

![image](https://user-images.githubusercontent.com/9307190/199946158-37e89cbb-46ac-4fde-aa39-937f45284ee1.png)

