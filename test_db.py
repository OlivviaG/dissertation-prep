from src.database import initialise_db, get_or_create_user, save_checkin, get_checkins

initialise_db()

user_id = get_or_create_user("Oliwia")
print(f"User ID: {user_id}")

save_checkin(user_id, energy=7.5, stress=4.0, heart_rate=72.0, mood_text="Feeling good today")
save_checkin(user_id, energy=5.0, stress=7.0, heart_rate=85.0, mood_text="Quite tired")

df = get_checkins(user_id)
print(df)