with open(r"backend\app\models.py", "r", encoding="utf-8") as f:
    text = f.read()

target = 'verifications = relationship("RequestVerification", back_populates="request")'
replacement = 'verifications = relationship("RequestVerification", foreign_keys="RequestVerification.request_id", back_populates="request")'

assert target in text, "Target verifications relationship not found"
text = text.replace(target, replacement, 1)

with open(r"backend\app\models.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Fixed foreign_keys on verifications relationship")
