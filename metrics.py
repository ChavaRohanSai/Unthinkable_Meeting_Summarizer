import mysql.connector
from evaluate import load

conn = mysql.connector.connect(
    host="localhost",
    user="rohan",
    password="Advaitha@123",   # change this
    database="meeting_app"       # change to your DB name
)
cursor = conn.cursor(dictionary=True)


cursor.execute("""
    SELECT transcript, summary
    FROM meetings
    WHERE transcript IS NOT NULL AND summary IS NOT NULL
""")

rows = cursor.fetchall()

if not rows:
    print(" No records found with both transcript and summary.")
    exit()

references = [row["transcript"] for row in rows]
predictions = [row["summary"] for row in rows]

print(f" Found {len(rows)} meeting summaries to evaluate...")

rouge = load("rouge")
bleu = load("bleu")


rouge_result = rouge.compute(predictions=predictions, references=references)
bleu_result = bleu.compute(predictions=predictions, references=references)

print(f"ROUGE-1: {rouge_result['rouge1']:.4f}")
print(f"ROUGE-2: {rouge_result['rouge2']:.4f}")
print(f"ROUGE-L: {rouge_result['rougeL']:.4f}")
print(f"BLEU:    {bleu_result['bleu']:.4f}")

cursor.close()
conn.close()
