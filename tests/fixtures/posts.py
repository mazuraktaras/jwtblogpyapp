import pytest


@pytest.fixture()
def user_post_body() -> dict:
    return {
        "post_text": "Accelerator is a good software"
    }


@pytest.fixture()
def user_post_response() -> dict:
    return {
        'post_id': 1,
        'user_id': 1,
        'username': 'username@mtv.tv',
        'post_text': 'Accelerator is a good software',
        'likes': 0,
        'dislikes': 0,
        'like_it': 0,
        'created_time': '02-04-2023 15:48:58'
    }
