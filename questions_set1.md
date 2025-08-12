questions = [
    {
        "question": "A person invests ₹12,000 in a fixed deposit scheme at a simple interest rate of 6% per annum for 2 years...",
        "options": ["₹16,560.00", "₹16,640.00", "₹16,665.60", "₹16,720.00"],
        "answer": "₹16,665.60",
        "explanation": "First investment: SI1 = ... Final amount = ₹16,665.60"
    },
    {
        "question": "Three pipes can fill a tank in 10 hours, 15 hours, and 20 hours respectively...",
        "options": ["6 5/6 hours", "6 4/5 hours", "6 6/7 hours", "7 1/6 hours"],
        "answer": "6 6/7 hours",
        "explanation": "Rates: r1=..., Total time = 6 6/7 hours"
    }
]

for q in questions:
    print("\n" + q["question"])
    for i, opt in enumerate(q["options"], 1):
        print(f"{i}. {opt}")
    choice = input("Enter the option number: ")
    if q["options"][int(choice)-1] == q["answer"]:
        print("✅ Correct!")
    else:
        print(f"❌ Incorrect. Correct answer: {q['answer']}")
    print("Explanation:", q["explanation"])
