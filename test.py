from notifier import send_alert
from evaluator import JobEvaluation

send_alert('https://facebook.com', JobEvaluation(is_relevant=True, confidence=1, job_title='Test Job Title', company_name='Test Co', reason='Verification test'), original_text='This is a test notification')
