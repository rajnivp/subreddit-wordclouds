import requests
import string
import sys
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
import nltk

nltk.download('stopwords')  # Download stopwords corpus
from nltk.corpus import stopwords


def generate_wordcloud(subreddit, num_words=40, save=False):
    """
    This function will fetch reddit most recent comments data for given sub-reddit.
    sanitize comments data and plot word cloud of most frequent words used in comments.
    specify number of word for word cloud in num_words arguments.
    set save to True to save plot as png.
    """
    url = f"https://api.pushshift.io/reddit/search/comment/?subreddit={subreddit}&sort=des&size=500"

    res = requests.get(url)
    res = res.json()  # Convert to dict
    res = res['data']

    filtered_comments = []

    # Loop through all data and get text in body of comments
    for r in res:

        # Remove words that start or ends with following words
        stop_words = ['[', '(', 'http', 'u/', 'r/', '!', ']', ')', '*']

        # Remove punctuation from comments strings
        query_words = r['body'].lower().translate(str.maketrans('', '', string.punctuation))
        query_words = nltk.word_tokenize(query_words)

        # Remove too long and single letter words
        for i in query_words:
            if len(i) > 15 or len(i) == 1:
                query_words.remove(i)

            # Remove words that start or ends with words in stop_words list
            for j in stop_words:
                try:
                    if i.startswith(j):
                        query_words.remove(i)
                    elif i.endswith(j):
                        query_words.remove(i)

                # If it is already removed then pass
                except ValueError:
                    pass

        # Add processed comments to filtered_comments list
        filtered_comments.extend(query_words)

    # Create dictionaries with words as keys and their count in list as value of that word key
    word_count = dict()

    # Get stopwords from nltk corpus
    stop_words = stopwords.words('english')

    # Add more stopwords from wordcloud library
    more_stopwords = set(STOPWORDS)

    # Load stopwords from stopwords.csv file. add words you want to ignore to this file
    new_stopwords = pd.read_csv("data/stopwords.csv")
    new_stopwords = list(new_stopwords['stopwords'])

    # Add all stopwords to stop_words
    stop_words.extend(new_stopwords)
    stop_words.extend(more_stopwords)

    # Make it a set to avoid duplicates
    stop_words = set(stop_words)

    # Put key-values in created word_count dictionary based count of words in list
    for word in filtered_comments:
        # Avoid words that are in stopwords
        if word not in stop_words:
            freq = filtered_comments.count(word)
            word_count[word] = freq

    # Generate WordCoud with 40 words
    wordcloud = WordCloud(width=500, height=500,
                          background_color='white',
                          max_words=num_words,
                          min_font_size=10).generate_from_frequencies(word_count)

    # plot the WordCloud
    plt.figure(figsize=(5, 5), facecolor=None)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout(pad=1)

    if save:
        plt.savefig(f"clouds/{subreddit}.png", bbox_inches="tight")
        plt.close()
    else:
        plt.show()


if __name__ == '__main__':
    subreddit = sys.argv[1]
    generate_wordcloud(subreddit)
