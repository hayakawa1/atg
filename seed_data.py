from app import app, db
from models import User, Post, Tag
from datetime import datetime, timedelta
import random

def seed_data():
    with app.app_context():
        # データベースをクリア
        db.drop_all()
        db.create_all()

        # テストユーザーの作成
        user = User(
            name="Test User",
            email="test@example.com",
            profile_pic="https://via.placeholder.com/150"
        )
        db.session.add(user)
        db.session.commit()

        # タグの作成
        tag_names = ["面白い", "学び", "感動", "技術", "アイデア", "雑談", "質問", "回答", "プログラミング", "AI", "未来", "考察"]
        tags = [Tag(name=name) for name in tag_names]
        for tag in tags:
            db.session.add(tag)
        db.session.commit()

        # 投稿の作成（200件）
        contents = [
            "ChatGPTとの面白い会話",
            "プログラミングについての深い議論",
            "AIの未来について",
            "技術的な質問への回答",
            "興味深い考察",
            "驚きの発見",
            "学びのある対話",
            "感動的なやり取り"
        ]

        for i in range(200):
            # ランダムな内容を選択
            content = f"{random.choice(contents)} #{i+1}"
            # ランダムな日時を生成（過去30日以内）
            created_at = datetime.utcnow() - timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            post = Post(
                content=content,
                url=f"https://chat.openai.com/c/{i+1}",
                user_id=user.id,
                created_at=created_at,
                favorite_count=random.randint(0, 50)
            )
            
            # ランダムにタグを2-4個付与
            selected_tags = random.sample(tags, random.randint(2, 4))
            post.tags.extend(selected_tags)
            
            db.session.add(post)

        db.session.commit()
        print("Test data has been seeded successfully!")

if __name__ == "__main__":
    seed_data() 