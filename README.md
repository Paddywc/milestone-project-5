[![Build Status](https://travis-ci.org/Paddywc/milestone-project-5.svg?branch=master)](https://travis-ci.org/Paddywc/milestone-project-5)

# UnicornAttractor 

## Overview
![Screenshot](https://i.snag.gy/WwAMkN.jpg)

### What it the website for? 
Assisting users in attracting unicorns

### What does it do?
Emits a sound wave that attracts unicorns*.  It also features a store with items that can assist in attracting unicorns. However, the core of the website is the User Suggestions app. Users can submit suggestions for new features and bug fixes. They can also comment on, and upvote, other users’ feature suggestions. Admins have a separate page for each suggestion, where they can set the suggestion’s priority level, assigned admin, estimated completion date, and more.  The User Suggestions app also features voting cycles. Whichever feature suggestion has the most votes at the end of the voting cycle is declared the winner.  The website also has its own currency: Coins. Users can spend coins on submitting, upvoting, and promoting feature suggestions. They can also earn coins for free, e.g. by referring a new user to the website.  
*Sound wave is fictitious. So are unicorns (probably). 

### How does it work? 
The website is built using a Django framework. It has four apps: [Accounts](https://github.com/Paddywc/milestone-project-5/tree/master/accounts), [Market](https://github.com/Paddywc/milestone-project-5/tree/master/market), [User Suggestions](https://github.com/Paddywc/milestone-project-5/tree/master/usersuggestions), and [Unicorn App](https://github.com/Paddywc/milestone-project-5/tree/master/unicornapp). Data are saved as objects, and are accessible and editable via a Django admin page. Django handles authentication, including password resets.  Voting cycles are determined by the estimated completion date of the previous voting cycle’s winner. When that date hits, a new winner is declared and a new voting cycle begins.  This logic, along with most of the website, is written in Python3. The cart and current user’s coins are both saved as context processors. This allows them to be used across templates, including the base template which all other templates inherit from. Whether or not coins are enabled is determined by a Boolean value in the [project settings.py file](https://github.com/Paddywc/milestone-project-5/blob/master/UnicornAttractor/settings.py).  Python if/else statements determine how the project functions depending on this setting.  

## UX

### Ease of Use
The goal of the UX was to make submitting suggestions (and otherwise engaging in the user suggestions process) simple for non-technical users.  The GitHub issue tracker for example, is very robust, but is designed for users with significant technical expertise. However, initial user stories suggested that having a bare-bone suggestion form, e.g. a standard textbox, could also be problematic for non-technical users. For these users, it would be easier to submit a screenshot than to try to describe their issue using only text.  Therefore, it was decided that [CK Editor](https://github.com/django-ckeditor/django-ckeditor) would be used instead of a textbox. CK Editor allows actions such as uploading images, while still being easy to use. The CK Editor toolbar was customised to only have basic features which almost all computer users would be familiar with.  As the default setting for uploading images in CKEditor is quite complex, CK Editor’s [Easy Image](https://ckeditor.com/cke4/addon/easyimage) plugin was also added.
As users are more likely to forget their username than their email, a custom user class was created in Django so that users sign in using their email, rather than their username. 
Another focus of the UX design was making navigating and sorting through suggestions easy. For this, a sorting option was added in the form of a dropdown button menu (so that they fit on all devices).  It uses four easy-to-understand sorting options: Newest, Oldest, Most Commented, and Most Popular.  User stories also brought up the potential issue of repeat suggestions. This is especially true for bug fixes, where a user could post a bug that has already been posted if they don’t quickly see this other post. To combat this, a search box was added to the suggestions homepage, allowing users to filter suggestions by specific words. This enables users to quickly and easily check if others have posted a similar bug. Users were also given the option to flag suggestions as duplicates

### Driving Users to Engage With User Suggestions
The website needed to be focused on getting users to engage in the user suggestions process, as this is the core of its business model. Therefore, information about user suggestions features heavily on the website’s [homepage](https://paddywc-unicornattractor.herokuapp.com/).  For users who aren’t logged in, the homepage sub-header provides information about user suggestions.  These users and logged in users both see information about user suggestions at the page footer. The rest of the page content takes up less than 100 viewport width (the exact amount is device-dependent), so this information is always visible to the user. This means that regular users are reminded of it every time they visit the website to emit the unicorn-attracting sound wave.
A main reason for adding coins was to encourage users to engage with paid features without initially spending any money, with the aim that this will make them more likely to buy coins once they run out. Users are given coins upon signup. They are also rewarded coins for referring additional users to the site.  Furthermore, they have their coins refunded if their feature suggestion wins, along with some extra coins depending on how many votes it got. This should encourage more users to post feature suggestions.
One issue raised by user stories was that users could suggest a feature that may be very demanding to implement. Users without sufficient technical knowledge might upvote a feature, not knowing that it could take months to implement, when in reality they would prefer that time is spent on developing several smaller features.  To counteract this, the admin’s estimated time to complete a suggestion is displayed on the public page for each suggestion. 
Another potential issue that was raised in user stories was the advantage in posting your suggestion early. If one suggestion has enough votes that its victory seems inevitable, it discourages other users from either upvoting or submitting other suggestions. This is why voting cycles were implemented. At the start of each voting cycle, all suggestions are equal. Users are given the option of delaying their submission, having it automatically posted when the new voting cycle begins. 
  
## Features

### Existing Features
-	A User Suggestions section where users can suggest, upvote, and comment on bug fixes and feature suggestions 
-	A voting cycle that when triggered on a specified date, automatically counts votes, determines a winner, edits backend values, posts new data, and sets a new end date
-	A store with cart functionality and Stripe integration
-	An internal currency that users can earn for free or purchase from the store
-	A page for visualizing up-to-date suggestions data
-	Ability to flag suggestions and comments and an admin page for dealing with these. The admin page automatically saves the admin who resolved the flag
-	Admins can navigate to a specific comment that was flagged
-	A userpage for each user that displays their past submissions, votes, and purchase history
-	Users can be redirected to buy more coins if they don’t have enough to make a feature suggestion. The minimum number of coins needed to make the purchase is suggested to the user. The user’s current form values are saved in the session cache and restored after the purchase is complete
-	A rich-text editor with custom, simplified features for posting comments and suggestions
-	Users can pay to promote a feature suggestion, making it appear at the top of the suggestions page. The end date for this promotion is automatically determined and displayed to the user once they have set a start date and number of days for their promotion
-	A suggestion’s admin page displays the full URL for the GitHub tree assigned to that suggestion.  This automatically updates when an admin changes the ‘GitHub Tree’ field.

### Features Left to Implement
-	Whatever the users determine! 

## Project Apps
Unit tests are designed to work on the full Unicorn Attractor project. Some of the unit tests for individual apps require models from other apps to work. Furthermore, all apps require a COINS_ENABLED Boolean value saved in your project settings.  Aside from that, the apps are stand-alone, except for where specified below.  

### Accounts 
Accounts deals with user accounts. This includes creating accounts, authenticating logins, and resetting passwords. 
-	**Required data from other apps **  
    *	If COINS_ENABLED is set to false, then the Accounts app is completely stand alone. However, you will need to clear the references to other apps from your imports.  If it is set as true, coins are added to a user’s account when they sign up. They can also get extra coins for referring users.

### Market
Market includes the store, cart, and coins functionality. 
-	**Required data from other apps **  
    *	Many of the models, for example Usercoins, require a user object to connect to via a foreign key.  By default, this is imported from the models file in an accounts app
    *	Connecting a UserCoinsHistory object to a Suggestion object via a foreign key is optional. However, if you don’t intend to import the UserSuggestions app, you should clear the Suggestions object from your imports 

### User Suggestions
User Suggestions includes functionality to post suggestions, comment on these suggestions, flag items, and manage the voting cycle for feature suggestions 
-	**Required data from other apps **  
    *	If COINS_ENABLED is set to false, the app does not require any data from the Market app. However, you will need to clear these references from your imports. 
    *	Most models require a user object to connect to via a foreign key.  By default, this is imported from the models file in an accounts app

### Unicorn App
Unicorn App brings together elements from the other three apps. It hosts the homepage and the userpages
-	**Required data from other apps **  
    *	The app is heavily reliant on data from all three other apps

## Tech Used

### Some of the tech used includes:
-	**Django**  
    *	The website is a Django project made up of four Django apps
    *	For handling user accounts and authentication
    *	To unit test functions
    *	For modelling data
    *	To render HTML templates and include Python programming within these templates. This includes inserting python variables into JavaScript scripts 
    *	To trigger functions on GET or POST requests
    *	For binding functions to URLs 
-	**Python3**
    *	All apps are predominantly written using Python, the language of Django 
    *	To create a Procfile to deploy the app on Heroku 
    *	The website apps use imported Python libraries, including [datetime](https://docs.python.org/3/library/datetime.html) and [random](https://docs.python.org/2/library/random.html)
-	**HTML** , **CSS** and **SCSS**
    *	To structure and style the web app content
    *	CSS was written in SCSS and compiled into [styles.css](https://s3.eu-west-1.amazonaws.com/paddywc-unicornattractor/static/css/styles.css?response-content-disposition=inline&X-Amz-Security-Token=FQoGZXIvYXdzEAMaDGB%2BmeF5%2BW4JJ8eKqyK4A1tUfepKKwfpz5qkAsEp6robGW53W8ptFqjgGeJ994r%2FK90HIJ%2FKFeGb7JI32iqJN4teqDs8mYS7puEjJgrClqXE%2FmMHfH6Wk%2FtcOuuIb%2BUrDcVKc416Ktl7a3xYlQ3EWhsJWwiSTHRZaEGtYMBnPuV2fZWwuRqyCh06zX7Goz26KyPofJTgQ2Mx7Fq1w7tq1cSGjGHVGnpyVmwnbVH5dDKX1uTNiKOLa%2F%2BRfNLJ%2FOY%2FFlpbz78fb1JfbAeSzNeIHPTjGFs9vpCvDEEdt9vJ58RFbgVmXebmkNnTYo0d3zliV0LlGMJCiPhF284lsvS0OCmFU862aqYWG8mrDvKNEz6PxhL88cIcK4fC%2BdLokqZCk1WtAiwo7YYT1ty27B3lrAt0%2Fdrslln%2BLbmQ9nlLEQN1A36Ylfx6r8B%2BDYpjhkkuKMaU4KqmG5Knd%2BEMT5G8ri%2FzRGCpO9qz8b%2FYyi%2F72iVCcuF%2B9GxcXv%2FfflDJ9mz1SEyElxdRcYP8sW7UQTP9XNaRwgi0UOEGDO%2By02aFLc2e%2FoY%2Fql%2F5%2FE17t5QHtOPL4o2Gah2dWDHm0Uw%2FU5Galos5irc12UCcKMeR8dsF&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20180821T171700Z&X-Amz-SignedHeaders=host&X-Amz-Expires=300&X-Amz-Credential=ASIAXRZSFNY4ASDWIMOG%2F20180821%2Feu-west-1%2Fs3%2Faws4_request&X-Amz-Signature=d9e386afe773c7829d213ace51fbcedcf944585c3d76cf9b23d651548343daac)
[**SQLite**](https://www.sqlite.org/index.html)
    *	Used as the application database
[**Bootstrap**](http://getbootstrap.com/)
    *	Used in conjunction with HTML and CSS to develop the website style
    *	For implementing the responsive, grid-based website layout
    *	Bootstrap components used includes cards, tables, and the navbar 
-	[**Matplotlib**](https://matplotlib.org/)
    *	For creating the charts on the [view data page](https://paddywc-unicornattractor.herokuapp.com/suggestions/view_data)
-	**JavaScript** and  [**jQuery**](https://jquery.com/)
    *	JQuery used to hide or show particular buttons based on a user’s form values
    *	For filtering suggestions using the searchbox 
    *	To calculate and display additional data to the user depending on their current form values
    *	For navigating to specific tabs on the suggestions homepage 
- [**Django Countries**](https://github.com/SmileyChris/django-countries)
    *	For providing country choices on the delivery address form 
- [**CKEditor**](https://ckeditor.com/)
    *	[CKEditor for Django](https://github.com/django-ckeditor/django-ckeditor) is the rich-text editor used when posting suggestions and comments
    *	[Easy Image](https://ckeditor.com/cke4/addon/easyimage) plugin used to simplify the process of uploading images to the rich-text editor
-	[**Stripe**](https://stripe.com)
    *	For processing credit card payments  
    *	Stripe JavaScript file manages payment modal and verifying payments, ensuring that sensitive information is never posted on the app’s forms
- [**Amazon S3**](https://aws.amazon.com/s3/)
    *	For storing and reading static files. This includes CSS, JavaScript, Django admin, and CKEditor files
    *	For storing and reading media files, such as store item images
- [**Travis CI**](https://travis-ci.org/)
    *	For continuous testing. Build tests are seen at the displayed of this readme
- [**Heroku**](https://paddywc-recipe-wiki.herokuapp.com/)
    *	The live version of the web app is hosted on [Heroku](https://paddywc-unicornattractor.herokuapp.com/)
    *	For saving configuration variables that should remain hidden from GitHub. This includes secret keys for Amazon AWS and Stripe

## Contributing 

### Getting the project running locally
1.	Clone or download this GitHub repository using the ‘Clone or Download’ button found on [the main GitHub repository page](https://github.com/Paddywc/milestone-project-5). Alternatively, initialize git and pull the GitHub repository as a remote
2.	If you wish, you can download just the individual [Accounts](https://github.com/Paddywc/milestone-project-5/tree/master/accounts),  [User Suggestions](https://github.com/Paddywc/milestone-project-5/tree/master/usersuggestions), or [Market](https://github.com/Paddywc/milestone-project-5/tree/master/market) apps for use in your project.  Aside from the dependencies on other apps listed in the [Project Apps section of this readme](https://github.com/Paddywc/milestone-project-5#project-apps), you also need to import many of the configurations found in this project’s [settings.py file](https://github.com/Paddywc/milestone-project-5/blob/master/UnicornAttractor/settings.py). The exact configuration depends on which combination of apps you intend to import
3.  Open the project directory using an integrated development environment (IDE) software application, such as Eclipse or Visual Code Studio
4.	Ensure you have Python3 and Django installed on your computer (or online IDE). Install it if you do not. How you should do this depends on which operating system you are using.  See the [Python Documentation](https://docs.python.org/3.4/using/index.html) for instructions on installing Python3, and the [Django documentation](https://docs.djangoproject.com/en/2.1/intro/install/) for installing Django.  The versions of Django and Python currently used in this project are found in the [requirements file](https://github.com/Paddywc/milestone-project-5/blob/master/requirements.txt)
5.	Install any other dependencies listed in the [requirements file](https://github.com/Paddywc/milestone-project-5/blob/master/requirements.txt) that are not already installed. It is recommended that you use your IDE to automate this
6.	Some features require variables that are hidden from the GitHub repository. To use these features, you will need to set these as environmental values. The simplest way to do this is to create an env.py file (that name is listed in the [project .gitignore file](https://github.com/Paddywc/milestone-project-5/blob/master/.gitignore), and will therefore remain hidden from git). Import os into that file. Then, set the values by entering ``` os.environ.setdefault("<key>", "<value>”) ```.  These values will then be imported where needed in the settings.py file. The values that you may need to set are: 
- SECRET_KEY
    *	The project secret key
- AWS_SECRET_ACCESS_KEY and AWS_ACCESS_KEY_ID
    *	Required to post to the S3 bucket
    *	These are unique to the S3 bucket used on this project. If you wish to post data to S3 (e.g. new product images or JavaScript files), then you will need to use your own S3 bucket
    *	You will still be able to read all S3 files without these keys. By clicking the following links, you can also download the project [SCSS](https://s3-eu-west-1.amazonaws.com/paddywc-unicornattractor/static/css/styles.scss), [CSS](https://s3-eu-west-1.amazonaws.com/paddywc-unicornattractor/static/css/styles.css) and [JavaScript](https://s3-eu-west-1.amazonaws.com/paddywc-unicornattractor/static/js/unicornattractor.js) files. This will allow you to edit them as you see fit
- EMAIL_ADDRESS and EMAIL_PASSWORD
    *	A valid Gmail email address and password 
    *	Required for sending password reset and referral emails. The emails will be sent from this account
- STRIPE_PUBLISHABLE and STRIPE_SECRET
    *	Publishable and secret Stripe keys 
    *	Required for Stripe functionality  
    *	Available when you create a Stripe account 
 -  CLOUDSERVICES_TOKENURL
    *	For saving images uploaded using CKEditor  
    *	If you wish to save these images, you will also need to change the cloudServices_uploadUrl in the settings.py file so that it links to your account   
    *	CKEditor Cloud Services is only required for the Easy Images plugin. If you remove this plugin, you will not need these values

7.	Add your computer/IDE as an allowed host in the [settings.py file](https://github.com/Paddywc/milestone-project-5/blob/master/UnicornAttractor/settings.py)
8.	You are good to go! Remember to set DEBUG=True when working on the project.  You can run the project by entering ``` python3 ~/workspace/manage.py runserver $<IP>:$<PORT>"  ``` in your terminal

## Testing
Unit tests are found in the tests directory of each app.  Each tests file uses its own mock database, and do not relate to the project database in any way (except for using the same Django models). Because of this, they are appropriate unit tests regardless of what database you are using. They are, however, designed to test individual functions with relation to their functionality for the entire UnicornAttractor website. Therefore, some tests rely on models imported from different apps (e.g. testing User Suggestions relies on the User model from the Accounts app). 
To run these unit tests, enter the following into the project terminal:
``` python3 manage.py test ```

## Deployment

The app is hosted on [Heroku](https://paddywc-unicornattractor.herokuapp.com/). The code uses the default GitHub (master branch)[https://github.com/Paddywc/milestone-project-5/tree/master]. The code found on GitHub is the same code used on the live Heroku app. Changes made to the master branch on GitHub are automatically pushed to Heroku.  The only data used in Heroku not visible on GitHub are the secret config variables detailed in the [contributing section of this readme](https://github.com/Paddywc/milestone-project-5#contributing), and the static and media files hosted on S3

## Credits

### Code
- The sources for all non-original code are displayed in comments above the relevant code
- [PyCharm](https://www.jetbrains.com/pycharm/download/) software was used for separating out the python code into separate files. Therefore, much of the code for importing functions from python files within the project directory was generated using PyCharm
- The code for registering the custom user class in the [Accounts Admin.py file](https://github.com/Paddywc/milestone-project-5/blob/master/accounts/admin.py) is from the (Django documentation)[https://docs.djangoproject.com/en/dev/topics/auth/customizing/#auth-custom-user]
- The custom user class in [accounts/models.py](https://github.com/Paddywc/milestone-project-5/blob/master/accounts/models.py)  is based on code from [FOMFUS](https://www.fomfus.com/articles/how-to-use-email-as-username-for-django-authentication-removing-the-username). The basic structure of this code is followed, with minor customisations to suit the needs of the project 
- Two lines of code in the [login_user() function](https://github.com/Paddywc/milestone-project-5/blob/master/accounts/views.py) are from [The Net Ninja](https://www.youtube.com/watch?v=XMgF3JwKzgs&list=PL4cUxeGkcC9ib4HsrXEYpQnTOTZE1x0uc&index=22). They are identified in the function docstring
- The [cart.py code](https://github.com/Paddywc/milestone-project-5/blob/master/market/cart.py) is largely taken from [muva](https://muva.co.ke/blog/developing-shopping-cart-class-shop-products-django-2-0-python-3-6/).  The cart.add and cart.remove functions are significantly edited as the original code did not function correctly. Other changes from the source are mostly simple name changes to match the variables of the project.  Completely original code is identified by comments
- Code for [processing Stripe payments](https://github.com/Paddywc/milestone-project-5/blob/master/market/checkout.py) is from the [Stripe documentation](https://stripe.com/docs/charges) 
- The [StoreItem class](https://github.com/Paddywc/milestone-project-5/blob/master/market/models.py)  is taken from the Code Institute e-commerce project. The delivery_required, is_coins and coins_amount fields are original code
- Code in the [Delivery class](https://github.com/Paddywc/milestone-project-5/blob/master/market/models.py) for automatically setting other current_delivery_method values to false when one’s value is set to true is taken from [Adam on stackoverflow](https://stackoverflow.com/questions/1455126/unique-booleanfield-value-in-django) and edited to reflect the project variables. Added is the condition of only changing the current_delivery_method values of that user. This code is also used in the [SuggestionAdminPage class](https://github.com/Paddywc/milestone-project-5/blob/master/usersuggestions/models)
- The code that fixes the bug where tests crash because unit tests can’t use the messages middleware is from [Tarsis Azevedo on stackoverflow](https://stackoverflow.com/questions/11938164/why-dont-my-django-unittests-know-that-messagemiddleware-is-installed). It is used throughout the various tests files and identified in the comments
- The code that enables unit testing session attributes is from [Mark L on stackoverflow.com)[https://stackoverflow.com/questions/16865947/django-httprequest-object-has-no-attribute-session]. It is used throughout the testing files and identified in the comments
- The code in the [base.html](https://github.com/Paddywc/milestone-project-5/blob/master/templates /base.html) template for displaying Django messages as a bootstrap alert is from [simpleisbetterthancomplex](https://simpleisbetterthancomplex.com/tips/2016/09/06/django-tip-14-messages-framework.html). The foundations of the [password_reset_done template](https://github.com/Paddywc/milestone-project-5/blob/master/templates/registration/password_reset_done.html) are also from [simpleisbetterthancomplex](https://simpleisbetterthancomplex.com/tutorial/2016/09/19/how-to-create-password-reset-view.html)
- The code in the [project settings](https://github.com/Paddywc/milestone-project-5/blob/master/unicornattractor/settings/py) for using AWS is from the Code Institute e-commerce project
- The [project settings](https://github.com/Paddywc/milestone-project-5/blob/master/unicornattractor/settings/py) code that enables testing for Matplotlib functions in Travis is from [Sylhare on stackoverflow](https://stackoverflow.com/questions/37604289/tkinter-tclerror-no-display-name-and-no-display-environment-variable)
- The code in [usersuggestions/data_visualization.py](https://github.com/Paddywc/milestone-project-5/blob/master/usersuggestions/data_visualization.py) for specifying minor and major tick mark intervals is from the [Matplotlib website](https://matplotlib.org/gallery/ticks_and_spines/major_minor_demo.html#sphx-glr-gallery-ticks-and-spines-major-minor-demo-py)
- The code in [usersuggestions/data_visualization.py](https://github.com/Paddywc/milestone-project-5/blob/master/usersuggestions/data_visualization.py) for saving plots to S3 is taken from [Aidan Feldman on stackoverflow](https://stackoverflow.com/questions/31485660/python-uploading-a-plot-from-memory-to-s3-using-matplotlib-and-boto). The code is adjusted to fit projects structure and data
- The [SuggestionAdminPageForm initialization code](https://github.com/Paddywc/milestone-project-5/blob/master/usersuggestions/forms.py) that only allows admin users to be assigned to a suggestion is from [neil.millikin  on stackoverflow](https://stackoverflow.com/questions/291945/how-do-i-filter-foreignkey-choices-in-a-django-modelform)
- The line of code used throughout the tests files that force logs in a user is from (WeizhongTu on stackoverflow)[https://stackoverflow.com/questions/2619102/djangos-self-client-login-does-not-work-in-unit-tests]

### Additional Credits
- The sound wave gif seen by logged in users on the [home page](https://paddywc-unicornattractor.herokuapp.com/) is taken from [tenor](https://tenor.com/view/sound-wave-wave-sound-gif-3535566) 
- The JPG used to represent coins in the store is from [futuristicraft](https://futuristicraft.com/product/coin-booster/)
- All icons used on the site are from [Material Design](https://material.io/tools/icons/?style=baseline) 
- The unicorn image used in the background of the [home page](https://paddywc-unicornattractor.herokuapp.com/) header is taken from [stickpng](http://www.stickpng.com/img/comics-and-fantasy/unicorns/unicorn-grace)
