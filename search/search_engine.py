from search.BM25_search import bm25_search
from search.vectorModel.vector_search import vector_search
from database.db_api import Database


def websearch(query, model_type='bm25', use_pagerank=True, use_model_score=True):
    if model_type == 'bm25':
        results = bm25_search(query)
    elif model_type == 'vector':
        results = vector_search(query)
    elif model_type == 'combined':
        results_bm25 = bm25_search(query)
        results_vector = vector_search(query)
        results = combine_search_results(results_bm25, results_vector)
    else:
        return []

    detailed_results = {}
    with Database() as db:
        for index, (doc_id, model_score) in enumerate(results.items()):
            result = db.execute("""
                            SELECT url, title, page_rank, rank_group
                            FROM pages
                            WHERE id = ?
                        """, (doc_id,))

            if result:
                url, title, pagerank, rank_group = result.fetchone()

                metrics = [
                    (model_score, 0.90, use_model_score),
                    (pagerank, 0.10, use_pagerank),
                ]

                total_score = calculate_total_score(metrics)

                detailed_results[doc_id] = {
                    'model_score': model_score,
                    'url': url,
                    'title': title,
                    'pagerank': pagerank,
                    'rank_group': rank_group,
                    'total_score': total_score
                }

    sorted_results = sorted(detailed_results.items(), key=lambda x: x[1]['total_score'], reverse=True)
    return sorted_results


def combine_search_results(results1, results2):
    combined_results = {doc_id: (results1.get(doc_id, 0) + results2.get(doc_id, 0)) / 2
                        for doc_id in results1 if doc_id in results2}
    return combined_results


def calculate_total_score(metrics):
    active_metrics = [(value, weight) for value, weight, is_active in metrics if is_active]
    # Якщо активний лише один метрик, повертаємо його значення без ваги
    if len(active_metrics) == 1:
        return active_metrics[0][0]
    # Розрахунок ваг і total_score, якщо активних метриків більше одного
    total_weight = sum(weight for _, weight in active_metrics)
    total_score = sum(value * (weight / total_weight) for value, weight in active_metrics)

    return total_score
