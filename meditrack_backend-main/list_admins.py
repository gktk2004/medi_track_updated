from meditrackapp.models import Admin
print("--- EXISTING ADMINS ---")
for a in Admin.objects.all():
    print(f"ID: {a.id} | Username: {a.username} | Email: {a.email} | Password: {a.password}")
print("--- END ---")
