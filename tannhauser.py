#! /usr/bin/env python3

#  Autopost script for "Tannhauser Gate" project.

import time
import sys
import argparse
from PIL import Image
import vk

class Poster():
    """
    The major class of app. Can post and give orders to other classes.
    """

    def __init__(self, public_id=None, app_id=None, scheduler=None, login=None, password=None):
        assert type(scheduler) is PostScheduler
        self.scheduler = scheduler
        self.public_id = public_id
        self.app_id=app_id
        self.session=vk.AuthSession(app_id=self.app_id, scope='groups,wall,photos',
                                    user_login=login, user_password=password)
        self.api = vk.API(self.session)

    def check(self):
        '''
        Checks if it's time to post, and does so if it is. Returns True if post was successful, False if it's
        unnecessary yet, throws exception otherwise
        :return: boolean
        '''
        if self.scheduler.is_post_time():
            print('{0} post time'.format(str(time.time())))
            post = self.scheduler.generate_post()
            # try:
            self.post(post)
            return True
            # except:
            #     sys.stderr.write('Posting at {0} unsuccessful'.format(time.asctime()))
        else:
            print(time.time())
            return False

    def post(self, post):
        '''
        Post the thing to public using VK API, change public title accordingly and remove old posts.
        :param post: Post
        :return: nothing
        '''
        assert type(post) is Post
        print (post.title)
        #  Get the wall and remove everything
        wall_posts = self.api.wall.get(owner_id='-{0}'.format(self.public_id),
                                     filter=all)
        post_ids=[x['id'] for x in wall_posts[1:]] #  Skip the first element: it's post count
        for post_id in post_ids:
            self.api.wall.delete(owner_id='-{0}'.format(self.public_id),
                                 post_id=post_id)
        #  Add the photo to the album
        # upload_server=self.api.photos.getWallUploadServer(group_id=self.public_id)
        # print(upload_server)
        #  Add the post to the wall
        self.api.wall.post(owner_id='-{0}'.format(self.public_id),
                           from_group=1,
                           message=post.image)
        #  Renaming. Post title should include at least some non-numeric symbols
        self.api.groups.edit(group_id=self.public_id, title=post.title)

class Post():
    '''
    Data class that contains post image, new public title and posting time.
    Has no methods, only attributes.
    '''

    def __init__(self, image=None, title='Tannhauser'):
        # Add the posting time, when schedule actually works
        #  No need for property decorators, as Post object will not change after it's created
        assert type(image) is str
        assert type(title) is str
        self.image = image
        self.title = str(title)

class PostScheduler():
    '''
    Post factory and posting schedule.
    '''

    def __init__(self, image_source, posting_interval=60, image_step=500, image_size=1000):
        '''
        Create a post scheduler.
        :param image_source: str. A filename with PNG image
        :param posting_interval: int. The time that should elapse between subsequent posts, in seconds
        :param posting_step: int. The x frameshift between subsequent posts, in pixels.
        :param image_size: int. The x size of image for a post
        :return:
        '''
        #self.image_source = image_source
        self.image = Image.open(image_source)
        self.posting_interval = posting_interval
        self.image_size = image_size
        #  This will later be replaced by the time of last post
        self.last_post = time.time()
        self.image_step = image_step
        #  Left border of the next post (in px from the left image border)
        self.current_pos = 0

    def is_post_time(self):
        '''
        Return True if it's time to post something, False otherwise
        :return:
        '''
        #  Simply returns true if a minute elapsed since the object was created or post generated
        return time.time()-10 >= self.last_post

    def generate_post(self):
        '''
        Generates post that is to be posted next. Assumes that whatever it generated was actually posted,
        so handling posting errors is the other classses' problem.
        :return:
        '''
        #  Crop and write down the subimage
        piece = self.image.crop((self.current_pos, 0, self.current_pos+self.image_size, self.image.size[1]))
        piece.save('tmp.png')
        self.current_pos += self.image_step
        #  Say we have produced the last frame and need to cycle back
        if self.current_pos+self.image_size > self.image.size[0]:
            self.current_pos = 0
        post = Post(image='tmp.png', title='Shift_{0}'.format(self.current_pos-self.image_step))
        self.last_post = time.time()
        return post


if __name__ == '__main__':
    #  Init arguments parser
    args_parser = argparse.ArgumentParser(description='Autopost system for Tannhauser Gate project')
    args_parser.add_argument('-g', type=str, help='Group ID (number, not a string!')
    args_parser.add_argument('-a', type=str, help='App ID')
    args_parser.add_argument('-l', type=str, help='User login')
    args_parser.add_argument('-p', type=str, help='User password')
    args = args_parser.parse_args()
    poster = Poster(public_id=args.g,
                    app_id=args.a,
                    login=args.l,
                    password=args.p,
                    scheduler=PostScheduler(image_source='prototype.png'))
    while 1>0:
        poster.check()
        time.sleep(1)