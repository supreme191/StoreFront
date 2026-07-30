from rest_framework import status
from django.contrib.auth.models import User
from model_bakery import baker
from Store.models import Collection
import pytest


@pytest.fixture
def create_collection(api_client) :
    def do_create_collection(collection) :
        return api_client.post('/collections/', collection)
    return do_create_collection

@pytest.fixture
def authenticate_user(api_client) :
    def do_authenticate_user(is_staff= False) :
        return api_client.force_authenticate(user=User(is_staff= is_staff))
    return do_authenticate_user


@pytest.mark.django_db
class TestCreateCollection :
    def test_if_user_is_anonymous_returns_401(self, create_collection) :
        response = create_collection({'title' : 'a'})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


    def test_if_user_is_not_admin_returns_403(self, create_collection, authenticate_user) :
        authenticate_user()     # By default is_staff is False
        response = create_collection({'title' : 'a'})
        assert response.status_code == status.HTTP_403_FORBIDDEN


    def test_if_data_is_invalid_returns_400(self, create_collection, authenticate_user) :
        authenticate_user(is_staff= True)
        response = create_collection({'title' : ''})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['title'] is not None


    def test_if_data_is_valid_returns_400(self, create_collection, authenticate_user) :
        authenticate_user(is_staff= True)
        response = create_collection({'title' : 'Tupperware'})
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] > 0


@pytest.mark.django_db
class TestRetrieveCollection :
    def test_if_collection_exists_return_200(self, api_client) :
        collection = baker.make(Collection)

        response = api_client.get(f'/collections/{collection.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            'id' : collection.id,
            'title' : collection.title,
            'product_count' : 0
        }

    def test_if_collection_does_not_exist_returns_404(self, api_client) :
        response = api_client.get(f'/collections/{99999}/')

        assert response.status_code == status.HTTP_404_NOT_FOUND