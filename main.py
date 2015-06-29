#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# Make sure to run app like so:
# dev_appserver.py --datastore_consistency_policy=consistent [path_to_app_name]
# in order to see changes reflected in the redirect immediately

# To clear the datastore:
# /usr/local/google_appengine/dev_appserver.py --clear_datastore=1 [path_to_app_name]

import os
import webapp2
import jinja2
from google.appengine.ext import ndb


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

# Define a Post model for the Datastore
class Post(ndb.Model):
    name = ndb.StringProperty(required=True)
    content = ndb.TextProperty(required=True)
    date = ndb.DateTimeProperty(auto_now_add=True)
    comments = ndb.KeyProperty(kind='Comment', repeated=True)

class Comment(ndb.Model):
    name = ndb.StringProperty(required=True)
    comment = ndb.TextProperty(required=True)
    date = ndb.DateTimeProperty(auto_now_add=True)

class MainHandler(webapp2.RequestHandler):
    def get(self):
        # Get all of the student data from the datastore
        query = Post.query()
        post_data = query.fetch()
        # Pass the data to the template
        template_values = {
            'posts' : post_data
        }
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

    def post(self):
        # Get the student name and university from the form
        name = self.request.get('name')
        content = self.request.get('content')
        # Create a new Student and put it in the datastore
        post = Post(name=name, content=content)
        post.put()
        # Redirect to the main handler that will render the template
        self.redirect('/')

class CommentHandler(webapp2.RequestHandler):
    def post(self):
        # Create the comment in the Database
        name = self.request.get('name')
        comment = self.request.get('comment')
        db_comment = Comment(
            name=name,
            comment=comment
        )
        comment_key = db_comment.put()

        # Find the post that was commented on using the hidden post_url_key
        post_url_key = self.request.get('post_url_key')
        post_key = ndb.Key(urlsafe=post_url_key)
        post = post_key.get()

        # Attach the comment to that post
        post.comments.append(comment_key)
        post.put()

        self.redirect('/')



app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/comment', CommentHandler)
], debug=True)
