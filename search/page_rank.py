import networkx as nx
import numpy as np

from database.db_api import Database


def filter_domains_for_pagerank(threshold=1000):
    with Database() as db:
        cursor = db.execute("SELECT target_url, COUNT(*) FROM links GROUP BY target_url HAVING COUNT(*) > ?",
                            (threshold,))
        frequent_domains = {row[0] for row in cursor.fetchall()}
    return frequent_domains


def calculate_pagerank_nx():
    # frequent_domains = filter_domains_for_pagerank()

    with Database() as db:
        # Завантажуємо сторінки та їх URL
        pages = db.execute("SELECT id, url FROM pages").fetchall()
        url_to_id = {row[1]: row[0] for row in pages}
        G = nx.DiGraph()

        # Додаємо вузли
        for page_id, url in pages:
            G.add_node(page_id)

        # Завантажуємо посилання та будуємо граф
        links = db.execute("SELECT source_page_id, target_url FROM links").fetchall()
        for source_id, target_url in links:
            # if target_url not in frequent_domains:
            target_id = url_to_id.get(target_url)
            if target_id:
                G.add_edge(source_id, target_id)
        pr = nx.pagerank(G, alpha=0.85)

        # нормалізація
        max_pr = max(pr.values())
        for node_id in pr:
            pr[node_id] = 100 * pr[node_id] / max_pr

        updates = [(rank, page_id) for page_id, rank in pr.items()]
        db.executemany("UPDATE pages SET page_rank = ? WHERE id = ?", updates)

    compute_pagerank_groups(pr)


def compute_pagerank_groups(pr_values):
    # відсортований список кортежів (ID, значення)
    sorted_pages = sorted(pr_values.items(), key=lambda x: x[1], reverse=True)

    # Отримуємо тільки значення PageRank для розрахунку середнього
    pagerank_values = [value for _, value in sorted_pages]
    mean_value = np.mean(pagerank_values)

    # Визначаємо індекс найближчий до середнього значення
    mean_index = min(range(len(pagerank_values)), key=lambda i: abs(pagerank_values[i] - mean_value))

    # Визначаємо межі груп
    rank_high = sorted_pages[:max(1, mean_index // 2)]
    rank_medium_high = sorted_pages[max(1, mean_index // 2):mean_index]
    rank_medium_low = sorted_pages[mean_index:mean_index + (len(pagerank_values) - mean_index) // 2]
    rank_low = sorted_pages[mean_index + (len(pagerank_values) - mean_index) // 2:]

    groups = []
    for page_id, _ in rank_high:
        groups.append((page_id, 'rank-high'))
    for page_id, _ in rank_medium_high:
        groups.append((page_id, 'rank-medium-high'))
    for page_id, _ in rank_medium_low:
        groups.append((page_id, 'rank-medium-low'))
    for page_id, _ in rank_low:
        groups.append((page_id, 'rank-low'))

    with Database() as db:
        db.executemany("UPDATE pages SET rank_group = ? WHERE id = ?", [(group, page_id) for page_id, group in groups])
