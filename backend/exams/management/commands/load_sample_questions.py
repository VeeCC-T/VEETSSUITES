from django.core.management.base import BaseCommand
from exams.models import Question


class Command(BaseCommand):
    help = 'Load sample pharmacy questions for testing'

    def handle(self, *args, **options):
        sample_questions = [
            {
                'text': 'What is the primary mechanism of action of aspirin?',
                'option_a': 'COX-1 inhibition only',
                'option_b': 'COX-2 inhibition only',
                'option_c': 'Both COX-1 and COX-2 inhibition',
                'option_d': 'Prostaglandin synthesis enhancement',
                'correct_answer': 'C',
                'category': 'Pharmacology',
                'difficulty': 'medium'
            },
            {
                'text': 'Which of the following is a contraindication for ACE inhibitors?',
                'option_a': 'Hypertension',
                'option_b': 'Heart failure',
                'option_c': 'Bilateral renal artery stenosis',
                'option_d': 'Diabetes mellitus',
                'correct_answer': 'C',
                'category': 'Clinical Pharmacy',
                'difficulty': 'hard'
            },
            {
                'text': 'What is the recommended storage temperature for insulin?',
                'option_a': 'Room temperature (20-25°C)',
                'option_b': 'Refrigerated (2-8°C)',
                'option_c': 'Frozen (-18°C)',
                'option_d': 'Hot temperature (30-35°C)',
                'correct_answer': 'B',
                'category': 'Pharmaceutics',
                'difficulty': 'easy'
            },
            {
                'text': 'Which enzyme is primarily responsible for metabolizing warfarin?',
                'option_a': 'CYP2D6',
                'option_b': 'CYP3A4',
                'option_c': 'CYP2C9',
                'option_d': 'CYP1A2',
                'correct_answer': 'C',
                'category': 'Pharmacokinetics',
                'difficulty': 'hard'
            },
            {
                'text': 'What is the first-line treatment for mild to moderate hypertension?',
                'option_a': 'Beta-blockers',
                'option_b': 'ACE inhibitors or ARBs',
                'option_c': 'Calcium channel blockers',
                'option_d': 'Diuretics',
                'correct_answer': 'B',
                'category': 'Clinical Pharmacy',
                'difficulty': 'medium'
            },
            {
                'text': 'Which of the following medications requires therapeutic drug monitoring?',
                'option_a': 'Paracetamol',
                'option_b': 'Ibuprofen',
                'option_c': 'Digoxin',
                'option_d': 'Aspirin',
                'correct_answer': 'C',
                'category': 'Clinical Pharmacy',
                'difficulty': 'medium'
            },
            {
                'text': 'What is the mechanism of action of proton pump inhibitors?',
                'option_a': 'H2 receptor antagonism',
                'option_b': 'Irreversible inhibition of H+/K+-ATPase',
                'option_c': 'Prostaglandin synthesis',
                'option_d': 'Antacid neutralization',
                'correct_answer': 'B',
                'category': 'Pharmacology',
                'difficulty': 'medium'
            },
            {
                'text': 'Which vitamin deficiency is associated with pernicious anemia?',
                'option_a': 'Vitamin B1 (Thiamine)',
                'option_b': 'Vitamin B6 (Pyridoxine)',
                'option_c': 'Vitamin B12 (Cobalamin)',
                'option_d': 'Vitamin C (Ascorbic acid)',
                'correct_answer': 'C',
                'category': 'Clinical Pharmacy',
                'difficulty': 'easy'
            },
            {
                'text': 'What is the half-life of a drug if 75% is eliminated after 8 hours?',
                'option_a': '2 hours',
                'option_b': '4 hours',
                'option_c': '6 hours',
                'option_d': '8 hours',
                'correct_answer': 'B',
                'category': 'Pharmacokinetics',
                'difficulty': 'hard'
            },
            {
                'text': 'Which of the following is NOT a side effect of statins?',
                'option_a': 'Myopathy',
                'option_b': 'Hepatotoxicity',
                'option_c': 'Hyperglycemia',
                'option_d': 'Hypotension',
                'correct_answer': 'D',
                'category': 'Pharmacology',
                'difficulty': 'medium'
            },
            {
                'text': 'What is the recommended route of administration for epinephrine in anaphylaxis?',
                'option_a': 'Intravenous',
                'option_b': 'Intramuscular',
                'option_c': 'Subcutaneous',
                'option_d': 'Oral',
                'correct_answer': 'B',
                'category': 'Clinical Pharmacy',
                'difficulty': 'easy'
            },
            {
                'text': 'Which drug interaction mechanism involves competition for the same enzyme?',
                'option_a': 'Enzyme induction',
                'option_b': 'Enzyme inhibition',
                'option_c': 'Protein binding displacement',
                'option_d': 'Renal clearance alteration',
                'correct_answer': 'B',
                'category': 'Pharmacokinetics',
                'difficulty': 'medium'
            },
            {
                'text': 'What is the primary indication for metformin?',
                'option_a': 'Type 1 diabetes',
                'option_b': 'Type 2 diabetes',
                'option_c': 'Gestational diabetes',
                'option_d': 'Hypoglycemia',
                'correct_answer': 'B',
                'category': 'Clinical Pharmacy',
                'difficulty': 'easy'
            },
            {
                'text': 'Which of the following antibiotics is bacteriostatic?',
                'option_a': 'Penicillin',
                'option_b': 'Cephalexin',
                'option_c': 'Tetracycline',
                'option_d': 'Amoxicillin',
                'correct_answer': 'C',
                'category': 'Pharmacology',
                'difficulty': 'medium'
            },
            {
                'text': 'What is the bioavailability of a drug given intravenously?',
                'option_a': '50%',
                'option_b': '75%',
                'option_c': '90%',
                'option_d': '100%',
                'correct_answer': 'D',
                'category': 'Pharmacokinetics',
                'difficulty': 'easy'
            }
        ]

        created_count = 0
        for question_data in sample_questions:
            question, created = Question.objects.get_or_create(
                text=question_data['text'],
                defaults=question_data
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully loaded {created_count} new sample questions. '
                f'Total questions in database: {Question.objects.count()}'
            )
        )