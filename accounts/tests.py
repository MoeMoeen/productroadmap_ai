# accounts/tests.py
"""
accounts/tests.py

Tests for Accounts app:
- Organization CRUD scoping
- User CRUD scoping
- Permissions and authentication
"""

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import Organization
from accounts.utils import get_user_org

User = get_user_model()


class AccountsAPITestCase(APITestCase):
    def setUp(self):
        # Orgs
        self.org1 = Organization.objects.create(name="Org1")
        self.org2 = Organization.objects.create(name="Org2")

        # Users
        self.superuser = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="pass", organization=self.org1
        )
        self.user1 = User.objects.create_user(
            username="user1", email="user1@example.com", password="pass", organization=self.org1
        )
        self.user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="pass", organization=self.org2
        )

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    # -------------------
    # Organization tests
    # -------------------
    def test_superuser_can_list_all_orgs(self):
        self.authenticate(self.superuser)
        resp = self.client.get("/api/accounts/organizations/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.json()), 2)

    def test_user_can_only_see_own_org(self):
        self.authenticate(self.user1)
        resp = self.client.get("/api/accounts/organizations/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        self.assertEqual(len(data), 1)
        org = get_user_org(self.user1)
        self.assertIsNotNone(org)
        if org is not None:
            self.assertEqual(data[0]["id"], org.pk)

    def test_superuser_can_create_org(self):
        self.authenticate(self.superuser)
        resp = self.client.post("/api/accounts/organizations/", {"name": "Org3"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_user_cannot_create_org(self):
        self.authenticate(self.user1)
        resp = self.client.post("/api/accounts/organizations/", {"name": "HackOrg"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_access_other_org_detail(self):
        self.authenticate(self.user1)
        resp = self.client.get(f"/api/accounts/organizations/{self.org2.pk}/")
        # should not even see it (404, not 403 — avoids leaking existence)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_cannot_update_org(self):
        self.authenticate(self.user1)
        resp = self.client.patch(f"/api/accounts/organizations/{self.org1.pk}/", {"name": "NewName"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    # -------------
    # User tests
    # -------------
    def test_superuser_can_list_all_users(self):
        self.authenticate(self.superuser)
        resp = self.client.get("/api/accounts/users/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(resp.json()), 3)

    def test_user_can_only_see_users_in_their_org(self):
        self.authenticate(self.user1)
        resp = self.client.get("/api/accounts/users/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], self.user1.pk)

    def test_user_cannot_create_user_in_other_org(self):
        self.authenticate(self.user1)
        resp = self.client.post(
            "/api/accounts/users/",
            {
                "username": "bad",
                "email": "bad@example.com",
                "password": "pass12345",
                "organization_id": self.org2.pk,
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_superuser_can_create_user_in_any_org(self):
        self.authenticate(self.superuser)
        resp = self.client.post(
            "/api/accounts/users/",
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "pass12345",
                "organization_id": self.org2.pk,
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.json()
        self.assertEqual(data["organization"]["id"], self.org2.pk)

    def test_user_cannot_update_other_user(self):
        self.authenticate(self.user1)
        resp = self.client.patch(f"/api/accounts/users/{self.user2.pk}/", {"first_name": "Hacker"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)  # not in queryset
