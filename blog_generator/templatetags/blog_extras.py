from django import template
from urllib.parse import urlparse, parse_qs
import markdown

register = template.Library()

@register.filter(name='get_yt_video_id')
def get_yt_video_id(url):
    if url is None:
        return None
    query = urlparse(url)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            p = parse_qs(query.query)
            return p.get('v', [None])[0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    return None

@register.filter(name='markdownify')
def markdownify(text):
    return markdown.markdown(text.replace('\n', '<br>'))