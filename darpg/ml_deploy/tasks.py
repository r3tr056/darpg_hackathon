
from celery import shared_task

from grievance_reports.models import GrievanceReport
from ml_deploy.topic_cluster.data.preprocess import preprocess

def classify_reports():
    pass

def preprocess_reports(all_reports):
    texts = [report.subject_content for report in all_reports]
    sentences, token_lists, idx_in = preprocess(texts)
    return (sentences, token_lists, idx_in)

@shared_task
def process_reports_batch():
    batch_size = 128
    reports_to_process = GrievanceReport.objects.filter(classified=False)[:batch_size]
    if not reports_to_process:
        return
    
    preprocessed_reports = preprocess_reports(reports_to_process)
    classification_results = classify_reports(preprocessed_reports)

    for report, result in zip(reports_to_process, classification_results):
        report.status = result
        report.classifed = True
        report.save()

@shared_task
def process_report(report_id):
    report = [GrievanceReport.objects.get(id=report_id)]
    if report.classifid:
        return "Report already classified"
    
    preprocessd_report = preprocess_reports(report)
    classification_result = classify_reports(preprocessd_report)

    report[0].status = classification_result[0]
    report[0].classifed = True
    report[0].save()