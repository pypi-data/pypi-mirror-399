import numpy as np
import json
from rouge_score import rouge_scorer
import razdel


def russian_tokenizer(text):
    return [token.text for token in razdel.tokenize(text)]

class RAGEvaluator:
    def __init__(self):
        self.rouge_scorer = rouge_scorer.RougeScorer(
            ["rouge1", "rougeL"], use_stemmer=True
        )
        self.rouge_scorer = rouge_scorer.RougeScorer(    
            ["rouge1", "rougeL"], 
            use_stemmer=False
        )
        self.rouge_scorer._tokenizer.tokenize = russian_tokenizer

    def evaluate_retrieval(
        self, retrieved_doc_ids, relevant_doc_id
    ):
        metrics = {}

        metrics["hit_rate"] = 1.0 if relevant_doc_id in retrieved_doc_ids else 0.0

        for i, doc_id in enumerate(retrieved_doc_ids):
            if doc_id == relevant_doc_id:
                metrics["mrr"] = 1.0 / (i + 1)
                break
        else:
            metrics["mrr"] = 0

        return metrics

    def evaluate_generation(self, generated_answer: str, reference_answer: str):
        rouge_scores = self.rouge_scorer.score(generated_answer, reference_answer)
        substring_match = 1 if reference_answer.lower() in generated_answer.lower() else 0
        return {
            "rouge1": rouge_scores["rouge1"].fmeasure,
            "rougeL": rouge_scores["rougeL"].fmeasure,
            "substr_match": substring_match
        }

def evaluate_rag_results(results, dataset, mapping, evaluator: RAGEvaluator):
    # Initialize results structure
    individual_results = {}
    dataset = dataset["train"].sort("public_id")
    
    questions_by_type = {}
    
    for i, question_data in enumerate(dataset):
        question_type = question_data.get("type", "simple")  # Default to "simple" if no type is specified
        if question_type not in questions_by_type:
            questions_by_type[question_type] = []
        questions_by_type[question_type].append(str(question_data["public_id"]))
    
    for i, result in results.items():
        question_data = dataset[int(i)]
        reference_answer = question_data["answer"]
        question_type = question_data.get("type", "simple")  # Default to "simple" if no type is specified
                
        text_ids = json.loads(question_data.get("text_ids"))
        
        relevant_doc_ids = []
        for text_id in text_ids:
            if isinstance(text_id, list):
                relevant_doc_ids.extend(text_id)
            else:
                relevant_doc_ids.append(text_id)
        
        relevant_doc_ids = list(set(relevant_doc_ids))
        
        # Apply mapping to convert public IDs to private IDs if needed
        mapped_found_doc_ids = []
        for doc_id in result["found_ids"]:
            if doc_id in mapping:
                mapped_found_doc_ids.append(mapping[doc_id])
            else:
                raise Exception(f'Document ID {doc_id} not found in mapping')
        
        retrieval_metrics_list = []
        for relevant_doc_id in relevant_doc_ids:
            metrics = evaluator.evaluate_retrieval(
                retrieved_doc_ids=mapped_found_doc_ids, relevant_doc_id=relevant_doc_id
            )
            retrieval_metrics_list.append(metrics)
        
        if retrieval_metrics_list:
            # Find the best metric scores
            best_retrieval_metrics = {
                "hit_rate": max(m["hit_rate"] for m in retrieval_metrics_list),
                "mrr": max(m["mrr"] for m in retrieval_metrics_list)
            }
            retrieval_metrics = best_retrieval_metrics
        else:
            # Default metrics if no relevant documents are found
            retrieval_metrics = {
                "hit_rate": 0.0,
                "mrr": 0.0
            }
            
        if mapped_found_doc_ids:
            correct_retrievals = sum(1 for doc_id in mapped_found_doc_ids if doc_id in relevant_doc_ids)
            retrieval_metrics["precision"] = correct_retrievals / len(mapped_found_doc_ids)
        else:
            retrieval_metrics["precision"] = 0.0

        generation_metrics = evaluator.evaluate_generation(
            generated_answer=result["model_answer"], reference_answer=reference_answer
        )

        individual_results[i] = {
            "retrieval": retrieval_metrics,
            "generation": generation_metrics,
            "type": question_type
        }

    aggregated_metrics = {}
    
    for question_type in questions_by_type.keys():
        aggregated_metrics[question_type] = {
            "retrieval": {
                "hit_rate": 0.0,
                "mrr": 0.0,
                "precision": 0.0
            },
            "generation": {
                "rouge1": 0.0,
                "rougeL": 0.0
            }
        }
    
    for question_type, questions in questions_by_type.items():
        type_results = [individual_results[q] for q in questions if q in individual_results]
        
        if not type_results:
            continue
            
        for metric in ["hit_rate", "mrr", "precision"]:
            aggregated_metrics[question_type]["retrieval"][metric] = np.mean(
                [res["retrieval"][metric] for res in type_results]
            )
            
        for metric in ["rouge1", "rougeL", "substr_match"]:
            aggregated_metrics[question_type]["generation"][metric] = np.mean(
                [res["generation"][metric] for res in type_results]
            )
    
    overall_metrics = {
        "retrieval": {
            "hit_rate": np.mean([res["retrieval"]["hit_rate"] for res in individual_results.values()]),
            "mrr": np.mean([res["retrieval"]["mrr"] for res in individual_results.values()]),
            "precision": np.mean([res["retrieval"]["precision"] for res in individual_results.values()])
        },
        "generation": {
            "rouge1": np.mean([res["generation"]["rouge1"] for res in individual_results.values()]),
            "rougeL": np.mean([res["generation"]["rougeL"] for res in individual_results.values()]),
            "substr_match": np.mean([res["generation"]["substr_match"] for res in individual_results.values()])
        }
    }
    
    aggregated_metrics["overall"] = overall_metrics
    
    average_metrics = {
        "retrieval": overall_metrics["retrieval"],
        "generation": overall_metrics["generation"]
    }

    return {
        "individual_results": individual_results,
        "aggregated_metrics": aggregated_metrics,
        "average_metrics": average_metrics  # Backward compatibility
    }
