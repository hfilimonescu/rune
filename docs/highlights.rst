Highlights
==========


**Rune** is the result of implementing various Flask projects with 
their own requirements and challenges.

Rune Apps
---------

The concept of Rune Apps is nothing new or groundbreaking. They just 
facilitate implementing the project-specific logic quicker and cleaner.

As a consequence, Rune makes use of Flasks **blueprints** and extends 
them as Rune apps. This decision came naturally, since the declared purpose 
of blueprints is exactly this. *I am aware, that blueprints are not apps, 
but at the moment I started the project this was the best name I could 
come up with.*

A naive classification of these apps would be **core** and **pluggable** apps.

By design all Rune Apps are packages that can be installed via ``pip``.

Core Rune Apps
^^^^^^^^^^^^^^

All these apps are contained and distributed as the **Rune** package.

- Rune-Auth (for Authentication and fine-grained Authorization)
- Rune-Admin (a central place to accomodate all admin tasks for the app)
- Rune-Basis (a place to manage the resources of the apps)
- Rune-Error (a central error handler)
- Rune-Main (a catch-all app for system messages and an about page)
- Rune-Theme (built on Flask-Menu and Flask-BS4 to have a uniform and complete UI)

Pluggable Rune Apps
^^^^^^^^^^^^^^^^^^^

These are the heart and mind of your customer's project. Here you can do all you
whish and get creative.

To run them you just need to add them to the ``RUNE_APPS`` key in the config file
and reload the app.

These Apps can be created and registered to rune as simple Flask blueprints.

A cookiecutter template can be found at https://github.com/hfilimonescu/rune-template.

Documentation will follow shortly.


Important Embedded Functionality
--------------------------------

- Fine-Grained and Flexible Authorization

    A user's access can be defined at route level.

    This concept uses three key elements: *users*, *roles*, and *permissions*.

    **Permissions** define what actions a user can perform, or what routes are 
    accessible to them.

    **Roles** bundle multiple permissions so that administrators don't need to
    assign each permission to every user.

    Roles also provide a means to revise the permissions of many users without
    the need of searching and updating users.

    The **flexibility** comes from the nature of roles and permissions. 
    Permissions are defined by the developer in the source code and cannot be 
    influenced by the administrators or users.
    Roles are defined by the administrators and can depict any structure the 
    project/client requires.

- Translations (Flask-Babel + Babel)
    
    Translations work very well in Flask and I never thought about them until I
    started packaging my first pluggable app. Because of the default overlap in 
    Babel domains your translations do not work as expected.

    Well Rune learned how it's done and the cookiecutter template sets it up.

- Distributed Task Queue (Celery)
    
    Rune supports celery task queues.
    
    Additionally the cookiecutter tempalte has an example ready to work.


- Versioning for SQLAlchemy (SQLAlchemy-Continuum)

    Sometimes your client wants to see the changes made in a datbase table from 
    within the app. That means logs are not an option.

- Simple, Consistent, Adaptable, and Functional (Flask-Menu + Flask-BS4 + Rune-Theme)

    The UI of Rune is built on top of *three* extensions that make it easy to maintain.

    It is **simple** because you define the menu entries when you define the routes.
    
    It is **consistent** because the theme has the template for building the menu 
    already set up.
    
    It is **adaptable** because you can modifiy the appearance of the menu entry points
    when when defining or when rendering them.
    
    It is **functional** because you only see the menu entries you are authorized to see.
