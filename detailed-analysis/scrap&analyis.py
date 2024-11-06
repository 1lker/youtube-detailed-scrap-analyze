import os
import re
import json
from collections import Counter
from googleapiclient.discovery import build
from dotenv import load_dotenv
from datetime import datetime

# Çevresel değişkenleri yükle
load_dotenv()

def get_youtube_service():
    """YouTube API istemcisini başlat."""
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        raise ValueError("Error: YouTube API key not found in .env file")
    youtube = build('youtube', 'v3', developerKey=api_key)
    return youtube

def extract_video_id(youtube_url):
    """YouTube veya YouTube Shorts URL'sinden video ID'sini çıkar."""
    # Hem klasik YouTube hem de Shorts URL formatlarını kapsayan bir regex deseni
    match = re.search(r'(?:v=|\/shorts\/|\/watch\/|\/embed\/)([a-zA-Z0-9_-]+)', youtube_url)
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

def calculate_video_statistics(metadata):
    """Video metadata bilgilerine dayalı istatistiksel skorlar hesaplar."""
    view_count = metadata['view_count']
    like_count = metadata['like_count']
    comment_count = metadata['comment_count']
    
    # Yayınlanma tarihinden geçen gün sayısı
    publish_date = datetime.strptime(metadata['publish_date'], "%Y-%m-%dT%H:%M:%SZ")
    days_since_published = (datetime.now() - publish_date).days

    # Skor hesaplamaları
    engagement_rate = (like_count + comment_count) / view_count * 100 if view_count > 0 else 0
    like_view_ratio = like_count / view_count * 100 if view_count > 0 else 0
    comment_like_ratio = comment_count / like_count * 100 if like_count > 0 else 0
    popularity_score = like_count + comment_count
    like_growth_rate = like_count / (days_since_published + 1)
    comment_growth_rate = comment_count / (days_since_published + 1)
    success_score = (view_count * 0.5) + (like_count * 0.3) + (comment_count * 0.2)
    engagement_depth = comment_count / (like_count + comment_count) * 100 if (like_count + comment_count) > 0 else 0
    reach_ratio = (like_count + comment_count) / view_count * 100 if view_count > 0 else 0
    intensity_score = (like_count + comment_count) / (days_since_published + 1)

    # Yeni Eklenen Skorlar
    engagement_per_day = (like_count + comment_count) / (days_since_published + 1)
    comprehensive_intensity_score = (view_count + like_count + comment_count) / (days_since_published + 1)

    statistics = {
        'engagement_rate': round(engagement_rate, 2),
        'like_view_ratio': round(like_view_ratio, 2),
        'comment_like_ratio': round(comment_like_ratio, 2),
        'popularity_score': popularity_score,
        'like_growth_rate': round(like_growth_rate, 2),
        'comment_growth_rate': round(comment_growth_rate, 2),
        'success_score': round(success_score, 2),
        'engagement_depth': round(engagement_depth, 2),
        'reach_ratio': round(reach_ratio, 2),
        'intensity_score': round(intensity_score, 2),
        'engagement_per_day': round(engagement_per_day, 2),
        'comprehensive_intensity_score': round(comprehensive_intensity_score, 2)
    }
    return statistics

def save_metadata_to_json(metadata):
    """Video metadata bilgilerini JSON dosyasına kaydeder."""
    with open('video_metadata.json', 'w', encoding='utf-8') as json_file:
        json.dump(metadata, json_file, ensure_ascii=False, indent=4)

def save_statistics_to_json(statistics):
    """Video istatistik sonuçlarını JSON dosyasına kaydeder."""
    with open('video_statistics.json', 'w', encoding='utf-8') as json_file:
        json.dump(statistics, json_file, ensure_ascii=False, indent=4)

def main():
    youtube_url = input("YouTube Video URL'sini girin: ")
    youtube = get_youtube_service()
    video_id = extract_video_id(youtube_url)
    
    # 1. Video Metadata Analizi
    metadata = get_video_metadata(video_id, youtube)
    save_metadata_to_json(metadata)
    print("Video metadata bilgileri 'video_metadata.json' dosyasına kaydedildi.")

    # 2. Video İstatistik Analizi
    statistics = calculate_video_statistics(metadata)
    save_statistics_to_json(statistics)
    print("Video istatistikleri 'video_statistics.json' dosyasına kaydedildi.")

if __name__ == "__main__":
    main()