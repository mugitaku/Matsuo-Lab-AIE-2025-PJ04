// グローバル変数
let currentData = null;
let currentClusters = null;
let selectedCluster = null;

// DOMが読み込まれたら初期化
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
});

// イベントリスナーの初期化
function initializeEventListeners() {
    document.getElementById('loadSampleBtn').addEventListener('click', loadSampleData);
    document.getElementById('uploadBtn').addEventListener('click', () => {
        document.getElementById('fileInput').click();
    });
    document.getElementById('fileInput').addEventListener('change', handleFileUpload);
    document.getElementById('copyAnswerBtn').addEventListener('click', copyAnswer);
    document.getElementById('regenerateBtn').addEventListener('click', regenerateAnswer);
}

// サンプルデータの読み込み
async function loadSampleData() {
    showLoadingStatus('サンプルデータを読み込んでいます...');
    
    try {
        const response = await fetch('/api/sample-data');
        const result = await response.json();
        
        if (result.success) {
            currentData = result.data;
            processQuestions(currentData);
            showSuccessStatus('サンプルデータを読み込みました');
        } else {
            showErrorStatus('データの読み込みに失敗しました');
        }
    } catch (error) {
        console.error('Error:', error);
        showErrorStatus('エラーが発生しました');
    }
}

// ファイルアップロードの処理
async function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    showLoadingStatus('ファイルを処理しています...');
    
    // ここでは簡易的にJSONファイルのみ対応
    if (file.name.endsWith('.json')) {
        const reader = new FileReader();
        reader.onload = function(e) {
            try {
                const data = JSON.parse(e.target.result);
                currentData = data;
                processQuestions(data);
                showSuccessStatus('ファイルを読み込みました');
            } catch (error) {
                showErrorStatus('ファイルの読み込みに失敗しました');
            }
        };
        reader.readAsText(file);
    } else {
        showErrorStatus('現在はJSONファイルのみ対応しています');
    }
}

// 質問データの処理とクラスタリング
async function processQuestions(questions) {
    const startTime = performance.now();
    
    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ questions: questions })
        });
        
        const result = await response.json();
        
        if (result.success) {
            currentClusters = result.data.clusters;
            const endTime = performance.now();
            const processingTime = ((endTime - startTime) / 1000).toFixed(2);
            
            // 統計情報の更新
            document.getElementById('totalQuestions').textContent = result.data.total_questions;
            document.getElementById('clusterCount').textContent = currentClusters.length;
            document.getElementById('processingTime').textContent = `${processingTime}秒`;
            
            // クラスタ一覧の表示
            displayClusters(currentClusters);
            
            // メインコンテンツを表示
            document.getElementById('mainContent').style.display = 'flex';
        } else {
            showErrorStatus('クラスタリングに失敗しました');
        }
    } catch (error) {
        console.error('Error:', error);
        showErrorStatus('エラーが発生しました');
    }
}

// クラスタ一覧の表示
function displayClusters(clusters) {
    const clusterList = document.getElementById('clusterList');
    clusterList.innerHTML = '';
    
    clusters.forEach((cluster, index) => {
        const clusterItem = document.createElement('div');
        clusterItem.className = 'cluster-item';
        clusterItem.innerHTML = `
            <strong>クラスタ ${index + 1}</strong>
            <span class="cluster-size">${cluster.size}件</span>
            <div style="clear: both;"></div>
            <small class="text-muted">${cluster.representative_question.質問.substring(0, 50)}...</small>
        `;
        
        clusterItem.addEventListener('click', () => selectCluster(cluster, index));
        clusterList.appendChild(clusterItem);
    });
}

// クラスタの選択
async function selectCluster(cluster, index) {
    selectedCluster = cluster;
    
    // アクティブ状態の更新
    document.querySelectorAll('.cluster-item').forEach((item, i) => {
        item.classList.toggle('active', i === index);
    });
    
    // クラスタ詳細の表示
    displayClusterDetail(cluster);
    
    // 要約の生成
    await generateSummary(cluster);
}

// クラスタ詳細の表示
function displayClusterDetail(cluster) {
    const detailDiv = document.getElementById('clusterDetail');
    
    let html = `
        <h5>クラスタ内の質問 (${cluster.size}件)</h5>
        <div style="max-height: 400px; overflow-y: auto;">
    `;
    
    cluster.questions.forEach((q, index) => {
        html += `
            <div class="question-item">
                <div class="question-timestamp">${q.タイムスタンプ}</div>
                <div class="mt-2">${q.質問}</div>
                ${q.回答 ? `<div class="mt-2 text-success"><strong>既存の回答:</strong> ${q.回答}</div>` : ''}
            </div>
        `;
    });
    
    html += '</div>';
    detailDiv.innerHTML = html;
}

// 要約の生成
async function generateSummary(cluster) {
    document.getElementById('summaryCard').style.display = 'block';
    document.getElementById('summaryContent').innerHTML = '<div class="text-center"><div class="loading-spinner"></div> 要約を生成中...</div>';
    
    try {
        const response = await fetch('/api/summarize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ questions: cluster.questions })
        });
        
        const result = await response.json();
        
        if (result.success) {
            displaySummary(result.data);
        } else {
            document.getElementById('summaryContent').innerHTML = '<p class="text-danger">要約の生成に失敗しました</p>';
        }
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('summaryContent').innerHTML = '<p class="text-danger">エラーが発生しました</p>';
    }
}

// 要約の表示
function displaySummary(summary) {
    document.getElementById('questionSummary').textContent = summary.summary || '要約なし';
    
    const keyPointsList = document.getElementById('keyPoints');
    keyPointsList.innerHTML = '';
    (summary.key_points || []).forEach(point => {
        const li = document.createElement('li');
        li.textContent = point;
        keyPointsList.appendChild(li);
    });
    
    document.getElementById('suggestedAnswer').innerHTML = (summary.answer || '回答なし').replace(/\n/g, '<br>');
    
    // ボタンを再表示
    document.getElementById('summaryContent').innerHTML = document.getElementById('summaryCard').querySelector('.card-body').innerHTML;
}

// 回答の再生成
async function regenerateAnswer() {
    if (!selectedCluster) return;
    await generateSummary(selectedCluster);
}

// 回答のコピー
function copyAnswer() {
    const answerText = document.getElementById('suggestedAnswer').textContent;
    navigator.clipboard.writeText(answerText).then(() => {
        showSuccessStatus('回答をクリップボードにコピーしました');
    }).catch(err => {
        showErrorStatus('コピーに失敗しました');
    });
}

// ステータス表示関数
function showLoadingStatus(message) {
    const statusDiv = document.getElementById('loadStatus');
    statusDiv.className = 'alert alert-info';
    statusDiv.innerHTML = `<div class="loading-spinner" style="margin-right: 10px;"></div> ${message}`;
    statusDiv.style.display = 'block';
}

function showSuccessStatus(message) {
    const statusDiv = document.getElementById('loadStatus');
    statusDiv.className = 'alert alert-success';
    statusDiv.textContent = message;
    statusDiv.style.display = 'block';
    setTimeout(() => {
        statusDiv.style.display = 'none';
    }, 3000);
}

function showErrorStatus(message) {
    const statusDiv = document.getElementById('loadStatus');
    statusDiv.className = 'alert alert-danger';
    statusDiv.textContent = message;
    statusDiv.style.display = 'block';
    setTimeout(() => {
        statusDiv.style.display = 'none';
    }, 5000);
}