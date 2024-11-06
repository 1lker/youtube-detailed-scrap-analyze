import os
import re
import json
from collections import Counter
from googleapiclient.discovery import build
import pandas as pd
from dotenv import load_dotenv
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

# Çevresel değişkenleri yükle
load_dotenv()

# Hugging Face modeli için duygusal analiz
sentiment_analyzer = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")

MAX_TOKENS = 512

def get_youtube_service():
    """YouTube API istemcisini başlat."""
    if not api_key:
        raise ValueError("Error: YouTube API key not found in .env file")
    youtube = build('youtube', 'v3', developerKey=api_key)
    return youtube

def extract_video_id(youtube_url):
    """YouTube URL'sinden video ID'sini çıkar."""
    match = re.search(r'v=([a-zA-Z0-9_-]+)', youtube_url)
    if not match:
        raise ValueError("Geçersiz YouTube URL'si. Lütfen doğru bir URL girin.")
    return match.group(1)

def get_video_metadata(video_id, youtube):
    """Belirli bir video hakkında geniş metadata al."""
    response = youtube.videos().list(
        part="snippet,contentDetails,statistics,status,topicDetails,liveStreamingDetails",
        id=video_id
    ).execute()

    if not response['items']:
        raise ValueError("Bu ID ile eşleşen video bulunamadı.")
    
    video_data = response['items'][0]
    metadata = {
        'video_id': video_id,
        'title': video_data['snippet']['title'],
        'description': video_data['snippet']['description'],
        'tags': video_data['snippet'].get('tags', []),
        'channel_title': video_data['snippet']['channelTitle'],
        'channel_id': video_data['snippet']['channelId'],
        'publish_date': video_data['snippet']['publishedAt'],
        'thumbnail_url': video_data['snippet']['thumbnails']['high']['url'],
        'view_count': int(video_data['statistics'].get('viewCount', 0)),
        'like_count': int(video_data['statistics'].get('likeCount', 0)),
        'comment_count': int(video_data['statistics'].get('commentCount', 0)),
        'duration': video_data['contentDetails']['duration'],
        'licensed_content': video_data['contentDetails'].get('licensedContent', False),
        'privacy_status': video_data['status']['privacyStatus'],
        'embeddable': video_data['status']['embeddable'],
        'public_stats_viewable': video_data['status']['publicStatsViewable'],
        'category_id': video_data['snippet'].get('categoryId', None),
        'topic_categories': video_data.get('topicDetails', {}).get('topicCategories', []),
        'live_broadcast': video_data.get('liveStreamingDetails', {}).get('actualStartTime', None),
        'default_language': video_data['snippet'].get('defaultLanguage')
    }
    return metadata

def truncate_text(text, max_tokens=MAX_TOKENS):
    """Yorum metnini belirli bir token uzunluğuna kısaltır."""
    tokenizer = AutoTokenizer.from_pretrained("nlptown/bert-base-multilingual-uncased-sentiment")
    tokens = tokenizer.encode(text, truncation=True, max_length=max_tokens)
    return tokenizer.decode(tokens, skip_special_tokens=True)

def get_comment_sentiments(video_id, youtube, max_comments=100):
    """Yorumları analiz ederek duygusal dağılım, anahtar kelimeler ve en aktif kullanıcıları bulur."""
    comments = []
    sentiment_counts = Counter()
    active_users = Counter()
    key_phrases = Counter()
    
    next_page_token = None

    while len(comments) < max_comments:
        response = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            textFormat="plainText",
            maxResults=min(max_comments - len(comments), 100),
            pageToken=next_page_token
        ).execute()

        for item in response.get('items', []):
            comment_text = item['snippet']['topLevelComment']['snippet']['textDisplay']
            truncated_text = truncate_text(comment_text)
            author = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
            like_count = item['snippet']['topLevelComment']['snippet']['likeCount']
            published_at = item['snippet']['topLevelComment']['snippet']['publishedAt']

            # Sentiment analizi
            sentiment = sentiment_analyzer(truncated_text)[0]
            sentiment_counts[sentiment['label']] += 1

            # Anahtar kelime analizi (tüm kelimeleri kaydeder)
            for word in truncated_text.split():
                if len(word) > 3:
                    key_phrases[word.lower()] += 1

            # Aktif kullanıcılar
            active_users[author] += 1

            # Yorum kaydı
            comments.append({
                'comment_text': comment_text,
                'author': author,
                'like_count': like_count,
                'published_at': published_at,
                'sentiment': sentiment['label']
            })

        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

    # En sık kullanılan 10 anahtar kelime
    top_keywords = key_phrases.most_common(10)
    # En aktif 5 kullanıcı
    top_active_users = active_users.most_common(5)

    return comments, dict(sentiment_counts), top_keywords, top_active_users

def save_metadata_to_json(metadata):
    """Video metadata bilgilerini JSON dosyasına kaydeder."""
    with open('video_metadata.json', 'w', encoding='utf-8') as json_file:
        json.dump(metadata, json_file, ensure_ascii=False, indent=4)

def save_sentiment_analysis_to_json(comments, sentiment_counts, top_keywords, top_active_users):
    """Sentiment analiz sonuçlarını JSON dosyasına kaydeder."""
    data = {
        'comments': comments,
        'sentiment_distribution': sentiment_counts,
        'top_keywords': top_keywords,
        'top_active_users': top_active_users
    }
    with open('sentiment_analysis.json', 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

def main():
    youtube_url = input("YouTube Video URL'sini girin: ")
    youtube = get_youtube_service()
    video_id = extract_video_id(youtube_url)
    
    # 1. Video Metadata Analizi
    metadata = get_video_metadata(video_id, youtube)
    save_metadata_to_json(metadata)
    print("Video metadata bilgileri 'video_metadata.json' dosyasına kaydedildi.")

    # 2. Sentiment Analizi
    comments, sentiment_counts, top_keywords, top_active_users = get_comment_sentiments(video_id, youtube, max_comments=100)
    save_sentiment_analysis_to_json(comments, sentiment_counts, top_keywords, top_active_users)
    print("Sentiment analiz sonuçları 'sentiment_analysis.json' dosyasına kaydedildi.")

if __name__ == "__main__":
    main()