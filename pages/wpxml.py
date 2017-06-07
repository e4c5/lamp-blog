from xml.etree.ElementTree import ElementTree, XMLTreeBuilder
from bs4 import BeautifulSoup  # @UnresolvedImport
import re
import httplib2
import json
from django.utils.http import urlencode
from django.utils.html import strip_tags
import traceback

SERVER = 'http://localhost:9000/importer/'  #
#SERVER = 'https://radithablog.appspot.com/importer/'
def wpxml_reader(filename):
    tree = ElementTree()
    root = tree.parse(filename)
    channel = root.find('channel')
    np = {'wp':'http://wordpress.org/export/1.2/', 
          'content': "http://purl.org/rss/1.0/modules/content/"}
    for item in channel.findall('item') :
        try :
            resp =  {'alt_link' : item.find('wp:post_name', np).text,
                     'postdate': item.find('wp:post_date_gmt', np).text,
                     'title' : item.find('title').text,
                     'draft': item.find('wp:status', np).text != 'publish',
                     'link' : re.sub('http://raditha.com/blog/archives/', '', item.find('link').text),
                    }
            
            raw_content = item.find('content:encoded',np).text
            img = False
            if re.search('img', raw_content) :
                raw_content = re.sub('\[caption.*?caption="(.*?)"](.*?)\[/caption]', 
                                     "<figure style='text-align:center'>\\2 <figcaption>\\1</figcaption></figure>",raw_content)
                print resp['link']
                img = True
            if raw_content :
                soup = BeautifulSoup(raw_content)

                if len(soup.find_all('p')) > 1 :
                    resp['content'] = raw_content.encode('utf-8')
                else :
                    if soup.p :
                        # there is exactly one '<p>' sorrounding the whole block. The rest of it
                        # is lost in translation.
                        resp['content'] = u"".join([u"<p>{0}</p>".format(p) for p in soup.p.__unicode__().split('\n') if p]).encode('utf-8')
                    else :
                        # wraps off!
                        resp['content'] = u"".join([u"<p>{0}</p>".format(p) for p in soup.body.__unicode__().split('\n') if p]).encode('utf-8')
                    
                            
                categories = []
                tags = []
                
                for cat in item.findall('category') :
                    if cat.attrib['domain'] == 'category':
                        categories.append(cat.attrib['nicename'])
                    else :
                        tags.append(cat.text)
                
                resp['tags'] = tags
                resp['categories'] = categories
                try :
                    resp['summary'] = strip_tags(resp['content'])[0:300]
                except :
                    resp['summary'] = resp['content'][0:300]

                if resp['title'] == 'Wordpress Chart Plugin':
                    print raw_content
                    print resp['content']
                yield resp
            else :
                print "%s has no content" % item.find('title').text
        except Exception , e:
            print traceback.format_exc()
            pass
            
            
if __name__ == '__main__':
    i = 0;
    h = httplib2.Http()
      
    
    for postdata in wpxml_reader('/home/raditha/Downloads/thesitewiththelamp.wordpress.2014-02-24.xml') :
        try :
            if i % 25 == 0 :
                print i
            i += 1

            h.request(SERVER,'POST', 
                  urlencode({'data': json.dumps(postdata) , 'content': 'new',
                            'campfire': 'HM 0_JuAt RanDOM keY to PROTECT GAints attacks Q(!ZOIE/.kl'}));            
        except :
            pass
    
            