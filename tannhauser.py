#! /usr/bin/env python3

#  Autopost script for "Tannhauser Gate" project.

import time
import sys
from PIL import Image

class Poster():
    """
    The major class of app. Can post and give orders to other classes.
    """

    def __init__(self, scheduler=None):
        assert type(scheduler) is PostScheduler
        self.scheduler = scheduler

    def check(self):
        '''
        Checks if it's time to post, and does so if it is. Returns True if post was successful, False if it's
        unnecessary yet, throws exception otherwise
        :return: boolean
        '''
        if self.scheduler.is_post_time():
            print('{0} post time'.format(str(time.time())))
            post = self.scheduler.generate_post()
            try:
                self.post(post)
                return True
            except:
                sys.stderr.write('Posting at {0} unsuccessful'.format(time.asctime()))
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
        Image.open(post.image).show()
        print (post.title)

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
        self.title = title

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
        return time.time()-5 >= self.last_post

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
        post = Post(image='tmp.png', title='{0}'.format(int(time.time())))
        self.last_post = time.time()
        return post

if __name__ == '__main__':
    poster = Poster(scheduler=PostScheduler(image_source='prototype.png'))
    while 1>0:
        poster.check()
        time.sleep(1)