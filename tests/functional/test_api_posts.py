from jwtblogapp import app

client = app.test_client()


def test_api_posts_user_can_post_message(user_credentials: dict,
                                         user_post_body: dict,
                                         login_url_path: str,
                                         posts_url_path: str
                                         ) -> None:
    result = client.post(login_url_path,
                         json=user_credentials)
    token = result.json["token"]
    result = client.post(posts_url_path,
                         headers={"Authorization": f'Bearer {token}'},
                         json=user_post_body
                         )
    assert result.status_code == 200
    assert 'successfully created' in result.json['msg']


def test_api_posts_user_can_get_posted_message(user_credentials: dict,
                                               user_post_response: dict,
                                               login_url_path: str,
                                               posts_url_path: str
                                               ) -> None:
    result = client.post(login_url_path,
                         json=user_credentials)
    token = result.json["token"]
    result = client.get(posts_url_path,
                        headers={"Authorization": f'Bearer {token}'},
                        )
    assert result.status_code == 200
    assert user_post_response["username"] == result.json["posts"][0]["username"]
    assert user_post_response["post_id"] == result.json["posts"][0]["post_id"]
    assert user_post_response["post_text"] == result.json["posts"][0]["post_text"]


def test_api_posts_user_can_not_post_empty_message(user_credentials: dict,
                                                   user_post_body: dict,
                                                   login_url_path: str,
                                                   posts_url_path: str
                                                   ) -> None:
    result = client.post(login_url_path,
                         json=user_credentials)
    token = result.json["token"]
    result = client.post(posts_url_path,
                         headers={"Authorization": f'Bearer {token}'},
                         json=user_post_body
                         )
    assert result.status_code == 200
    assert 'successfully created' in result.json['msg']
