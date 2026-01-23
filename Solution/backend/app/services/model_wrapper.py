import torch
from typing import List

def predict_comments(comments: List[str]) -> List[List[str]]:
    """
    Simulates the prediction of a list of comments using final_model.pt.
    Returns a list of labels for each comment.
    Example output for one comment: ["price_complaint", "service_appreciation"]
    """
    # This is a placeholder for the actual model logic.
    # In a real scenario, you would do:
    # model = torch.load("final_model.pt")
    # results = model.predict(comments)
    
    # For now, we return mock predictions based on keywords or random data
    # as requested by the user to "create that but dont use it yet".
    
    mock_results = []
    for comment in comments:
        # Mock logic to match keywords
        labels = []
        c = comment.lower()
        if "prix" in c or "cher" in c or "price" in c:
            labels.append("price_complaint")
        if "bien" in c or "top" in c or "good" in c or "excellent" in c:
            labels.append("service_appreciation")
        if "attente" in c or "retard" in c or "slow" in c:
            labels.append("service_complaint")
        
        if not labels:
            labels.append("general_feedback")
            
        mock_results.append(labels)
        
    return mock_results
