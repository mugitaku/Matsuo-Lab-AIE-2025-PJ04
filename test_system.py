import json
import time
from clustering import QuestionClusterer
from summarizer import QuestionSummarizer

def test_clustering():
    """クラスタリング機能のテスト"""
    print("=== クラスタリング機能のテスト ===")
    
    # サンプルデータの読み込み
    with open('sample_questions.json', 'r', encoding='utf-8') as f:
        questions = json.load(f)
    
    # クラスタリングの実行
    clusterer = QuestionClusterer(similarity_threshold=0.7)
    start_time = time.time()
    clusters = clusterer.cluster_questions(questions[:50])  # 最初の50件でテスト
    end_time = time.time()
    
    print(f"処理時間: {end_time - start_time:.2f}秒")
    print(f"質問数: {len(questions[:50])}")
    print(f"クラスタ数: {len(clusters)}")
    print("\n各クラスタのサイズ:")
    for i, cluster in enumerate(clusters):
        print(f"  クラスタ{i+1}: {cluster['size']}件")
        print(f"    代表質問: {cluster['representative_question']['質問'][:50]}...")
    
    return clusters

def test_summarization(clusters):
    """要約機能のテスト"""
    print("\n=== 要約機能のテスト ===")
    
    # 最大のクラスタを選択
    largest_cluster = max(clusters, key=lambda x: x['size'])
    print(f"最大クラスタ（{largest_cluster['size']}件）の要約を生成")
    
    try:
        summarizer = QuestionSummarizer()
        summary = summarizer.summarize_questions(largest_cluster['questions'])
        
        print("\n要約結果:")
        print(f"要約: {summary['summary']}")
        print("\n重要ポイント:")
        for point in summary.get('key_points', []):
            print(f"  - {point}")
        print(f"\n回答案:\n{summary['answer']}")
        
    except Exception as e:
        print(f"エラー: {e}")
        print("注意: Gemini APIキーが設定されていることを確認してください")

def test_performance():
    """パフォーマンステスト"""
    print("\n=== パフォーマンステスト ===")
    
    # 全データでのテスト
    with open('sample_questions.json', 'r', encoding='utf-8') as f:
        all_questions = json.load(f)
    
    clusterer = QuestionClusterer(similarity_threshold=0.7)
    
    # 異なるデータサイズでテスト
    test_sizes = [100, 200, 500, len(all_questions)]
    
    for size in test_sizes:
        if size > len(all_questions):
            continue
        
        start_time = time.time()
        clusters = clusterer.cluster_questions(all_questions[:size])
        end_time = time.time()
        
        print(f"質問数 {size}: {end_time - start_time:.2f}秒 (クラスタ数: {len(clusters)})")

if __name__ == "__main__":
    print("講義質疑応答まとめシステム - テスト実行\n")
    
    # クラスタリングテスト
    clusters = test_clustering()
    
    # 要約テスト（Gemini APIキーが必要）
    test_summarization(clusters)
    
    # パフォーマンステスト
    test_performance()