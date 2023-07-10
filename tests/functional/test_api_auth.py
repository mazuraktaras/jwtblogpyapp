from jwtblogapp import app

client = app.test_client()


def test_if_api_health() -> None:
    result = client.get('/')
    assert result.status_code == 200


def test_api_signup_user(user_credentials: dict,
                         signup_url_path: str) -> None:
    result = client.post(signup_url_path,
                         json=user_credentials)
    assert result.status_code == 200
    assert f'{user_credentials["username"]} successfully signed up' in result.json['msg']


def test_api_signup_user_already_exist(user_credentials: dict,
                                       signup_url_path: str) -> None:
    result = client.post(signup_url_path,
                         json=user_credentials)
    assert result.status_code == 202
    assert f'{user_credentials["username"]} already exist' in result.json['msg']


def test_api_login_user(user_credentials: dict,
                        login_url_path: str) -> None:
    result = client.post(login_url_path,
                         json=user_credentials)
    assert result.status_code == 200
    assert f'{user_credentials["username"]} successfully logged in' in result.json['msg']
    assert isinstance(result.json["token"], str)


def test_api_login_user_wrong_username(user_credentials_wrong_username: dict,
                                       login_url_path: str) -> None:
    result = client.post(login_url_path,
                         json=user_credentials_wrong_username)
    assert result.status_code == 401
    assert 'Bad credentials!' in result.json['msg']


def test_api_login_user_wrong_password(user_credentials_wrong_password: dict,
                                       login_url_path: str) -> None:
    result = client.post(login_url_path,
                         json=user_credentials_wrong_password)
    assert result.status_code == 401
    assert 'Bad credentials!' in result.json['msg']


def test_api_logout_user(user_credentials: dict,
                         login_url_path: str,
                         logout_url_path: str) -> None:
    result = client.post(login_url_path,
                         json=user_credentials)
    token = result.json["token"]
    result = client.post(logout_url_path,
                         headers={"Authorization": f'Bearer {token}'}
                         )
    assert result.status_code == 200
    assert 'logged out' in result.json['msg']


def test_api_logout_user_with_wrong_auth_header(logout_url_path: str) -> None:
    result = client.post(logout_url_path, headers={"Authorization": 'Bearer '})
    assert result.status_code == 422
    assert 'Bad Authorization header' in result.json['msg']


def test_api_logout_user_with_revoked_token(user_credentials: dict,
                                            login_url_path: str,
                                            logout_url_path: str
                                            ) -> None:
    result = client.post(login_url_path,
                         json=user_credentials)
    token = result.json["token"]

    client.post(logout_url_path,
                headers={"Authorization": f'Bearer {token}'}
                )

    result = client.post(logout_url_path,
                         headers={"Authorization": f'Bearer {token}'}
                         )

    assert result.status_code == 401
    assert 'revoked' in result.json['msg']


def test_api_logout_user_expired_token(user_expired_token: dict,
                                       logout_url_path: str
                                       ) -> None:
    token = user_expired_token["token"]
    result = client.post(logout_url_path,
                         headers={"Authorization": f'Bearer {token}'}
                         )

    assert result.status_code == 401
    assert 'expired' in result.json['msg']


def test_blank_api_signup_returned_bad_request_code(signup_url_path) -> None:
    result = client.post(signup_url_path)
    assert result.status_code == 400


def test_api_login_not_allowed_request_method(login_url_path: str) -> None:
    result = client.get(login_url_path)
    assert result.status_code == 405


def test_api_signup_not_allowed_request_method(signup_url_path) -> None:
    result = client.get(signup_url_path)
    assert result.status_code == 405
