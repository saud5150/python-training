import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from users.models import User

pytestmark = pytest.mark.django_db

# ------------------ Fixtures ------------------

@pytest.fixture
def admin_user():
    return User.objects.create_superuser(
        email='admin@example.com',
        name='Admin',
        password='admin123',
        role=User.RoleType.ADMIN

    )
@pytest.fixture
def teacher_user():
    return User.objects.create_user(
        email='teacher@example.com',
        name='Teacher',
        password='teacher123',
        role=User.RoleType.TEACHER
    )

@pytest.fixture
def teacher_client(client, teacher_user):
    client.force_authenticate(user=teacher_user)
    return client
@pytest.fixture
def student_user():
    return User.objects.create_user(
        email='student@example.com',
        name='Student',
        password='student123'
    )

@pytest.fixture
def client():
    return APIClient()

@pytest.fixture
def auth_client(client, admin_user):
    client.force_authenticate(user=admin_user)
    return client

@pytest.fixture
def student_client(client, student_user):
    client.force_authenticate(user=student_user)
    return client

# ------------------ Serializer Tests ------------------

from users.serializers import UserSerializer

def test_user_serializer_valid_data():
    data = {
        'email': 'serialtest@example.com',
        'name': 'Ser Test',
        'password': 'pw1234'
    }
    serializer = UserSerializer(data=data)
    assert serializer.is_valid(), serializer.errors
    user = serializer.save()
    assert user.email == data['email']
    assert user.check_password(data['password'])

def test_user_serializer_invalid_email():
    data = {
        'email': 'notanemail',
        'name': 'Test User',
        'password': 'pw12345'
    }
    serializer = UserSerializer(data=data)
    assert not serializer.is_valid()
    assert 'email' in serializer.errors

# ------------------ User Registration API ------------------

def test_admin_can_register_student(auth_client):
    url = reverse('register-student')
    data = {
        'email': 'regstudent@example.com',
        'name': 'Reg Student',
        'password': 'pass1234'
    }
    response = auth_client.post(url, data)
    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.filter(email='regstudent@example.com', role=User.RoleType.STUDENT).count() == 1

def test_admin_can_register_teacher(auth_client):
    url = reverse('register-teacher')
    data = {
        'email': 'regteacher@example.com',
        'name': 'Reg Teacher',
        'password': 'pass1234'
    }
    response = auth_client.post(url, data)
    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.filter(email='regteacher@example.com', role=User.RoleType.TEACHER).count() == 1

def test_admin_can_register_admin(auth_client):
    url = reverse('register-admin')
    data = {
        'email': 'regadmin@example.com',
        'name': 'Reg Admin',
        'password': 'pass1234'
    }
    response = auth_client.post(url, data)
    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.filter(email='regadmin@example.com', role=User.RoleType.ADMIN).count() == 1

def test_registration_requires_admin(client):
    # Not authenticated
    url = reverse('register-student')
    data = {'email': 'noadmin@example.com', 'name': 'NoAdmin', 'password': 'pw'}
    response = client.post(url, data)
    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

# ------------------ User List & Detail Endpoints ------------------

def test_admin_can_list_users(auth_client):
    url = reverse('user-list-create')
    response = auth_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.data, list)

def test_student_cannot_list_users(student_client):
    url = reverse('user-list-create')
    response = student_client.get(url)
    assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED]

def test_admin_can_retrieve_update_delete_user(auth_client, student_user):
    url = reverse('user-detail', args=[str(student_user.id)])

    # Retrieve
    response = auth_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['email'] == student_user.email

    # Update
    patch_data = {'name': 'Updated Student'}
    response = auth_client.patch(url, patch_data)
    assert response.status_code == status.HTTP_200_OK
    student_user.refresh_from_db()
    assert student_user.name == 'Updated Student'

    # Delete
    response = auth_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not User.objects.filter(email=student_user.email).exists()

# ------------------ Profile Endpoint (self only) ------------------

def test_teacher_can_access_profile(teacher_client, teacher_user):
    url = reverse('profile')
    response = teacher_client.get(url)
    assert response.status_code == 200
    assert response.data['email'] == teacher_user.email

    response = teacher_client.patch(url, {'name': 'New Name'})
    assert response.status_code == 200
    teacher_user.refresh_from_db()
    assert teacher_user.name == 'New Name'

def test_admin_can_access_profile(auth_client, admin_user):
    url = reverse('profile')
    response = auth_client.get(url)
    assert response.status_code == 200
    assert response.data['email'] == admin_user.email

def test_student_cannot_access_profile(student_client):
    url = reverse('profile')
    response = student_client.get(url)
    assert response.status_code == 403
    response = student_client.patch(url, {'name': 'Hacker'})
    assert response.status_code == 403


# ------------------ Authentication Endpoints ------------------

def test_token_obtain(admin_user, client):
    url = reverse('token_obtain_pair')
    data = {'email': admin_user.email, 'password': 'admin123'}
    response = client.post(url, data)
    assert response.status_code == 200
    assert 'access' in response.data and 'refresh' in response.data

def test_token_invalid_password(admin_user, client):
    url = reverse('token_obtain_pair')
    data = {'email': admin_user.email, 'password': 'wrongpw'}
    response = client.post(url, data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_token_refresh(admin_user, client):
    obtain_url = reverse('token_obtain_pair')
    refresh_url = reverse('token_refresh')
    obtain_resp = client.post(obtain_url, {'email': admin_user.email, 'password': 'admin123'})
    refresh_token = obtain_resp.data['refresh']
    response = client.post(refresh_url, {'refresh': refresh_token})
    assert response.status_code == 200
    assert 'access' in response.data

# ------------------ Misc and Edge Cases ------------------

def test_user_password_is_hashed(auth_client):
    url = reverse('register-student')
    data = {
        'email': 'plainpwstudent@example.com',
        'name': 'HashedPW Student',
        'password': 'somestrongpw'
    }
    resp = auth_client.post(url, data)
    user = User.objects.get(email=data['email'])
    # Password should not be stored in plaintext
    assert user.password != data['password']
    assert user.check_password(data['password'])

def test_google_login_endpoint_exists(client):
    url = reverse('google_login')
    # No credentials; expect 4xx but not 404
    response = client.post(url)
    assert response.status_code in [400, 401, 403]
