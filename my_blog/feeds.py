from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords
from my_blog.models import Post


class LatestPostFeed(Feed):
    title = 'Mój blog'
    link = '/my_blog/'
    description = 'Nowe posty na moim blogu.'

    def items(self):
        return Post.published.all()[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return truncatewords(item.body, 30)