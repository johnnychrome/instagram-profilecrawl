"""Methods to extract the data for the given usernames profile"""
from time import sleep
from re import findall
import math
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import requests

def get_user_info(browser):
  """Get the basic user info from the profile screen"""

  container = browser.find_element_by_class_name('_mesn5')
  img_container = browser.find_element_by_class_name('_b0acm')

  infos = container.find_elements_by_class_name('_t98z6')
                           
  alias_name = container.find_element_by_class_name('_ienqf')\
                        .find_element_by_tag_name('h1').text
  try:
    bio = container.find_element_by_class_name('_tb97a')\
                        .find_element_by_tag_name('span').text                      
  except:
    print ("Bio is empty", "\n")
    bio = ""
  print ("►►Alias name: ", alias_name, "\n")
  print ("►►Bio: ", bio, "\n")
  prof_img = img_container.find_element_by_tag_name('img').get_attribute('src')
  num_of_posts = int(infos[0].text.split(' ')[0].replace(',', ''))
  followers = str(infos[1].text.split(' ')[0].replace(',', ''))
  if followers.find('.') != -1:
    followers = followers.replace('.', '')
    followers = int(followers.replace('k', '00').replace('m', '00000'))
  else:
    followers = int(followers.replace('k', '000').replace('m', '000000'))
  following = str(infos[2].text.split(' ')[0].replace(',', ''))
  if following.find('.') != -1:
    following = following.replace('.', '')
    following = int(following.replace('k', '00').replace('m', '00000'))
  else:
    following = int(following.replace('k', '000').replace('m', '000000'))

  return alias_name, bio, prof_img, num_of_posts, followers, following


def extract_post_info(browser):
  """Get the information from the current post"""

  post = browser.find_element_by_class_name('_622au')

  # Get caption
  caption = ''
  try:
    username = post.find_element_by_class_name('_iadoq').text
    caption_username = post.find_element_by_class_name('_b0tqa').find_element_by_class_name('_ezgzd').find_element_by_tag_name('a').text
    if username == caption_username:
        caption = post.find_element_by_class_name('_b0tqa').find_element_by_class_name('_ezgzd').find_element_by_tag_name('span').text
  except:
    pass

  # Get location details
  location_url = ''
  location_name = ''
  location_id = 0
  lat = ''
  lng = ''
  try:
    # Location url and name
    x = post.find_element_by_class_name('_60iqg').find_elements_by_tag_name('a')
    location_url = x[0].get_attribute('href')
    location_name = x[0].text

    # Longitude and latitude
    location_id = location_url.strip('https://www.instagram.com/explore/locations/').split('/')[0]
    url = 'https://www.instagram.com/explore/locations/' + location_id + '/?__a=1'
    response = requests.get(url)
    data = response.json()
    lat = data['graphql']['location']['lat']
    lng = data['graphql']['location']['lng']
  except:
    pass

  #print('BEFORE IMG')

  imgs = post.find_elements_by_tag_name('img')
  img = ''
  
  
  if len(imgs) >= 2:
    img = imgs[1].get_attribute('src')
    

  likes = 0
  
  if len(post.find_elements_by_tag_name('section')) > 2:
    likes = post.find_elements_by_tag_name('section')[1]\
            .find_element_by_tag_name('div').text
    
    likes = likes.split(' ')

    #count the names if there is no number displayed
    if len(likes) > 2:
      likes = len([word for word in likes if word not in ['and', 'like', 'this']])
    else:
      likes = likes[0]
      likes = likes.replace(',', '').replace('.', '')
      likes = likes.replace('k', '00')

  # if more than 22 comment elements, use the second to see
  # how much comments, else count the li's

  # first element is the text, second either the first comment
  # or the button to display all the comments
  comments = []
  tags = []
  
  date = post.find_element_by_tag_name('time').get_attribute("datetime")
  #print ("date is ", date)  
  
  if post.find_elements_by_tag_name('ul'):
    comment_list = post.find_element_by_tag_name('ul')
    comments = comment_list.find_elements_by_tag_name('li')
    
    if len(comments) > 1:
      # load hidden comments
      while (comments[1].text == 'load more comments'):
        comments[1].find_element_by_tag_name('button').click()
        comment_list = post.find_element_by_tag_name('ul')
        comments = comment_list.find_elements_by_tag_name('li')
        
      tags = comments[0].text + ' ' + comments[1].text
    else:
      tags = comments[0].text

    tags = findall(r'#[A-Za-z0-9]*', tags)
    print (len(user_commented_list), " comments.")
    return caption, location_url, location_name, location_id, lat, lng, img, tags, int(likes), int(len(comments) - 1), date

                                                  
def extract_information(browser, username, limit_amount):
  """Get all the information for the given username"""

  browser.get('https://www.instagram.com/' + username)

  try:
    alias_name, bio, prof_img, num_of_posts, followers, following \
    = get_user_info(browser)
    if limit_amount <1 :
        limit_amount = 999999
    num_of_posts = min(limit_amount, num_of_posts)
  except:
    print ("►►Error: Couldn't get user profile.\nTerminating", "\n")
    with open('not_completed', 'a') as out:
	out.write(username + ": Couldn't get user profile\n")
    out.close()
    inf_err = {
        'alias': "ERROR",
        'username': username,
        'bio': "ERROR",
        'prof_img': "ERROR",
        'num_of_posts': "ERROR",
        'followers': "ERROR",
        'following': "ERROR",
        'posts': "ERROR"     
    }
    return inf_err
  prev_divs = browser.find_elements_by_class_name('_70iju')


  try:
    body_elem = browser.find_element_by_tag_name('body')

    #load_button = body_elem.find_element_by_xpath\
    #  ('//a[contains(@class, "_1cr2e _epyes")]')
    #body_elem.send_keys(Keys.END)
    #sleep(3)

    #load_button.click()

    links = []
    links2 = []
    
    #list links contains 30 links from the current view, as that is the maximum Instagram is showing at one time
    #list links2 contains all the links collected so far
    
    previouslen = 0
    breaking = 0
    
    #print ("►►Getting only first",12*math.ceil(num_of_posts/12),"posts only, if you want to change this limit, change limit_amount value in crawl_profile.py\n")  
    while (len(links2) < num_of_posts):
      
      prev_divs = browser.find_elements_by_tag_name('main')      
      links_elems = [div.find_elements_by_tag_name('a') for div in prev_divs]  
      links = sum([[link_elem.get_attribute('href')
        for link_elem in elems] for elems in links_elems], [])
      for link in links:
        if "/p/" in link:
          links2.append(link) 
      links2 = list(set(links2))   
      print ("►►Scrolling posts: ", len(links2), "/", num_of_posts, end="\r")
      body_elem.send_keys(Keys.END)
      sleep(1.5)
   
      ##remove bellow part to never break the scrolling script before reaching the num_of_posts
      if (len(links2) == previouslen):
          breaking += 1
	  print ("\n►►Breaking in ", 5-breaking, "... (If you believe this is caused by slow internet, increase sleep time in line 152 in extractor.py)","\n")
          sleep(2.5)
      else:
          breaking = 0
      if breaking > 4:
          print ("►►Not getting any more posts, ending scrolling and scraping.","\n") 
          with open('not_completed', 'a') as out:
              out.write(alias_name + ': Freeze at ' + str(len(links2)) + '/' + str(num_of_posts) + '\n') 
          out.close()
	  sleep(2)
	  inf_err = {
              'alias': alias_name,
              'username': username,
              'bio': bio,
              'prof_img': "ERROR",
              'num_of_posts': "ERROR",
              'followers': "ERROR",
              'following': "ERROR",
              'posts': "ERROR"     
          }
          return inf_err
      previouslen = len(links2)   
      ##

  except NoSuchElementException as err:
    print('►►Something went terribly wrong\n')

  post_infos = []

  counter = 1
  
  for link in links2:
    
    #print ("\n", counter , "/", len(links2))
    counter = counter + 1
    
    print ("►►Scrapping posts: ", counter , "/", len(links2), end="\r")
    browser.get(link)
    try:
      caption, location_url, location_name, location_id, lat, lng, img, tags, likes, comments, date = extract_post_info(browser)

      location = {
        'location_url': location_url,
        'location_name': location_name,
        'location_id': location_id,
        'latitude': lat,
        'longitude': lng,
      }

      post_infos.append({
        'caption': caption,
        'location': location,
        'img': img,
        'date': date,
        'tags': tags,
        'likes': likes,
        'comments': comments
      })
    except NoSuchElementException:
      print('►►Could not get information from post: ' + link, "\n")



  information = {
    'alias': alias_name,
    'username': username,
    'bio': bio,
    'prof_img': prof_img,
    'num_of_posts': num_of_posts,
    'followers': followers,
    'following': following,
    'posts': post_infos     
  }    

return information
