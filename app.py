import matplotlib.pyplot as plt
import seaborn as sns
import preprocessor as pp
import helper as h
import streamlit as st

st.sidebar.title("WhatsApp Chat Analyzer")
uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = pp.preprocess(data)

    #fetch unique users
    user_list = df['user'].unique().tolist()
    user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0,'overall')
    selected_usr = st.sidebar.selectbox("show analysis w.r.t", user_list)

    if st.sidebar.button("Show analysis"):
        st.title("Top statistics")
        num_messages, num_words, distinct_words, medias, links= h.fetch_data(selected_usr,df)
        col1, col2,col3,col4,col5 = st.columns(5)
        with col1:
            st.metric(f"Total messages",num_messages)
            # st.header(num_messages)
        with col2:
            st.metric(f"Total words",num_words)
            # st.header(num_words)
        with col3:
            st.metric(f"Total distinct words",distinct_words)
            # st.header(distinct_words)
        with col4:
            st.metric(f"Total medias",medias)
            # st.header(medias)
        with col5:
            st.metric(f"Total links",links)
            # st.title(links)
        col1,col2 = st.columns(2)
        with col1:
            #user timeline
            st.title("monthly timeline")
            timeline = h.monthly_timeline(selected_usr,df)
            fig, ax = plt.subplots()
            ax.plot(timeline['time'], timeline['message'])
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
        with col2:
            #activity map
            st.title('Activity map')
            busy_day = h.weekly_activity_map(selected_usr,df)
            fig, ax = plt.subplots()
            ax.barh(busy_day.index,busy_day.values)
            st.pyplot(fig)

        #finding the busiest user in the chat
        if selected_usr == 'overall':
            st.title("user activity")
            x,new_df = h.fetch_most_busy_users(df)
            fig, ax = plt.subplots()

            col1, col2 = st.columns(2)

            with col1:
                ax.bar(x.index,x.values)
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            with col2:
                st.dataframe(new_df)
        col1,col2 = st.columns(2)

        with col1:
            #WordCloud
            st.title("Word-Cloud")
            df_wc = h.create_wordcloud(selected_usr,df)
            fig, ax = plt.subplots()
            ax.imshow(df_wc)
            st.pyplot(fig)

        with col2:
            #most common words
            st.title("Top 20 most common words")
            new_df = h.max_word(selected_usr,df)
            fig, ax = plt.subplots()
            ax.barh(new_df['word'],new_df['count'])
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        #activity heatmap:
        st.title("weekly activity HeatMap")
        user_heatmap = h.User_heatmap(selected_usr,df)
        fig, ax = plt.subplots()
        ax = sns.heatmap(user_heatmap)
        st.pyplot(fig)


