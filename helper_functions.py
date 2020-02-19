import os.path
from emoji import demojize
from instalooter.looters import HashtagLooter
import langid
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt; plt.rcdefaults()
import datetime
import instalooter
from IPython.display import display, HTML
import warnings
import json

### some functions

def create_init_csv(HASHTAG):
    with open("{}.csv".format(HASHTAG), "a+") as f:
        f.write("comments_disabled; id; edge_media_to_caption; shortcode; edge_media_to_comment; taken_at_timestamp; dimension; edge_liked_by; owner; is_video\n")
    print("\t{} created.".format("{}.csv".format(HASHTAG)))

def overwrite_file(HASHTAG):
    if os.path.isfile('{}.csv'.format(HASHTAG)) == True:
        print("\t{}.csv exists.".format(HASHTAG))
        answer1 = str(input('\tRemove and overwrite {}.csv? (y/n)\n'.format(HASHTAG)))
        if answer1 == 'n':
            print('\tdoing nothing...')
            return
        if answer1 == 'y':
            os.remove("{}.csv".format(HASHTAG))
            print("\told {}.csv removed!".format(HASHTAG))
            create_init_csv(HASHTAG)

    if os.path.isfile('{}.csv'.format(HASHTAG)) == False:
        print('{}.csv does not exist.'.format(HASHTAG))
        create_init_csv(HASHTAG)

def post_info(HASHTAG,media):
    try:
        comments_disabled = media['comments_disabled']
    except:
        comments_disabled = None
    try:
        id_ = media['id']
    except:
        id_ = None
    try:
        # translating emojis to text, replacing ; to ,replace linebreaks with spaces
        edge_media_to_caption = demojize(media['edge_media_to_caption']['edges'][0]['node']['text']).replace(";","").replace('\n',' ')
    except:
        edge_media_to_caption = None
    try:
        shortcode = media['shortcode']
    except:
        shortcode = None
    try:
        edge_media_to_comment = media['edge_media_to_comment']['count']
    except:
        edge_media_to_comment = None
    try:
        taken_at_timestamp = media['taken_at_timestamp']
    except:
        taken_at_timestamp = None

    try:
        dimension = (media['dimensions']['height'], media['dimensions']['width'])
    except:
        dimension = None
    try:
        edge_liked_by = media['edge_liked_by']['count']
    except:
        edge_liked_by = None
    try:
        owner = media['owner']['id']
    except:
        owner = None
    try:
        is_video = media['is_video']
    except:
        is_video = None

    nfo = '{}; {}; {}; {}; {}; {}; {}; {}; {}; {}'.format(comments_disabled,id_,edge_media_to_caption,shortcode,edge_media_to_comment,taken_at_timestamp,dimension,edge_liked_by,owner,is_video)


    with open("{}.csv".format(HASHTAG), "a+") as f:
        f.write("{}\n".format(nfo))


def hashtags_in_str(r):
    '''given a string, returns an array containing
    the number of hashtags used [0] and
    a list of the used hashtags [1]'''
    word_list=[]
    tag_list=[]
    # for cases where more than one hastags are in one 'word'
    try:
        r = r.replace('#',' #')
    except:
        r = r
    word_list = str(r).split()

    for tag in word_list:
        if tag.startswith("#"):
            tag=tag.split('.')[0]
            tag_list.append(tag.strip("#"))
    try:
        tag_list.remove('')
    except:
        pass
    return len(tag_list),(', '.join(tag_list))

def language_id(text):
    return str(langid.classify(text)[0])

def draw(df,HASHTAG,y_axis,x_axis,yscale,cuttoff_date):
    # Figure
    plt.figure(num=None, figsize=(10, 2), dpi=300, facecolor='w', edgecolor='k')

    # Plot
    plt.scatter(x = df[x_axis],y = df[y_axis],c='b',alpha=0.3,marker='.',s=1)

    # Limits
    #cuttoff_date = datetime.date(2018, 1, 1)
    # cuttoff_date = df['timestamp'].min().to_pydatetime().date()
    plt.xlim([cuttoff_date, df['timestamp'].max().to_pydatetime().date()])

    # Ticks
    plt.xticks(rotation=90)

    # Scale
    plt.yscale(yscale) # yscale values : 'linear' or 'symlog' for best results


    # Text
    plt.title('{} per usage of #{} \nin media captions per {} of media'.format(y_axis.replace('_',' ').replace('edge ',''),HASHTAG,x_axis))
    plt.xlabel(x_axis)
    plt.ylabel(y_axis.replace('_',' ').replace('edge ',''))

    print('Hashtag: #{}'.format(HASHTAG))
    plt.show()

def post_location_data(row):
    shortcode = row
    js = instalooter.looters.PostLooter(shortcode).get_post_info(shortcode)
    try:
        address_json = json.loads(js['location']['address_json'])
        try:
            street_address = (address_json['street_address'])
        except:
            street_address = None
        try:
            zip_code = (address_json['zip_code'])
        except:
            zip_code = None
        try:
            city_name = (address_json['city_name'])
        except:
            city_name = None
        try:
            region_name = (address_json['region_name'])
        except:
            region_name = None
        try:
            country_code = (address_json['country_code'])
        except:
            country_code = None
        try:
            exact_city_match = (address_json['exact_city_match'])
        except:
            exact_city_match = None
        try:
            exact_region_match = (address_json['exact_region_match'])
        except:
            exact_region_match = None
        try:
            exact_country_match = (address_json['exact_country_match'])
        except:
            exact_country_match = None
            
        try:
            caption_is_edited = (js['caption_is_edited'])
        except:
            caption_is_edited = None       

        #out = [street_address,zip_code,city_name,region_name,country_code,exact_city_match,exact_region_match,exact_country_match]
        out = [caption_is_edited,country_code,city_name]
        #out = country_code
        #out = caption_is_edited

    except:
        #out = np.nan
        out = [np.nan,np.nan,np.nan]
    
    return out


def cap_edited(TOP_LIMIT,df):
    '''for checking whether a post was edited'''
    for i in range(int(TOP_LIMIT)):
        try:
            shortcode=df.iloc[i]['shortcode']
            URL = ("https://www.instagram.com/p/{}/".format(shortcode))
            json = instalooter.looters.PostLooter(shortcode).get_post_info(shortcode)
            print('{}\tcaption_is_edited: {}'.format(URL,json['caption_is_edited']))
        except:
            print('{}\tcaption_is_edited: {}'.format(URL,None))
            
def get_username(shortcode):
    try:
        js = instalooter.looters.PostLooter(shortcode).get_post_info(shortcode)
        username = str(js['owner']['username'])
    except:
        username = None
    return username