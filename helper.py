import nltk
from urlextract import URLExtract
from wordcloud import WordCloud
from collections import Counter
import pandas as pd

nltk.download('stopwords')
from nltk.corpus import stopwords

#reading the stop words
with open("stop_words.txt", "r") as f:
    content1 = {word.lower() for word in f.read().split()}
with open("bengali_pronouns.txt", "r",encoding="utf-8") as f:
    content2 = {word.lower() for word in f.read().split()}
nltk_stopwords = set(word.lower() for word in stopwords.words('english'))
ALL_STOPWORDS = content1.union(content2).union(nltk_stopwords)

extract = URLExtract()

def fetch_data(selected_user, df):
    #number of messages
    if selected_user != 'overall':
        df = df[df['user'] == selected_user]
    num_messages = df.shape[0]
    # number of words
    words = []
    for message in df['message']:
        words.extend(message.split())
    #number of medias
    medias = df[df['message'] == '<Media omitted>'].shape[0]

    #fetch number of links
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))
    return num_messages, len(words), len(set(words)), medias, len(links)
def fetch_most_busy_users(df):
    x = df[df['user'] != 'group_notification']['user'].value_counts()
    df = round((df[df['user'] != 'group_notification']['user'].value_counts()/df.shape[0])*100,2).reset_index().rename(columns={'user':'name','count':'activity-percentage'})
    return x,df

#creating the wordcloud

def create_wordcloud(select_user, df):
    if select_user != 'overall':
        df = df[df['user'] == select_user]
    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    def remove_stopwords(message):
        words = []
        for word in message.lower().split():
            if word.lower() not in ALL_STOPWORDS:
                words.append(word)
        return " ".join(words)

    wc = WordCloud(width=500,height=500,min_font_size=7,background_color='white')
    temp['message'] = temp['message'].apply(remove_stopwords)
    df_wc = wc.generate(temp['message'].str.cat(sep=" "))
    return df_wc


#finding the max words:

def max_word(select_user, df):

    if select_user != 'overall':
        df = df[df['user'] == select_user]
    tempdf = df[df['user'] != 'group_notification']
    tempdf = tempdf[tempdf['message'] != '<Media omitted>\n']
    words = []
    for message in tempdf['message']:
        for word in message.lower().split():
            if word.lower() not in ALL_STOPWORDS:
                words.append(word)
    result = dict(Counter(words))
    top10 = sorted(result.items(), key=lambda x: x[1], reverse=True)[:20]
    top10 = pd.DataFrame(top10, columns=['word', 'count'])
    top10['percentage'] = (top10['count'] / top10['count'].sum() * 100).round(2)
    return top10

def monthly_timeline(selected_user, df ):
    if selected_user != 'overall':
        df = df[df['user'] == selected_user]
    timeline = df.groupby(['year', 'month_number', 'month']).count()['message'].reset_index()
    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))
    timeline['time'] = time
    return timeline


def weekly_activity_map(selected_user,df):
    if selected_user != 'overall':
        df= df[df['user'] == selected_user]
    return df['day_name'].value_counts()


def User_heatmap(selected_user,df):
    if selected_user != 'overall':
        df = df[df['user']== selected_user]
    User_heatmap = df.pivot_table(index='day_name', columns='period', values='message',aggfunc='count').fillna(0)
    return User_heatmap