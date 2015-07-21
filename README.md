# Python Database Blog Tags Lab

### An adventure in Many-to-Many relationships

## Concept

This lab will expand your blog capabilities even furthur!  After this lab you will be able to tag any specific blog post and see all the posts that you have tagged. This will demonstrate a Many-to-Many relationship, where *one* post can have *many* tags, and *one* tag can have many *posts*.

## Objectives

+ Understand the code that went into creating the Many to Many model
+ Make a corresponding front end that allows users to create tags
+ Show the full list of tags on a page
+ Show a list of all posts, their comments, and tags

## Directions

1. Fill in the tag handler so it gets the Tag Name and adds it to the post entry
2. Fill out the route so that `WSGIApplication` accepts the `/tags` route and passes it to the `TagHandler`
3. Fill out the form in `index.html` so that it passes the tag name to the `/tags` route
4. Pass all of the tags to our `tags.html` page
5. Fill out `tags.html` so that it displays a list of tags
6. Each tag should have a list of posts within it's section.


## Stretch

+ Make the site look better with CSS and more creative HTML
+ Validate tag content and title name
