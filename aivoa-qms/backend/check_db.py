from database import SessionLocal
import models

db = SessionLocal()
complaints = db.query(models.Complaint).all()

print("\n=== SAVED COMPLAINTS IN DATABASE ===")
if not complaints:
    print("No complaints found. Database is empty.")
else:
    for c in complaints:
        print(f"ID: {c.id} | Product: {c.product_name} | Batch: {c.batch_number} | Site: {c.originating_site}")
print("====================================\n")

db.close()