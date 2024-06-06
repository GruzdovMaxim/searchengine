from flask import Flask, request, render_template
from search.search_engine import websearch


app = Flask(__name__, template_folder='./static')


@app.route("/")
def home():
    return render_template('home.html')


@app.route('/websearch', methods=['GET'])
def search():
    query = request.args.get('query', '')
    model_type = request.args.get('model_type', 'bm25')
    use_pagerank = request.args.get('use_pagerank', 'off') == 'on'
    use_model_score = request.args.get('use_model_score', 'off') == 'on'
    page = request.args.get('page', 1, type=int)
    per_page = 10

    if not query:
        return render_template('home.html')

    results = websearch(query, model_type=model_type, use_pagerank=use_pagerank, use_model_score=use_model_score)
    total_results = len(results)
    results = results[(page - 1) * per_page:page * per_page]

    last_page = (total_results // per_page) + (total_results % per_page > 0)
    start_page = max(1, page - 2)
    end_page = min(page + 2, last_page)

    if end_page - start_page < 4:
        if start_page == 1:
            end_page = min(5, last_page)
        elif end_page == last_page:
            start_page = max(1, last_page - 4)

    pagination_pages = list(range(start_page, end_page + 1))

    return render_template('results.html', query=query, results=results, page=page,
                           total_results=total_results, per_page=per_page, model_type=model_type,
                           use_pagerank='on' if use_pagerank else 'off',
                           use_model_score='on' if use_model_score else 'off',
                           pagination_pages=pagination_pages, last_page=last_page)


if __name__ == "__main__":
    app.run(debug=True)
