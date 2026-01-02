from django.contrib.auth.models import AbstractUser
from django.test import Client
from django.urls import reverse


def test_not_logged_in(client: Client):
    checks_url = reverse("health-checks")

    response = client.get(checks_url)

    assert response.status_code == 403


def test_view_injected_collector(client: Client, django_user_model: AbstractUser):
    checks_url = reverse("health-checks")  # Uses injected checks collector.
    user = django_user_model.objects.create_user(
        username="johndoe", password="verysecret"
    )
    client.force_login(user)

    response = client.get(checks_url)

    assert response.status_code == 200
    assert response.json() == [
        {
            "success": False,
            "verbose_name": "Dummy fail",
            "identifier": "dummy_fail",
            "message": "Everything is sad.",
            "extra": {"info": "bla"},
        }
    ]


def test_view_with_success(client: Client, django_user_model: AbstractUser):
    checks_url = reverse("health-checks")  # Uses injected checks collector.
    user = django_user_model.objects.create_user(
        username="johndoe", password="verysecret"
    )
    client.force_login(user)

    # TODO: change when we drop support for Django 4.2
    # response = client.get(checks_url, query_params={"include_success": "yes"})
    response = client.get(f"{checks_url}?include_success=yes")

    assert response.status_code == 200
    assert response.json() == [
        {
            "success": True,
            "identifier": "dummy",
            "verbose_name": "Dummy",
            "message": "Everything is great.",
            "extra": None,
        },
        {
            "success": False,
            "identifier": "dummy_fail",
            "verbose_name": "Dummy fail",
            "message": "Everything is sad.",
            "extra": {"info": "bla"},
        },
    ]
