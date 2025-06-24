from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
from clustering import QuestionClusterer
from summarizer import QuestionSummarizer

app = Flask(__name__)
CORS(app)

# 初期化
clusterer = QuestionClusterer()
summarizer = QuestionSummarizer()

@app.route('/')
def index():
    """メインページの表示"""
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_questions():
    """質問データのアップロード"""
    try:
        data = request.json
        questions = data.get('questions', [])
        
        # クラスタリング実行
        clusters = clusterer.cluster_questions(questions)
        
        # 結果を保存
        result = {
            'timestamp': datetime.now().isoformat(),
            'total_questions': len(questions),
            'clusters': clusters
        }
        
        return jsonify({
            'success': True,
            'data': result
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/summarize', methods=['POST'])
def summarize_cluster():
    """クラスタの要約と回答生成"""
    try:
        data = request.json
        cluster_questions = data.get('questions', [])
        
        # 要約と回答生成
        summary = summarizer.summarize_questions(cluster_questions)
        
        return jsonify({
            'success': True,
            'data': summary
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/sample-data')
def get_sample_data():
    """サンプルデータの取得"""
    try:
        with open('sample_questions.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return jsonify({
            'success': True,
            'data': data
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)