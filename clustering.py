import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import AgglomerativeClustering
import re

class QuestionClusterer:
    def __init__(self, similarity_threshold=0.7):
        """
        質問のクラスタリングを行うクラス
        
        Args:
            similarity_threshold: 類似度の閾値（0-1）
        """
        self.similarity_threshold = similarity_threshold
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 2),
            min_df=1,
            stop_words=None  # 日本語のストップワードは別途処理
        )
    
    def preprocess_text(self, text):
        """テキストの前処理"""
        if not text:
            return ""
        
        # 改行を空白に置換
        text = text.replace('\n', ' ')
        
        # 連続する空白を1つに
        text = re.sub(r'\s+', ' ', text)
        
        # 前後の空白を削除
        text = text.strip()
        
        return text
    
    def cluster_questions(self, questions):
        """
        質問をクラスタリングする
        
        Args:
            questions: 質問データのリスト（各要素は辞書形式）
        
        Returns:
            クラスタリング結果
        """
        if not questions:
            return []
        
        # 質問テキストを抽出して前処理
        question_texts = [self.preprocess_text(q.get('質問', '')) for q in questions]
        
        # 単一の質問の場合は1つのクラスタとして返す
        if len(question_texts) <= 1:
            return [{
                'cluster_id': 0,
                'questions': questions,
                'size': len(questions),
                'representative_question': questions[0] if questions else None
            }]
        
        # TF-IDFベクトル化
        try:
            tfidf_matrix = self.vectorizer.fit_transform(question_texts)
        except ValueError:
            # ベクトル化に失敗した場合は全て別クラスタとする
            return [
                {
                    'cluster_id': i,
                    'questions': [q],
                    'size': 1,
                    'representative_question': q
                }
                for i, q in enumerate(questions)
            ]
        
        # コサイン類似度の計算
        similarity_matrix = cosine_similarity(tfidf_matrix)
        
        # 階層的クラスタリング
        # 類似度を距離に変換（1 - similarity）
        distance_matrix = 1 - similarity_matrix
        
        clustering = AgglomerativeClustering(
            n_clusters=None,
            distance_threshold=1 - self.similarity_threshold,
            linkage='average',
            metric='precomputed'
        )
        
        cluster_labels = clustering.fit_predict(distance_matrix)
        
        # クラスタごとに質問をグループ化
        clusters = {}
        for idx, label in enumerate(cluster_labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(idx)
        
        # 結果を整形
        result = []
        for cluster_id, question_indices in clusters.items():
            cluster_questions = [questions[i] for i in question_indices]
            
            # 代表的な質問を選択（最も他の質問との類似度が高いもの）
            if len(question_indices) > 1:
                # クラスタ内の類似度の平均を計算
                avg_similarities = []
                for i in question_indices:
                    sim_sum = sum(similarity_matrix[i][j] for j in question_indices if i != j)
                    avg_similarities.append(sim_sum / (len(question_indices) - 1))
                
                best_idx = question_indices[np.argmax(avg_similarities)]
                representative = questions[best_idx]
            else:
                representative = cluster_questions[0]
            
            result.append({
                'cluster_id': int(cluster_id),
                'questions': cluster_questions,
                'size': len(cluster_questions),
                'representative_question': representative
            })
        
        # サイズの大きい順にソート
        result.sort(key=lambda x: x['size'], reverse=True)
        
        return result
    
    def get_cluster_keywords(self, cluster_questions):
        """
        クラスタの主要キーワードを抽出
        
        Args:
            cluster_questions: クラスタ内の質問リスト
        
        Returns:
            主要キーワードのリスト
        """
        texts = [self.preprocess_text(q.get('質問', '')) for q in cluster_questions]
        combined_text = ' '.join(texts)
        
        # TF-IDFで重要な単語を抽出
        try:
            tfidf_matrix = self.vectorizer.fit_transform([combined_text])
            feature_names = self.vectorizer.get_feature_names_out()
            tfidf_scores = tfidf_matrix.toarray()[0]
            
            # スコアの高い順にソート
            top_indices = np.argsort(tfidf_scores)[::-1][:10]
            keywords = [feature_names[i] for i in top_indices if tfidf_scores[i] > 0]
            
            return keywords
        except:
            return []