from livekit import api

token = api.AccessToken(api_key="devkey", api_secret="secret") \
    .with_grants(api.VideoGrants(room_join=True, room="my-room")) \
    .with_identity("user1") \
    .to_jwt()

print(token)