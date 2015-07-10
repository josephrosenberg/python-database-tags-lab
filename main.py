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
    title = ndb.StringProperty(required=True)
    content = ndb.TextProperty(required=True)
    date = ndb.DateTimeProperty(auto_now_add=True)
    comment_keys = ndb.KeyProperty(kind='Comment', repeated=True)

    def get_tags(self):
        """Gets all tags associated with this post."""
        post_tags = PostTag.query(PostTag.post_key == self.key).fetch()
        tag_keys = [post_tag.tag_key for post_tag in post_tags]
        return ndb.get_multi(tag_keys)

    def add_tag(self, tag_name):
        """Adds a tag to this post."""
        tag = Tag.get_or_create(tag_name)
        post_tag = PostTag.query(PostTag.tag_key == tag.key,
                                 PostTag.post_key == self.key
                                ).get()
        # Only link the two if that hasn't happened already
        if not post_tag:
            post_tag = PostTag(post_key=self.key, tag_key=tag.key)
            post_tag.put()


    def add_tags(self, tag_names):
        """Adds multiple tags to this post."""
        tags = [Tag.get_or_create(tag_name) for tag_name in tag_names]
        post_tags = []
        for tag in tags:
            post_tag = PostTag(post_key=self.key, tag_key=tag.key)
        ndb.put_multi(post_tags)


class Comment(ndb.Model):
    name = ndb.StringProperty(required=True)
    comment = ndb.TextProperty(required=True)
    date = ndb.DateTimeProperty(auto_now_add=True)


class PostTag(ndb.Model):
    post_key = ndb.KeyProperty(kind='Post')
    tag_key = ndb.KeyProperty(kind='Tag')


class Tag(ndb.Model):
    name = ndb.StringProperty(required=True)

    @classmethod
    def get_or_create(cls, name):
        """Gets or creates a tag with the given name."""
        tag = Tag.query(Tag.name == name).get()
        if not tag:
            tag = Tag(name=name)
            tag.put()
        return tag

    def get_posts(self):
        """Gets all posts associated with this tag."""
        post_tags = PostTag.query(PostTag.tag_key == self.key).fetch()
        post_keys = [post_tag.post_key for post_tag in post_tags]
        return ndb.get_multi(post_keys)

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
        # Get the post title and content from the form
        title = self.request.get('title')
        content = self.request.get('content')
        # Create a new Student and put it in the datastore
        post = Post(title=title, content=content)
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
        post.comment_keys.append(comment_key)
        post.put()

        self.redirect('/')

class TagHandler(webapp2.RequestHandler):
    def get(self):
        query = Tag.query()
        tags = query.fetch()
        # Pass the data to the template
        template_values = {
            'tags' : tags
        }
        template = JINJA_ENVIRONMENT.get_template('tags.html')
        self.response.write(template.render(template_values))

    def post(self):
        # Make tag
        name = self.request.get('name')

        # Find the related post
        post_url_key = self.request.get('post_url_key')
        post_key = ndb.Key(urlsafe=post_url_key)
        post = post_key.get()

        #This will create the tag if necessary
        post.add_tag(name)

        self.redirect('/')


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/comments', CommentHandler),
    ('/tags', TagHandler)
], debug=True)
