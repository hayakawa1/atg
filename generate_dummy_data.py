from app import app, db
from models import User, Post, Tag
from datetime import datetime, timedelta
import random

# 基本の会話パターン
base_conversations = [
    {
        "content": "ChatGPTに「僕の親友になって」と言ったら、すごく温かい返事が返ってきて感動しました😊",
        "tags": ["心温まる", "友情", "感動"]
    },
    {
        "content": "「好きな食べ物は？」と聞いたら「私はデータなので食べ物を食べることはできませんが、みなさんの美味しそうな話を聞くのが大好きです」って返してきて笑いました😂",
        "tags": ["ユーモア", "食べ物", "笑える"]
    },
    {
        "content": "「最近疲れているんだ」と言ったら、めっちゃ詳しく疲労回復法を教えてくれて、最後に「あなたの健康が一番大切です」って。なんか嬉しかった🥹",
        "tags": ["癒し", "アドバイス", "優しい"]
    },
    {
        "content": "「好きな人に告白したいんだけど」って相談したら、めっちゃ真剣に考えてくれて、素敵なアドバイスをくれました💕",
        "tags": ["恋愛", "アドバイス", "応援"]
    },
    {
        "content": "「今日は雨だね」って言ったら「雨の日は家で本を読むのが素敵ですよね。でも私は濡れても大丈夫です（笑）」って返してきて可愛かった☔️",
        "tags": ["ユーモア", "日常", "癒し"]
    }
]

# 追加の会話パターン
more_patterns = [
    {
        "content": "「人生について教えて」って聞いたら、哲学的な話から実践的なアドバイスまでしてくれて感動😌",
        "tags": ["深い", "アドバイス", "感動"]
    },
    {
        "content": "「面白い話して」って言ったら、即興で素敵なストーリーを作ってくれました📚",
        "tags": ["物語", "創造性", "楽しい"]
    },
    {
        "content": "「今日は調子が悪いんだ」って言ったら、すごく親身になって話を聞いてくれて癒されました😊",
        "tags": ["癒し", "優しい", "心温まる"]
    },
    {
        "content": "「夢を叶える方法を教えて」って相談したら、具体的なステップまで考えてくれて感激です✨",
        "tags": ["夢", "アドバイス", "応援"]
    },
    {
        "content": "「一緒に歌を作ろう」って提案したら、素敵な歌詞を考えてくれて楽しかった🎵",
        "tags": ["音楽", "創造性", "楽しい"]
    }
]

# 感情を表す絵文字リスト
emotions = ["😊", "😂", "🥹", "💕", "☺️", "😌", "🥰", "😄", "😃", "😆", "🤗", "✨", "💫", "🌟", "⭐️", "💝", "💖", "💓", "💗", "💞"]

def generate_variations(base_content, count=20):
    variations = []
    templates = [
        "ChatGPTに{}と聞いてみたら、{}返ってきました",
        "「{}」って話しかけたら、「{}」って返してくれました",
        "{}って相談したら、{}って言ってくれて嬉しかった",
        "「{}」って言ったら、「{}」という返事が返ってきて面白かった",
        "{}について話したら、{}という返事が返ってきて感動"
    ]
    
    for _ in range(count):
        template = random.choice(templates)
        emotion = random.choice(emotions)
        content = template.format(
            random.choice([
                "「どう思う？」", "「教えて」", "「聞かせて」", "「話して」",
                "「アドバイスして」", "「相談したい」", "「どうすれば？」"
            ]),
            random.choice([
                "とても親身に", "楽しく", "面白く", "優しく", "丁寧に",
                "ユーモアたっぷりに", "温かく", "真剣に", "熱心に"
            ])
        ) + emotion
        variations.append(content)
    
    return variations

def generate_dummy_data():
    # データベースをリセット
    db.drop_all()
    db.create_all()
    
    # テストユーザーを作成
    users = []
    for i in range(5):
        user = User(
            google_id=f"dummy_id_{i}",
            email=f"test{i}@example.com",
            name=f"テストユーザー{i+1}",
            profile_pic=f"https://api.dicebear.com/7.x/avataaars/svg?seed=test{i}"
        )
        db.session.add(user)
        users.append(user)
    db.session.commit()
    
    # タグの準備
    all_tags = set()
    for conv in base_conversations + more_patterns:
        all_tags.update(conv["tags"])
    
    tag_objects = {}
    for tag_name in all_tags:
        tag = Tag(name=tag_name)
        db.session.add(tag)
        tag_objects[tag_name] = tag
    
    # 投稿を作成（200件）
    base_time = datetime.utcnow() - timedelta(days=30)
    all_conversations = base_conversations + more_patterns
    
    for i in range(200):
        # ベースとなる会話をランダムに選択
        conv = random.choice(all_conversations)
        
        # 投稿を作成
        post = Post(
            user_id=random.choice(users).id,
            content=random.choice([
                conv["content"],
                *generate_variations(conv["content"], 1)
            ]),
            url=f"https://chat.openai.com/share/dummy-conversation-{i+1}",
            created_at=base_time + timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            ),
            ip_address="127.0.0.1"
        )
        
        # タグを追加（基本のタグ + ランダムな追加タグ）
        used_tags = set(conv["tags"])
        if random.random() < 0.3:  # 30%の確率で追加のタグを付ける
            additional_tags = random.sample(list(all_tags - used_tags), k=random.randint(1, 2))
            used_tags.update(additional_tags)
        
        for tag_name in used_tags:
            post.tags.append(tag_objects[tag_name])
        
        db.session.add(post)
    
    db.session.commit()
    print("200件のダミーデータの生成が完了しました！")

if __name__ == "__main__":
    with app.app_context():
        generate_dummy_data()
