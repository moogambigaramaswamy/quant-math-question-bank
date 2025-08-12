#!/usr/bin/env python3
"""
run_quiz.py

Usage:
    python run_quiz.py

Description:
    Parses a tagged question block (see `RAW_QUESTIONS`) and runs an interactive quiz in the terminal.
    The correct option is detected by the tag line beginning with @@option.
"""

import re
import textwrap

RAW_QUESTIONS = r"""
@title Quantitative Aptitude – Numbers and Operations Assessment
@description Assessment covering problem-solving skills in Numbers and Operations, focusing on Simple Interest and Time & Work problems.

// Question 1
@question A person invests ₹12,000 in a fixed deposit scheme at a simple interest rate of \( 6\% \) per annum for 2 years. The total amount is then reinvested at \( 8\% \) per annum for 3 more years. What is the final amount after the second investment?
@instruction Select the correct answer.
@difficulty moderate
@Order 1
@option ₹16,560.00
@option ₹16,640.00
@@option ₹16,665.60
@option ₹16,720.00
@explanation 
First investment: \(\text{SI}_1=\dfrac{12000\times 6\times 2}{100}=₹1,440\). Amount after 2 years \(A_1=12000+1440=₹13,440\).  
Second investment: \(\text{SI}_2=\dfrac{13{,}440\times 8\times 3}{100}=₹3,225.60\). Final amount \(=13{,}440+3{,}225.60=₹16,665.60\).
@subject Mathematics
@unit Commercial Mathematics
@topic Simple Interest
@plusmarks 1

// Question 2
@question Three pipes can fill a tank in 10 hours, 15 hours, and 20 hours respectively. All three pipes are opened together for 2 hours, after which the fastest pipe (10-hour) is closed. The remaining two pipes continue until the tank is full. What is the total time taken to fill the tank?
@instruction Select the correct answer.
@difficulty moderate
@Order 2
@option \(6\frac{5}{6}\) hours
@option \(6\frac{4}{5}\) hours
@@option \(6\frac{6}{7}\) hours
@option \(7\frac{1}{6}\) hours
@explanation 
Rates: \(r_1=\tfrac{1}{10},\ r_2=\tfrac{1}{15},\ r_3=\tfrac{1}{20}\). Combined rate \(=\tfrac{13}{60}\) tank/hr. Work in first 2 hrs \(=2\times\tfrac{13}{60}=\tfrac{13}{30}\). Remaining \(=1-\tfrac{13}{30}=\tfrac{17}{30}\). Remaining two pipes rate \(=\tfrac{1}{15}+\tfrac{1}{20}=\tfrac{7}{60}\). Time to finish \(=\dfrac{\tfrac{17}{30}}{\tfrac{7}{60}}=\dfrac{34}{7}\) hrs \(=4\frac{6}{7}\) hrs. Total time \(=2+\dfrac{34}{7}=\dfrac{48}{7}\) hrs \(=6\frac{6}{7}\) hrs.
@subject Mathematics
@unit Algebraic Applications
@topic Time and Work
@plusmarks 1
"""

# -----------------------------
# Parsing functions
# -----------------------------
def split_question_blocks(raw_text):
    # split on "// Question" markers (keep the first overall metadata block if needed)
    parts = re.split(r'//\s*Question\s*\d+', raw_text)
    # first part before first question may contain title/description; ignore if empty
    blocks = [p.strip() for p in parts if p.strip()]
    return blocks

def parse_block(block_text):
    """Parse one block into a dict with keys: question, instruction, difficulty, order, options (list),
       correct_index (int), explanation, subject, unit, topic, plusmarks"""
    data = {
        "question": "",
        "instruction": "",
        "difficulty": "",
        "order": None,
        "options": [],
        "correct_index": None,
        "explanation": "",
        "subject": "",
        "unit": "",
        "topic": "",
        "plusmarks": None,
    }

    # Patterns for tags
    tag_pattern = re.compile(r'@(\w+)\s*(.*)')
    lines = block_text.splitlines()
    current_tag = None
    buffer = []

    def flush_buffer():
        nonlocal current_tag, buffer
        if not current_tag:
            buffer = []
            return
        content = "\n".join(buffer).strip()
        if current_tag == "question":
            data["question"] = content
        elif current_tag == "instruction":
            data["instruction"] = content
        elif current_tag == "difficulty":
            data["difficulty"] = content
        elif current_tag == "Order":
            try:
                data["order"] = int(content)
            except:
                data["order"] = content
        elif current_tag == "explanation":
            data["explanation"] = content
        elif current_tag == "subject":
            data["subject"] = content
        elif current_tag == "unit":
            data["unit"] = content
        elif current_tag == "topic":
            data["topic"] = content
        elif current_tag == "plusmarks":
            data["plusmarks"] = content
        buffer = []

    # We'll treat option lines differently since they can be multiple per block
    for raw in lines:
        line = raw.rstrip()
        if not line:
            # keep blank lines for multi-line tags like explanation
            if current_tag:
                buffer.append("")
            continue

        # Check for @@option (correct option)
        if line.strip().startswith('@@option'):
            # flush previous tag buffer
            flush_buffer()
            # extract option text after tag
            opt_text = line.strip()[len('@@option'):].strip()
            if opt_text:
                data["options"].append(opt_text)
                data["correct_index"] = len(data["options"]) - 1
            else:
                # handle multi-line option content
                current_tag = "option"
                buffer = []
            continue

        # check for @option (normal option)
        if line.strip().startswith('@option'):
            flush_buffer()
            opt_text = line.strip()[len('@option'):].strip()
            data["options"].append(opt_text)
            continue

        # check for other tags like @question, @instruction, etc.
        m = tag_pattern.match(line.strip())
        if m:
            # a new tag begins
            flush_buffer()
            tag = m.group(1)
            rest = m.group(2).strip()
            current_tag = tag
            if rest:
                buffer = [rest]
            else:
                buffer = []
            continue

        # if line does not start with a tag, it's continuation of current tag
        if current_tag:
            buffer.append(line)
        else:
            # stray text: ignore or append to question
            buffer.append(line)

    # flush any remaining buffer
    flush_buffer()

    # final cleanup: if correct_index wasn't set by @@option, attempt to find an option marked by some other method
    # (not required here)
    return data

def load_questions(raw_text):
    blocks = split_question_blocks(raw_text)
    parsed = []
    for blk in blocks:
        # skip global metadata that might be title/description
        if blk.strip().startswith('@title') or blk.strip().startswith('@description') or blk.strip().startswith('@question'):
            # If block contains @question tag we need to parse; parse_block expects one question block (we passed question chunk)
            # But split_question_blocks returns first chunk possibly with title/description: we'll detect presence of @question
            if '@question' not in blk:
                # this is global metadata - skip
                continue
        parsed.append(parse_block(blk))
    return parsed

# -----------------------------
# Quiz runner
# -----------------------------
def run_quiz(questions):
    print("\nWelcome to the Quantitative Aptitude Quiz!\n")
    score = 0
    total = len(questions)
    for i, q in enumerate(questions, start=1):
        print(f"Question {i}:")
        print(textwrap.fill(q['question'], width=80))
        print()
        if q['instruction']:
            print(f"Instruction: {q['instruction']}")
        print()
        # print options numbered
        for idx, opt in enumerate(q['options'], start=1):
            print(f"  {idx}. {opt}")
        # get input
        while True:
            try:
                choice = input("\nEnter option number (or 'q' to quit): ").strip()
                if choice.lower() == 'q':
                    print("Quiz aborted by user.")
                    return
                choice_num = int(choice)
                if 1 <= choice_num <= len(q['options']):
                    break
            except ValueError:
                pass
            print("Invalid input — please enter a valid option number.")
        selected_idx = choice_num - 1
        correct_idx = q['correct_index']
        if correct_idx is not None and selected_idx == correct_idx:
            print("✅ Correct!")
            score += 1
        else:
            correct_text = q['options'][correct_idx] if correct_idx is not None and 0 <= correct_idx < len(q['options']) else "Not specified"
            print(f"❌ Incorrect. Correct answer: {correct_text}")
        if q['explanation']:
            print("\nExplanation:")
            print(textwrap.fill(q['explanation'], width=80))
        print("\n" + "-"*60 + "\n")
    # final score
    print(f"You scored {score} out of {total} ({(score/total*100):.1f}%).\n")

# -----------------------------
# Main
# -----------------------------
def main():
    questions = load_questions(RAW_QUESTIONS)
    if not questions:
        print("No questions found in the input. Make sure the tagged format is correct.")
        return
    run_quiz(questions)

if __name__ == "__main__":
    main()
