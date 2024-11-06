# YouTube Comment Analysis Tool

This Python tool provides an in-depth analysis of YouTube video comments using various NLP and sentiment analysis techniques. It fetches YouTube video metadata, performs sentiment and emotion analysis, extracts top keywords, and visualizes the data through charts and word clouds. Additionally, the tool includes topic modeling, clustering, and user interaction analysis.

## Features

- **Fetch YouTube Video Metadata**: Retrieve metadata for a YouTube video, including title, description, view count, like count, comments, etc.
- **Comment Sentiment Analysis**: Analyze the sentiment of video comments (positive, negative, neutral).
- **Emotion Analysis**: Identify the dominant emotions expressed in the comments.
- **Key Phrase Extraction**: Extract and visualize key phrases (top 20 keywords) from comments.
- **Word Cloud Generation**: Visualize the most frequent words in the comments.
- **Sentiment and Emotion Distribution Visualization**: Visualize sentiment and emotion distributions with bar charts.
- **Comment Timeline**: Visualize the timeline of comments posted over time.
- **Topic Modeling**: Perform Latent Dirichlet Allocation (LDA) topic modeling on the comments.
- **Top Comments**: Identify and analyze the top liked comments.
- **Comment Length Analysis**: Analyze the length of comments and generate a distribution chart.
- **Clustering Analysis**: Cluster comments into topics using KMeans clustering.
- **User Interaction Network**: Analyze user interactions and create a network graph of replies and replies-to-replies.

## Requirements

To use this tool, you need to install the required Python libraries. Run the following command to install the dependencies:

```bash
pip install -r requirements.txt
```

## YouTube API Key Setup

To use this tool, you will need a YouTube API key. Follow these steps to obtain one:

1. Go to the Google Cloud Console.
2. Create a new project or select an existing one.
3. Enable the YouTube Data API v3.
4. Create an API key.
5. Save the API key as an environment variable (`YOUTUBE_API_KEY`) or create a `.env` file with the following content:

    ```plaintext
    YOUTUBE_API_KEY=your-api-key-here
    ```

If you are running this on Google Colab, use the following code to access the API key:

```python
from google.colab import userdata
api_key = userdata.get('YOUTUBE_API_KEY')
```

## Usage

### Running the script

To start the analysis, run the `main.py` script:

```bash
python main.py
```

### Input the YouTube Video URL

When prompted, enter the YouTube video URL to analyze.

**Example:**

```bash
YouTube Video URL'sini girin: https://www.youtube.com/watch?v=VIDEO_ID
```

### Output Files

- `video_metadata.json`: Video metadata information.
- `sentiment_analysis.json`: Analysis of comments including sentiment distribution, emotion distribution, top keywords, and top active users.
- `topic_modeling.json`: Topic modeling results (LDA).
- `top_comments.json`: Analysis of the top 10 most liked comments.
- `comment_length_stats.json`: Statistics related to comment lengths.
- `clustering_results.json`: Results of clustering analysis on comments.
- `user_interaction_network.png`: Visualization of user interactions in the comment section.

### Visualizations

- `wordcloud.png`: Word cloud of the most frequent keywords in comments.
- `sentiment_distribution.png`: Bar chart showing the distribution of comment sentiments.
- `emotion_distribution.png`: Bar chart showing the distribution of emotions.
- `comment_timeline.png`: Line chart showing the timeline of comments over time.
- `sentiment_trends.png`: Line chart showing sentiment trends over time.

### Example Output

Upon running the script and providing a YouTube video URL, the program will output several files, including sentiment analysis results, topic modeling results, and various visualizations like sentiment distribution and user interaction networks.

### Additional Notes

- **Comment Limit**: The tool retrieves up to 1000 comments by default, but you can modify this by adjusting the `max_comments` parameter in the script.
- **Data Preprocessing**: The text is preprocessed by removing URLs, user mentions, hashtags, and extra spaces to ensure cleaner text for analysis.
- **Sentiment and Emotion Analysis**: Sentiment analysis is performed using a pre-trained sentiment analysis model from Hugging Face, and emotion detection is done using another Hugging Face model for emotion classification.

## License

This project is licensed under the MIT License - see the LICENSE file for details.