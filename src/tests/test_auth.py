
def test_signup(client):
    response = client.post("/auth/signup/microsoft", follow_redirects=True)
    print(response)
