import os
import google.generativeai as genai
from dotenv import load_dotenv
import json

# 環境変数の読み込み
load_dotenv()

class QuestionSummarizer:
    def __init__(self):
        """質問の要約と回答生成を行うクラス"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY が設定されていません。.env ファイルを確認してください。")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def summarize_questions(self, questions):
        """
        質問群を要約し、回答案を生成する
        
        Args:
            questions: 質問データのリスト
        
        Returns:
            要約と回答案を含む辞書
        """
        if not questions:
            return {
                'summary': '',
                'answer': '',
                'key_points': []
            }
        
        # 質問テキストを抽出
        question_texts = [q.get('質問', '') for q in questions if q.get('質問')]
        
        # プロンプトの作成
        prompt = self._create_summarization_prompt(question_texts)
        
        try:
            # Gemini APIで処理
            response = self.model.generate_content(prompt)
            
            # レスポンスをパース
            result = self._parse_response(response.text)
            
            # 質問数などのメタデータを追加
            result['question_count'] = len(questions)
            result['original_questions'] = questions
            
            return result
        
        except Exception as e:
            print(f"Gemini API エラー: {e}")
            return {
                'summary': '要約の生成に失敗しました',
                'answer': '回答の生成に失敗しました',
                'key_points': [],
                'error': str(e)
            }
    
    def _create_summarization_prompt(self, question_texts):
        """要約用のプロンプトを作成"""
        questions_str = '\n'.join([f"- {q}" for q in question_texts])
        
        prompt = f"""以下は大規模言語モデル（LLM）に関する講義で受講生から寄せられた質問群です。
これらの質問を分析し、講師が効率的に回答できるよう要約してください。

【質問一覧】
{questions_str}

【タスク】
1. これらの質問の共通テーマや主要な疑問点を要約してください
2. 講師が回答すべき重要なポイントを3-5個挙げてください
3. これらの質問に対する包括的な回答案を作成してください

【出力形式】
以下のJSON形式で出力してください：
{{
    "summary": "質問群の要約（1-2文）",
    "key_points": ["ポイント1", "ポイント2", "ポイント3"],
    "answer": "包括的な回答案（3-5文程度）",
    "additional_notes": "講師への補足情報（任意）"
}}

必ずJSON形式で出力し、コードブロックなどは使用しないでください。"""
        
        return prompt
    
    def _parse_response(self, response_text):
        """Geminiのレスポンスをパース"""
        try:
            # JSON形式でパース
            result = json.loads(response_text)
            
            # 必須フィールドの確認と初期値設定
            return {
                'summary': result.get('summary', ''),
                'key_points': result.get('key_points', []),
                'answer': result.get('answer', ''),
                'additional_notes': result.get('additional_notes', '')
            }
        
        except json.JSONDecodeError:
            # JSONパースに失敗した場合は、テキストを直接使用
            return {
                'summary': response_text[:200] + '...' if len(response_text) > 200 else response_text,
                'key_points': [],
                'answer': response_text,
                'additional_notes': ''
            }
    
    def generate_detailed_answer(self, questions, context=None):
        """
        より詳細な回答を生成（講義資料などのコンテキストを考慮）
        
        Args:
            questions: 質問データのリスト
            context: 追加のコンテキスト情報（講義資料など）
        
        Returns:
            詳細な回答
        """
        question_texts = [q.get('質問', '') for q in questions if q.get('質問')]
        
        prompt = f"""以下の質問に対して、大規模言語モデル（LLM）の専門家として詳細に回答してください。

【質問】
{chr(10).join([f"- {q}" for q in question_texts])}

{"【追加コンテキスト】" + context if context else ""}

【回答要件】
- 技術的に正確であること
- 初学者にも理解しやすい説明を心がけること
- 具体例を交えること
- 必要に応じて参考資料を提示すること

回答:"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"回答の生成に失敗しました: {str(e)}"