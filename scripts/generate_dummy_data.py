import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User, Post, Tag, Favorite
from datetime import datetime, timedelta
import random
from faker import Faker

fake = Faker(['ja_JP'])

def generate_dummy_data():
    with app.app_context():
        # データベースをクリア
        db.drop_all()
        db.create_all()
        
        print("Generating users...")
        users = []
        for i in range(10):
            user = User(
                google_id=f"dummy_google_id_{i}",
                email=f"user{i}@example.com",
                name=fake.name(),
                profile_pic=f"https://api.dicebear.com/6.x/avataaars/svg?seed=user{i}",
                created_at=fake.date_time_between(start_date='-30d', end_date='now')
            )
            users.append(user)
            db.session.add(user)
        db.session.commit()
        
        print("Generating tags...")
        tags = []
        tag_names = [
            "面白い", "驚き", "感動", "学び", "技術", "アイデア",
            "哲学", "ユーモア", "考察", "発見", "質問", "回答",
            "議論", "雑談", "アドバイス", "経験談"
        ]
        for tag_name in tag_names:
            tag = Tag(name=tag_name)
            tags.append(tag)
            db.session.add(tag)
        db.session.commit()
        
        print("Generating posts...")
        posts = []
        conversation_starters = [
            "ChatGPTに「{0}」について聞いてみました",
            "AIと{0}の話で盛り上がりました",
            "ChatGPTの{0}に関する回答が興味深かった",
            "AIと{0}について議論してみた結果",
            "ChatGPTに{0}を教えてもらいました"
        ]
        topics = [
            "人生の意味", "幸せの定義", "理想の社会", "未来の技術",
            "宇宙の謎", "人間の本質", "創造性", "感情", "意識",
            "芸術", "音楽", "文学", "科学", "哲学", "歴史",
            "教育", "環境", "経済", "政治", "文化"
        ]
        
        # メインの投稿を生成
        for i in range(100):
            topic = random.choice(topics)
            template = random.choice(conversation_starters)
            content = template.format(topic)
            user = random.choice(users)
            
            post = Post(
                content=content,
                url=f"https://chat.openai.com/share/dummy-conversation-{i}",
                user_id=user.id,
                created_at=fake.date_time_between(start_date='-30d', end_date='now'),
                ip_address=fake.ipv4(),
                favorite_count=0
            )
            
            # ランダムにタグを付ける（1-3個）
            post_tags = random.sample(tags, random.randint(1, 3))
            for tag in post_tags:
                post.tags.append(tag)
            
            posts.append(post)
            db.session.add(post)
        db.session.commit()
        
        # リプライを生成
        print("Generating replies...")
        reply_templates = [
            "確かに{0}は興味深い視点ですね。",
            "私も{0}について考えていました。",
            "この{0}という考え方は新鮮です。",
            "{0}についての議論は大切だと思います。",
            "なるほど、{0}はそういう見方もできるんですね。"
        ]
        
        for i in range(100):
            original_post = random.choice(posts)
            topic = original_post.content.split("「")[-1].split("」")[0] if "「" in original_post.content else "この話題"
            template = random.choice(reply_templates)
            content = template.format(topic)
            user = random.choice(users)
            
            reply = Post(
                content=content,
                url=original_post.url,
                user_id=user.id,
                created_at=fake.date_time_between(start_date=original_post.created_at, end_date='now'),
                ip_address=fake.ipv4(),
                reply_to_id=original_post.id,
                favorite_count=0
            )
            
            # リプライにもタグを付ける（1-2個）
            reply_tags = random.sample(tags, random.randint(1, 2))
            for tag in reply_tags:
                reply.tags.append(tag)
            
            db.session.add(reply)
        db.session.commit()
        
        print("Generating favorites...")
        # いいねを生成
        for post in posts:
            # 各投稿に0-5個のいいねをつける
            for _ in range(random.randint(0, 5)):
                user = random.choice(users)
                # 既にいいねしていない場合のみ追加
                existing_favorite = Favorite.query.filter_by(
                    user_id=user.id,
                    post_id=post.id
                ).first()
                
                if not existing_favorite:
                    favorite = Favorite(
                        user_id=user.id,
                        post_id=post.id,
                        created_at=fake.date_time_between(
                            start_date=post.created_at,
                            end_date='now'
                        )
                    )
                    db.session.add(favorite)
                    post.favorite_count += 1
        
        db.session.commit()
        print("Done!")

if __name__ == "__main__":
    generate_dummy_data() 