import cStringIO
import feeds
from flask import Flask
import urllib2
import urlparse as urlparse2
import xml.etree.ElementTree as ET


app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/feed/<feed_route>')
def handle_feed(feed_route):
    for feed in feeds.FEEDS:
        if feed['route'] == feed_route:
            return convert_feed(feed)
    return 'No feed with route %s' % feed_route


def convert_feed(feed):
    request = urllib2.Request(feed['url'])
    response = urllib2.urlopen(request)
    status = response.getcode()

    if status == 200:
        return convert_response(feed, response)
    else:
        return 'Unexpected status code %d' % status


def convert_response(feed, response):
    ET.register_namespace('', "http://www.w3.org/2005/Atom")
    ET.register_namespace('idx', "urn:atom-extension:indexing")
    root = ET.fromstring(response.read())

    update_feed_title(root, feed['title'])

    for entry in root.findall(tag('entry')):
        update_entry(entry)

    tree = ET.ElementTree(element=root)
    string_file = cStringIO.StringIO()
    tree.write(string_file)
    result = string_file.getvalue()
    string_file.close()
    return result


def update_feed_title(root, new_title):
    title_element = root.find(tag('title'))
    if title_element is not None:
        title_element.text = new_title


def update_entry(entry):
    link = entry.find(tag('link'))
    if link is not None:
        link.set('href', extract_raw_url(link.attrib['href']))

    title = entry.find(tag('title'))
    if title is not None:
        title.text = convert_content(title.text)

    content = entry.find(tag('content'))
    if content is not None:
        content.text = convert_content(content.text)


def extract_raw_url(google_url):
    return urlparse2.parse_qs(urlparse2.urlparse(google_url).query)['url'][0]


def convert_content(content):
    result = content
    result = result.replace('<b>', '*')
    result = result.replace('</b>', '*')
    print result
    return result


def tag(value):
    return '{http://www.w3.org/2005/Atom}%s' % value


if __name__ == '__main__':
    app.run()
