# Introduction

Welcome to Kayleigh Fichten Studio. For my capstone project I decided to build a website for an artist friend that would allow them to showcase and sell their art directly to their audience. A brief walkthrough of the website can be found here: https://www.youtube.com/watch?v=m-zYY8UMy6Y

In this introduction I will layout the reasons this web application is distinct from and more complex than the other projects in this course. This web application was developed on Wagtail, a content management system built on Django. The main benefit of Wagtail is the built in admin interface which makes it easy for an end user to engage and add their own content to the site dynamically. To best understand the structure of this application, [a basic understanding of Wagtail may be helpful](https://docs.wagtail.io/en/stable/getting_started/the_zen_of_wagtail.html), although it follows Django's file structure conventions. The center of the Wagtail system focuses on the `Page` class, which combines the power of a database model that also acts like a class based view with built in url routing. Each `Page` model renders a template on the front end of the same name as the `__class__.__name__` (converted from camelCase to snake_case.html) and allows the backend user to add object instances of that `Page` class.

Two things that sets this Wagtail application from others:
    - It is not a blog, but takes advantage of a blog style CMS
    - It includes custom e-commerce functionality built into the CMS system

While this web application was designed for one particular artist in mind, it could easily be modified to fit the style and needs of other artists.

The remainder of this readme will focus on the distinct purpose of each Django app within the project. Although I won't explain each file individually, I will point out the most important files, and give a high-level explanation of the structure and the purpose of the web application as a whole. Most apps contain a templates folder which contains a template corresponding to each of that app's `Page` models. Most of the apps do not utilize a `views.py` as the primary functionality in Wagtail can be controlled from the `Page` classes. Additionally, some apps contain static folders for `.js`, `.css`, fonts, and static media, however most of the static files are contained in the primary app - `kf`. The working folder for this project is also named 'kf', and the root directory also contains a folder of images which are used by a django management command.

# APPS

## kf

The primary app for this project. Contains settings (separated into `dev.py` for development when `DEBUG=TRUE`, `production.py`, and `base.py-`). Most of the static files are stored in this app's static folder. `wsgi.py` is stored here, as well as `urls.py` which has been configured for use beyond Wagtail defaults with some custom url handling including:
    - The `allauth` app for handling registration and login pages
    - The `email/` path used by `allauth` is redirected to a 404 page to prevent users from changing their account email
    - Routes from the `Shop` app's `views.py` which are not constructed automatically using `Page` models
    - The `wagtailcache` app included for increased performance

## home

This app contains the model for the web site's landing page, a `HomePage` object. After initializing the app and creating a `HomePage` object and some related child objects, its `parent_page_types` and `subpage_types` were set to empty arrays to keep the intended user from manipulating the top level of the site's structure. The `HomePageImage` class lets the user feature certain `GalleryImages` on the landing page.

## gallery

This is the main focus of the web site, in which the model classes define the majority of the site content.

#### models.py

`InstallationMedium`: Categories of art medium can be added in the Snippets menu in the admin interface, and selected for any particular `InstallationPage`

`DirectSaleType`: Items listed in the shop can display a label as to which type of product is being sold. Labels can be added in the Snippets menu.

`Gallery`: The top level page where content can be added as child objects. A gallery object has been prepared for the intended user, then `parent_page_types` was restricted to keep only one gallery object in the database. The admin user can edit the intro field, or leave it blank. The `get_context` method collects all the child `InstallationPage`s and filters them to a particular `medium` if the frontend user clicks on a filter. Results are paginated to a low value to reduce page load time, and more results are loaded dynamically via the Waypoints javascript package.

`InstallationPage`: Can be added as children of the Gallery in the admin interface. These should contain one or more `GalleryItem`s. By default the main image used for thumbnails in the gallery would be the first image added to its first `GalleryItem`, or one can be selected manually.

`GalleryItem`: Should contain one or more `GalleryImage`. By default the main image used for thumbnails in the shop would be the first image added to it, or one can be selected manually. Shop characteristics are also controlled here. `direct_sale` can be enabled to list it for sale on the web site, or `external_sale` can be enabled to add one or more links to other web sites where products may be sold. This project focuses on Society6 as the branded external website. Although it can contain many images, they should all represent the same object, as they would all be displayed on this item's shop page.

`GalleryImage`: Uses Wagtail's built-in Image class to handle uploading and rendering images.

`ExternalLink`: Links that can be added to a `GalleryItem`'s shop page.


#### custom_panels.py

Allows for a read-only calculated field in the admin panel, used for `GalleryImage.display_caption`.

#### views.py

Contains a view for a report that can be viewed in the admin interface as described in the [Wagtail docs](https://docs.wagtail.io/en/stable/advanced_topics/adding_reports.html).

#### wagtail_hooks.py

This file contains the main logic behind customization of the default Wagtail admin interface, primarily by adding modeladmin links to the sidebar, and modifying the 'Edit', 'Add', and 'Delete', buttons that are displayed by default. It also customizes the columns displayed and filters in each modeladmin page, was well as various other attributes.

#### /templates/modeladmin/

Additional admin interface customization is done by overriding the default Wagtail admin templates.

#### /management/commands/

This file contains utilities for importing and modifying content initial content for testing and for when the end user will migrate to this web application. JSON data and image files were scraped from the intended user's existing web site, which can be added or removed to the database with these commands.

## shop

Although shop inventory is primarily managed in the `gallery` app, additional logic for the shop was factored to a separate app to handle `ShopItem` views, and checkout logic. Custom urls are defined in `urls.py`.

#### models.py

`Shop`: Similar to `Gallery`, a single `Shop` object was prepared for the intended user, and restricted from adding more shop pages. The context is modified to only include `GalleryItems` that are either enabled for `direct_sale` or `external_sale`. The `item_view` route is defined to enable shop items to be loaded at a subpath of `/shop/`.

`ShopItem`: A proxy field of `GalleryItem` used for the `ShopItemAdmin`

`Cart`: A `Page` class to render the cart. Retrieves cart items from their IDs stored in the user session.

`Profile`: A `Page` class to render the user's profile and allows them to manage it.

`Order`: Shop order `Page` used to render completed orders to the frontend and log orders for the admin user.

`UserAddress`: A custom address model which uses the `django-address` package.

#### views.py

This contains the server side e-commerce logic. Users can add or remove shop items to their cart via ajax calls to these. A checkout page is rendered in the traditional Django manner after retrieving a Braintree token to be used for collecting payment. Once a user completes the order form and payment information, the server attempts to complete the order by saving the order to the database, sending the transaction to Braintree, then reducing the stock of the items purchased and clearing the cart. An order confirmation email is sent to the user. This file also contains ajax calls for the user to add or remove shipping addresses to their saved profile.

#### context_processors.py

Checks the user session cart for items no longer in stock to remove them from the cart and notify the user. Also adds the current installation page to the page context if the user is viewing one.

## media and search

Wagtail's built in media storage folder, and search apps.

# JavaScript
`admin_edit.js`: extra JS for the admin interface, to show and hide certain fields based on checkbox values.

`braintree.js`: ajax logic for rendering the Braintree drop-in UI (payment form), and sending the collected information to the server.

`homeSwiper.js`, `installationSwiper.js`, `shopItemSwiper.js`: Swiperjs instances for displaying images in a carousel

`infinite.min.js`, `jquery.waypoints.min.js`: Local copies of Waypoints and its Infinite Scroll Shortcut

`main.js`: enables certain Bootstrap tools, as well as Waypoints. Also contains ajax calls for adding and removing cart items, and removing addresses from the user profile page.

`viewerjs.js`: Enables Viewerjs for click to enlarge images on `InstallationPage`s
