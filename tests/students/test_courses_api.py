import pytest
from rest_framework.test import APIClient
from students.models import Student, Course
from model_bakery import baker


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def student_factory():
    def factory(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)

    return factory


@pytest.fixture
def course_factory():
    def factory(*args, **kwargs):
        return baker.make(Course, *args, **kwargs)

    return factory


@pytest.mark.django_db
def test_get_first_course(client, course_factory, student_factory):
    #Arrange
    courses = course_factory(_quantity=10)

    #Act
    response = client.get('/api/v1/courses/', {'id': courses[0].id})
    data = response.json()

    #Assert
    assert response.status_code == 200
    assert data[0]['id'] == courses[0].id
    assert data[0]['name'] == courses[0].name


@pytest.mark.django_db
def test_get_courses_list(client, course_factory):
    # Arrange
    courses = course_factory(_quantity=10)

    # Act
    response = client.get('/api/v1/courses/')
    data = response.json()

    # Assert
    assert response.status_code == 200
    for ind, c in enumerate(data):
        assert c['id'] == courses[ind].id
        assert c['name'] == courses[ind].name


@pytest.mark.django_db
def test_filter_id_courses(client, course_factory):
    # Arrange
    courses = course_factory(_quantity=100)
    id = courses[0].id

    # Act
    response = client.get(f'/api/v1/courses/?id={id}')
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert data[0]['name'] == courses[0].name


@pytest.mark.django_db
def test_filter_name_courses(client, course_factory):
    # Arrange
    courses = course_factory(_quantity=100)
    name = courses[0].name

    # Act
    response = client.get(f'/api/v1/courses/?name={name}')
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert data[0]['id'] == courses[0].id


@pytest.mark.django_db
def test_create_course(client, course_factory, student_factory):
    # Arrange
    count = Course.objects.count()

    students = student_factory(_quantity=10)
    ids_students = []
    for s in students:
        ids_students.append(s.id)

    json_data = {'name': 'Python Development', 'students': ids_students}

    # Act
    post_response = client.post('/api/v1/courses/', data=json_data)

    #Assert
    assert post_response.status_code == 201
    assert Course.objects.count() == count + 1


@pytest.mark.django_db
def test_update_course(client, course_factory):
    # Arrange
    courses = course_factory(_quantity=10)
    id = courses[0].id
    new_data = {'name': 'Django'}

    # Act
    update_response = client.patch(f'/api/v1/courses/{id}/', data=new_data)
    get_response = client.get(f'/api/v1/courses/{id}/')
    data = get_response.json()

    # Assert
    assert update_response.status_code == 200
    assert get_response.status_code == 200
    assert data['name'] == new_data['name']


@pytest.mark.django_db
def test_remove_course(client, course_factory):
    # Arrange
    courses = course_factory(_quantity=3)
    id = courses[0].id
    count = Course.objects.count()

    # Act
    response = client.delete(f'/api/v1/courses/{id}/')

    # Assert
    assert response.status_code == 204
    assert Course.objects.count() == count - 1