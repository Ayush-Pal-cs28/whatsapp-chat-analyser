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
    medias = df[df['message'] == '<Media omitted>\n'].shape[0]

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

def response_time_analysis(selected_user, df):
    temp = df[df['user'] != 'group_notification'].copy()
    temp = temp.sort_values('date').reset_index(drop=True)

    temp['prev_user'] = temp['user'].shift(1)
    temp['prev_time'] = temp['date'].shift(1)
    temp['response_time'] = (temp['date'] - temp['prev_time']).dt.total_seconds() / 60

    responses = temp[
        (temp['user'] != temp['prev_user']) &
        (temp['response_time'] > 0) &
        (temp['response_time'] < 720)
    ]

    if selected_user != 'overall':
        responses = responses[responses['user'] == selected_user]

    avg_response = responses.groupby('user')['response_time'].mean().round(2).sort_values()

    responses['month_year'] = responses['date'].dt.to_period('M').astype(str)

    monthly_trend = responses.groupby('month_year')['response_time'].mean().round(2)

    fastest = avg_response.idxmin() if not avg_response.empty else None
    slowest = avg_response.idxmax() if not avg_response.empty else None

    return avg_response, monthly_trend, fastest, slowest


def day_night_activity(selected_user, df):
    temp = df[df['user'] != 'group_notification'].copy()

    # classify each message as day or night
    # Day: 6AM - 10PM (6 to 21)
    # Night: 10PM - 6AM (22 to 5)
    def classify_time(hour):
        if 6 <= hour <= 21:
            return 'Day'
        else:
            return 'Night'

    temp['time_of_day'] = temp['hour'].apply(classify_time)

    if selected_user != 'overall':
        temp = temp[temp['user'] == selected_user]

        # count day vs night messages
        counts = temp['time_of_day'].value_counts()
        day_count = counts.get('Day', 0)
        night_count = counts.get('Night', 0)

        # determine if day or night person
        total = day_count + night_count
        day_pct = round((day_count / total) * 100, 1) if total > 0 else 0
        night_pct = round((night_count / total) * 100, 1) if total > 0 else 0

        if day_pct >= night_pct:
            personality = f"🌞 Day Person ({day_pct}% messages sent during day)"
        else:
            personality = f"🌙 Night Owl ({night_pct}% messages sent during night)"

        # hourly breakdown for that user
        hourly = temp.groupby(['hour', 'time_of_day']).size().reset_index(name='count')

        return 'single', personality, day_count, night_count, day_pct, night_pct, hourly

    else:
        # classify each user as day or night person
        user_summary = []

        for user in temp['user'].unique():
            user_df = temp[temp['user'] == user]
            counts = user_df['time_of_day'].value_counts()
            day_count = counts.get('Day', 0)
            night_count = counts.get('Night', 0)
            total = day_count + night_count

            if total == 0:
                continue

            day_pct = round((day_count / total) * 100, 1)
            night_pct = round((night_count / total) * 100, 1)
            category = 'Day' if day_pct >= night_pct else 'Night'

            user_summary.append({
                'user': user,
                'day_count': day_count,
                'night_count': night_count,
                'day_pct': day_pct,
                'night_pct': night_pct,
                'category': category
            })

        summary_df = pd.DataFrame(user_summary)
        day_people = summary_df[summary_df['category'] == 'Day'].sort_values('day_pct', ascending=False)
        night_people = summary_df[summary_df['category'] == 'Night'].sort_values('night_pct', ascending=False)

        return 'overall', day_people, night_people