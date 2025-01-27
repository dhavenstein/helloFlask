from flask import Flask, render_template, request, redirect, url_for, jsonify
import wikipedia
from diskcache import Cache

app = Flask(__name__)

# Create caches with separate directories for different types of data
message_store = Cache('./cache/messages')
wiki_cache = Cache('./cache/wikipedia')

# Initialize messages list if it doesn't exist
if 'messages' not in message_store:
    message_store['messages'] = []

@app.route('/')
def home():
    return render_template('index.html', messages=message_store['messages'])

@app.route('/add_message', methods=['POST'])
def add_message():
    message = request.form.get('message')
    if message:
        messages = message_store['messages']
        messages.append(message)
        message_store['messages'] = messages
    return redirect(url_for('home'))

@app.route('/wikipedia', methods=['GET'])
def get_wikipedia():
    title = request.args.get('title')
    if not title:
        return jsonify({'error': 'Title parameter is required'}), 400

    # Try to get from cache first
    cached_data = wiki_cache.get(title)
    if cached_data:
        return jsonify(cached_data)

    try:
        page = wikipedia.page(title)
        page_data = {
            'title': page.title,
            'summary': page.summary,
            'images': page.images,
            'links': page.links,
            'references': page.references,
            'categories': page.categories,
        }
        # Cache Wikipedia data for 1 day (86400 seconds)
        wiki_cache.set(title, page_data, expire=86400)
        return jsonify(page_data)
    except wikipedia.exceptions.PageError:
        return jsonify({'error': 'Page not found'}), 404
    except wikipedia.exceptions.DisambiguationError as e:
        return jsonify({'error': 'Ambiguous title', 'options': e.options}), 400

if __name__ == '__main__':
    app.run(debug=True)
