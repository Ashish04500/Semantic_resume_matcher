import math


def precision_at_k(ranked_ids, relevance_map, k):
    if k <= 0:
        return 0.0

    top_k = ranked_ids[:k]

    if not top_k:
        return 0.0

    relevant = sum(
        1
        for resume_id in top_k
        if relevance_map.get(resume_id, 0) > 0
    )

    return relevant / len(top_k)


def recall_at_k(ranked_ids, relevance_map, k):
    if k <= 0:
        return 0.0

    total_relevant = sum(
        1
        for relevance in relevance_map.values()
        if relevance > 0
    )

    if total_relevant == 0:
        return 0.0

    top_k = ranked_ids[:k]

    retrieved_relevant = sum(
        1
        for resume_id in top_k
        if relevance_map.get(resume_id, 0) > 0
    )

    return retrieved_relevant / total_relevant


def dcg(relevances):
    score = 0.0

    for position, relevance in enumerate(
        relevances,
        start=1
    ):
        score += (
            (2 ** relevance - 1)
            / math.log2(position + 1)
        )

    return score


def ndcg_at_k(ranked_ids, relevance_map, k):
    if k <= 0:
        return 0.0

    actual_relevances = [
        relevance_map.get(resume_id, 0)
        for resume_id in ranked_ids[:k]
    ]

    ideal_relevances = sorted(
        relevance_map.values(),
        reverse=True
    )[:k]

    actual_dcg = dcg(actual_relevances)
    ideal_dcg = dcg(ideal_relevances)

    if ideal_dcg == 0:
        return 0.0

    return actual_dcg / ideal_dcg


def evaluate(ranked_ids, relevance_map, k):
    if k is None:
        raise ValueError(
            "K must be provided by the caller."
        )

    if k <= 0:
        raise ValueError(
            "K must be greater than 0."
        )

    return {
        f"Precision@{k}": round(
            precision_at_k(
                ranked_ids,
                relevance_map,
                k
            ),
            4
        ),

        f"Recall@{k}": round(
            recall_at_k(
                ranked_ids,
                relevance_map,
                k
            ),
            4
        ),

        f"NDCG@{k}": round(
            ndcg_at_k(
                ranked_ids,
                relevance_map,
                k
            ),
            4
        )
    }