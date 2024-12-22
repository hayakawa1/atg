// DOM要素の取得
const postsContainer = document.getElementById('posts');
const newPostModal = document.getElementById('newPostModal');
const newPostForm = document.getElementById('newPostForm');
const postTemplate = document.getElementById('post-template');

// 初期化
document.addEventListener('DOMContentLoaded', () => {
    fetchPosts();
    setupEventListeners();
    fetchPopularTags();
    setupTagClickHandlers();
    setupNavigation();
});

// イベントリスナーの設定
function setupEventListeners() {
    // 新規投稿フォームの送信
    newPostForm?.addEventListener('submit', handleNewPost);

    // 投稿一覧の無限スクロール
    window.addEventListener('scroll', handleScroll);
}

// 投稿の取得
async function fetchPosts(page = 1) {
    try {
        console.log('Fetching posts...'); // デバッグログ
        const response = await fetch(`/api/posts?page=${page}`);
        const data = await response.json();
        console.log('Received data:', data); // デバッグログ
        
        if (page === 1) {
            postsContainer.innerHTML = '';
        }
        
        data.posts.forEach(post => {
            const postElement = createPostElement(post);
            postsContainer.appendChild(postElement);
        });
    } catch (error) {
        console.error('Error fetching posts:', error);
    }
}

// 投稿要素の作成
function createPostElement(post) {
    const template = postTemplate.content.cloneNode(true);
    
    // ユーザー情報
    const avatar = template.querySelector('.avatar');
    avatar.src = post.author.profile_pic;
    avatar.alt = post.author.name;
    
    const username = template.querySelector('.username');
    username.textContent = post.author.name;
    username.style.cursor = 'pointer';  // カーソルをポインターに
    username.addEventListener('click', (e) => {
        e.preventDefault();
        fetchPostsByUser(post.author.id, post.author.name);
    });
    
    template.querySelector('.post-time').textContent = formatDate(post.created_at);
    
    // 投稿内容
    const contentLink = template.querySelector('.content-text');
    contentLink.href = post.url;
    contentLink.textContent = post.content;
    
    // タグ
    const tagsContainer = template.querySelector('.post-tags');
    post.tags.forEach(tag => {
        const tagLink = document.createElement('a');
        tagLink.href = `/tags/${tag}`;
        tagLink.className = 'tag';
        tagLink.textContent = `#${tag}`;
        tagsContainer.appendChild(tagLink);
    });
    
    // カウント
    template.querySelector('.reply-count').textContent = post.replies_count || 0;
    template.querySelector('.like-count').textContent = post.favorite_count || 0;
    
    // 投稿IDを設定
    const article = template.querySelector('article');
    article.dataset.postId = post.id;
    article.addEventListener('click', (e) => {
        // リンクやボタンのクリックは無視
        if (e.target.closest('a, button')) return;
        fetchReplies(post.id, post.content);
    });

    // いいねボタンの初期状態を設定
    const likeBtn = article.querySelector('.like-btn');
    const likeIcon = likeBtn.querySelector('i');
    if (post.is_favorited) {
        likeBtn.classList.add('active');
        likeIcon.textContent = 'favorite';
    } else {
        likeBtn.classList.remove('active');
        likeIcon.textContent = 'favorite_border';
    }
    likeBtn.addEventListener('click', () => toggleLike(post.id));

    // ボタンのイベントリスナー
    setupPostActions(article, post);
    
    return template;
}

// 投稿アクションの設定
function setupPostActions(article, post) {
    const replyBtn = article.querySelector('.reply-btn');
    const deleteBtn = article.querySelector('.delete-btn');
    
    replyBtn?.addEventListener('click', () => showReplyModal(post.id));
    
    // 自分の投稿の場合のみ削除ボタンを表示
    if (post.is_own) {
        deleteBtn.style.display = 'flex';
        deleteBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            showDeleteConfirm(post.id);
        });
    } else {
        deleteBtn.style.display = 'none';
    }
}

// 新規投稿の処理
async function handleNewPost(event) {
    event.preventDefault();
    
    const formData = new FormData(newPostForm);
    const replyToId = formData.get('reply_to_id');
    
    const data = {
        content: formData.get('content'),
        url: formData.get('url'),
        tags: formData.get('tags').split(',').filter(tag => tag.trim()).map(tag => tag.trim())
    };
    
    try {
        let url = '/api/posts';
        if (replyToId) {
            url = `/api/posts/${replyToId}/replies`;
        }
        
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            closeNewPostModal();
            newPostForm.reset();
            fetchPosts();
        }
    } catch (error) {
        console.error('Error creating post:', error);
    }
}

// モーダル制御
function showNewPostModal() {
    newPostModal.style.display = 'block';
}

function closeNewPostModal() {
    const modal = document.getElementById('newPostModal');
    const form = document.getElementById('newPostForm');
    const replyToInput = document.getElementById('reply_to_id');
    
    // フォームをリセット
    form.reset();
    replyToInput.value = '';
    
    // タイトルを元に戻す
    modal.querySelector('h2').textContent = '新規投稿';
    
    // URLフィールドを必須に戻す
    const urlInput = form.querySelector('#url');
    urlInput.required = true;
    
    modal.style.display = 'none';
}

// ユーティリティ関数
function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    
    // 1分未満
    if (diff < 60000) {
        return '今';
    }
    // 1時間未満
    if (diff < 3600000) {
        return `${Math.floor(diff / 60000)}分前`;
    }
    // 24時間未満
    if (diff < 86400000) {
        return `${Math.floor(diff / 3600000)}時間前`;
    }
    // それ以外
    return `${Math.floor(diff / 86400000)}日前`;
}

// 無限スクロール
let currentPage = 1;
let isLoading = false;

function handleScroll() {
    const { scrollTop, scrollHeight, clientHeight } = document.documentElement;
    
    if (scrollTop + clientHeight >= scrollHeight - 100 && !isLoading) {
        isLoading = true;
        currentPage++;
        fetchPosts(currentPage).finally(() => {
            isLoading = false;
        });
    }
}

// モーダルの外側クリックで閉じる
window.addEventListener('click', (event) => {
    if (event.target === newPostModal) {
        closeNewPostModal();
    }
});

// ハッシュタグの取得と表示
async function fetchPopularTags() {
    try {
        const response = await fetch('/api/tags/popular');
        const tags = await response.json();
        displayPopularTags(tags);
    } catch (error) {
        console.error('Error fetching tags:', error);
    }
}

function displayPopularTags(tags) {
    const hashtagsList = document.querySelector('.hashtags-list');
    hashtagsList.innerHTML = '';
    
    tags.forEach(tag => {
        const tagLink = document.createElement('a');
        tagLink.href = '#';  // JavaScriptで処理するのでhrefは#に
        tagLink.className = 'hashtag-item';
        tagLink.innerHTML = `
            <span class="hashtag-name">#${tag.name}</span>
            <span class="hashtag-count">${tag.count}</span>
        `;
        tagLink.addEventListener('click', async (e) => {
            e.preventDefault();
            await fetchPostsByTag(tag.name);
        });
        hashtagsList.appendChild(tagLink);
    });
}

// リプライモーダルの表示
function showReplyModal(postId) {
    const modal = document.getElementById('newPostModal');
    const form = document.getElementById('newPostForm');
    const replyToInput = document.getElementById('reply_to_id');
    
    // リプライ先の投稿IDを設定
    replyToInput.value = postId;
    
    // モーダルのタイトルを変更
    modal.querySelector('h2').textContent = '返信を投稿';
    
    // URLフィールドを任意に
    const urlInput = form.querySelector('#url');
    urlInput.required = false;
    
    modal.style.display = 'block';
}

// いいねの切り替え
async function toggleLike(postId) {
    try {
        const response = await fetch(`/api/posts/${postId}/favorite`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            const article = document.querySelector(`[data-post-id="${postId}"]`);
            const likeBtn = article.querySelector('.like-btn');
            const likeIcon = likeBtn.querySelector('i');
            const likeCount = article.querySelector('.like-count');
            
            if (data.action === 'added') {
                likeBtn.classList.add('active');
                likeIcon.textContent = 'favorite';
            } else {
                likeBtn.classList.remove('active');
                likeIcon.textContent = 'favorite_border';
            }
            likeCount.textContent = data.favorite_count;
        }
    } catch (error) {
        console.error('Error toggling like:', error);
    }
}

// タグクリックのイベントハンドラを追加
function setupTagClickHandlers() {
    document.addEventListener('click', async (event) => {
        const tagLink = event.target.closest('.tag, .hashtag-item');
        if (!tagLink) return;

        event.preventDefault();
        const tagName = tagLink.textContent.replace('#', '').trim().split(' ')[0];
        console.log('Clicked tag:', tagName);
        await fetchPostsByTag(tagName);
    });
}

// タグでフィルタリングされた投稿を取得
async function fetchPostsByTag(tagName) {
    try {
        console.log('Fetching posts for tag:', tagName);
        const response = await fetch(`/api/posts/tag/${encodeURIComponent(tagName)}`);
        if (!response.ok) throw new Error('Failed to fetch posts');
        
        const data = await response.json();
        console.log('Received tag data:', data);
        
        postsContainer.innerHTML = '';
        data.posts.forEach(post => {
            const postElement = createPostElement(post);
            postsContainer.appendChild(postElement);
        });
    } catch (error) {
        console.error('Error fetching posts by tag:', error);
    }
}

// ユーザーの投稿を取得する関数を追加
async function fetchPostsByUser(userId, userName) {
    try {
        console.log('Fetching posts for user:', userName);
        const response = await fetch(`/api/posts/user/${userId}`);
        if (!response.ok) throw new Error('Failed to fetch posts');
        
        const data = await response.json();
        console.log('Received user posts:', data);
        
        // タイトルを更新
        const title = document.querySelector('.content-header h1');
        title.textContent = `${userName}の投稿`;
        
        // 投稿を表示
        postsContainer.innerHTML = '';
        data.posts.forEach(post => {
            const postElement = createPostElement(post);
            postsContainer.appendChild(postElement);
        });
        
        // ホームに戻るボタンを表示
        const subtitle = document.querySelector('.subtitle');
        subtitle.innerHTML = `
            <a href="#" onclick="resetToHome(event)" style="color: #1DA1F2; text-decoration: none;">
                ← ホームに戻る
            </a>
        `;
    } catch (error) {
        console.error('Error fetching user posts:', error);
    }
}

// ホームに戻る関数を追加
function resetToHome(event) {
    if (event) event.preventDefault();
    
    // タイトルを元に戻す
    const title = document.querySelector('.content-header h1');
    title.textContent = 'AI Talk Gallery';
    
    // サブタイトルを元に戻す
    const subtitle = document.querySelector('.subtitle');
    subtitle.textContent = 'ChatGPTとの面白い会話集';
    
    // 投稿を再読み込み
    fetchPosts();
}

// 削除確認モーダルを表示
function showDeleteConfirm(postId) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.id = 'deleteConfirmModal';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h2>投稿の削除</h2>
                <button type="button" class="close-btn" onclick="closeDeleteConfirmModal()">
                    <i class="material-icons">close</i>
                </button>
            </div>
            <div class="modal-body">
                <p>この投稿を削除してもよろしいですか？</p>
                <p class="warning-text">この操作は取り消せません。</p>
                <div class="modal-buttons">
                    <button class="cancel-btn" onclick="closeDeleteConfirmModal()">キャンセル</button>
                    <button class="delete-confirm-btn" onclick="deletePost(${postId})">削除する</button>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    modal.style.display = 'block';
}

// 削除確認モーダルを閉じる
function closeDeleteConfirmModal() {
    const modal = document.getElementById('deleteConfirmModal');
    if (modal) {
        modal.remove();
    }
}

// 投稿を削除
async function deletePost(postId) {
    try {
        const response = await fetch(`/api/posts/${postId}`, {
            method: 'DELETE',
            credentials: 'include'
        });

        if (response.ok) {
            // 投稿要素を削除
            const post = document.querySelector(`[data-post-id="${postId}"]`);
            post.remove();
            closeDeleteConfirmModal();
        } else {
            console.error('Failed to delete post');
        }
    } catch (error) {
        console.error('Error deleting post:', error);
    }
}

// リプライ一覧を取得して表示
async function fetchReplies(postId, originalContent) {
    try {
        console.log('Fetching replies for post:', postId);
        const response = await fetch(`/api/posts/${postId}/replies`);
        if (!response.ok) throw new Error('Failed to fetch replies');
        
        const data = await response.json();
        console.log('Received replies:', data);
        
        // タイトルを更新
        const title = document.querySelector('.content-header h1');
        title.textContent = 'リプライ一覧';
        
        // サブタイトルに元の投稿の内容を表示
        const subtitle = document.querySelector('.subtitle');
        subtitle.innerHTML = `
            <div style="margin-bottom: 1rem;">
                <p style="color: #8899A6;">元の投稿：</p>
                <p>${originalContent}</p>
            </div>
            <a href="#" onclick="resetToHome(event)" style="color: #1DA1F2; text-decoration: none;">
                ← ホームに戻る
            </a>
        `;
        
        // リプライを表示
        postsContainer.innerHTML = '';
        if (data.replies.length === 0) {
            postsContainer.innerHTML = '<p style="padding: 1rem;">まだリプライはありま���ん。</p>';
        } else {
            data.replies.forEach(reply => {
                const replyElement = createPostElement(reply);
                postsContainer.appendChild(replyElement);
            });
        }
    } catch (error) {
        console.error('Error fetching replies:', error);
    }
}

// ナビゲーション機能のセットアップ
function setupNavigation() {
    const homeNav = document.getElementById('home-nav');
    const favoritesNav = document.getElementById('favorites-nav');
    const profileNav = document.getElementById('profile-nav');

    // ホーム
    homeNav?.addEventListener('click', (e) => {
        e.preventDefault();
        resetToHome(e);
        updateActiveNav(homeNav);
    });

    // お気に入り
    favoritesNav?.addEventListener('click', async (e) => {
        e.preventDefault();
        await fetchFavoritePosts();
        updateActiveNav(favoritesNav);
    });

    // プロフィール
    profileNav?.addEventListener('click', async (e) => {
        e.preventDefault();
        // ログインユーザーの投稿を表示
        const userId = currentUser.id;  // currentUserはサーバーから取得する必要があります
        const userName = currentUser.name;
        await fetchPostsByUser(userId, userName);
        updateActiveNav(profileNav);
    });
}

// アクティブなナビゲーションアイテムを更新
function updateActiveNav(activeNav) {
    document.querySelectorAll('.nav-item').forEach(nav => {
        nav.classList.remove('active');
    });
    activeNav.classList.add('active');
}

// お気に入り投稿の取得
async function fetchFavoritePosts() {
    try {
        const response = await fetch('/api/posts/favorites');
        if (!response.ok) throw new Error('Failed to fetch favorites');
        
        const data = await response.json();
        
        // タイトルを更新
        const title = document.querySelector('.content-header h1');
        title.textContent = 'お気に入り';
        
        // サブタイトルを更新
        const subtitle = document.querySelector('.subtitle');
        subtitle.textContent = 'お気に入りに追加した投稿';
        
        // 投稿を表示
        postsContainer.innerHTML = '';
        if (data.posts.length === 0) {
            postsContainer.innerHTML = '<p style="padding: 1rem;">お気に入りの投稿はありません。</p>';
        } else {
            data.posts.forEach(post => {
                const postElement = createPostElement(post);
                postsContainer.appendChild(postElement);
            });
        }
    } catch (error) {
        console.error('Error fetching favorites:', error);
    }
}