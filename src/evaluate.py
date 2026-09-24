import json
import os
import sys
from src.hybrid_search import hybrid_search

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

def load_questions():
    file_path = os.path.join(PROJECT_ROOT, "queries", "test_queries.json")

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

def recall_at_k(results, relevant_chunks, k):
    top_results = results[:k]
    retrieved_chunks = set()

    for result in top_results:
        if "chunk_id" in result:
            retrieved_chunks.add(result["chunk_id"])
     
        elif "payload" in result:
            payload = result["payload"]

            if "chunk_id" in payload:
                retrieved_chunks.add(payload["chunk_id"])

    relevant_chunks = set(relevant_chunks)

    if len(relevant_chunks) == 0:
        return 0.0

    found = retrieved_chunks.intersection(relevant_chunks)
    recall = len(found) / len(relevant_chunks)

    return recall


def evaluate_question(question_data, question_number):

    question_id = question_data.get("id", question_number)
    question = question_data.get("question", question_data["query"])
    relevant_chunks = question_data["relevant_chunks"]

    print("\n" + "=" * 60)
    print(f"Question ID: {question_id}")
    print(f"Question: {question}")
    print(f"Relevant chunks: {relevant_chunks}")

    results = hybrid_search(question, limit=10)
    recall_5 = recall_at_k(results, relevant_chunks, 5)
    recall_10 = recall_at_k(results, relevant_chunks, 10)

    retrieved_chunks = []

    for result in results[:10]:
        if "chunk_id" in result:
            retrieved_chunks.append(result["chunk_id"])

        elif "payload" in result:
            payload = result["payload"]

            if "chunk_id" in payload:
                retrieved_chunks.append(payload["chunk_id"])

    print(f"Retrieved chunks: {retrieved_chunks}")
    print(f"Recall@5: {recall_5 * 100:.2f}%")
    print(f"Recall@10: {recall_10 * 100:.2f}%")

    return {
        "id": question_id,
        "question": question,
        "relevant_chunks": relevant_chunks,
        "retrieved_chunks": retrieved_chunks,
        "recall_at_5": recall_5,
        "recall_at_10": recall_10
    }

def main():
    
    print("\n")
    print("=" * 60)
    print("        PHASE 12 - RETRIEVAL RECALL EVALUATION")
    print("=" * 60)

    questions = load_questions()
    print(f"\nTotal questions: {len(questions)}")
    
    results = []

    for question_number, question in enumerate(questions, start=1):
        result = evaluate_question(question, question_number)
        results.append(result)

    if len(results) > 0:
        average_recall_5 = sum(result["recall_at_5"] for result in results) / len(results)
        average_recall_10 = sum(result["recall_at_10"] for result in results) / len(results)
        
    else:
        average_recall_5 = 0.0
        average_recall_10 = 0.0

    print("\n")
    print("=" * 60)
    print("                FINAL RESULTS")
    print("=" * 60)
    print(f"Total questions : {len(results)}")
    print(f"Recall@5        : " f"{average_recall_5 * 100:.2f}%")
    print(f"Recall@10       : " f"{average_recall_10 * 100:.2f}%")
    print("=" * 60)

    output_file = os.path.join(PROJECT_ROOT, "results", "evaluation_results.json")
    report = {
        "total_questions": len(results),
        "average_recall_at_5": average_recall_5,
        "average_recall_at_10": average_recall_10,
        "questions": results
    }


    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4, ensure_ascii=False)

evaluate = main


if __name__ == "__main__":
    main()