import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_root_redirect():
    """Test that root endpoint redirects to static index"""
    # Arrange
    # Act
    response = client.get("/", follow_redirects=False)
    # Assert
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"


def test_get_activities():
    """Test retrieving all activities"""
    # Arrange
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 9  # All predefined activities
    assert "Chess Club" in data
    assert "description" in data["Chess Club"]
    assert "schedule" in data["Chess Club"]
    assert "max_participants" in data["Chess Club"]
    assert "participants" in data["Chess Club"]
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_success():
    """Test successful signup for an activity"""
    # Arrange
    activity = "Chess Club"
    email = "newstudent@mergington.edu"
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    assert f"Signed up {email} for {activity}" == result["message"]
    # Verify added to participants
    get_response = client.get("/activities")
    activities = get_response.json()
    assert email in activities[activity]["participants"]


def test_signup_duplicate():
    """Test signing up twice for same activity fails"""
    # Arrange
    activity = "Programming Class"
    email = "test@mergington.edu"
    # First signup
    client.post(f"/activities/{activity}/signup?email={email}")
    # Act - Second signup
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 400
    result = response.json()
    assert result["detail"] == "Student already signed up for this activity"


def test_signup_invalid_activity():
    """Test signup for non-existent activity fails"""
    # Arrange
    activity = "NonExistent Activity"
    email = "student@mergington.edu"
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 404
    result = response.json()
    assert result["detail"] == "Activity not found"


def test_unregister_success():
    """Test successful unregistration from an activity"""
    # Arrange
    activity = "Gym Class"
    email = "removeme@mergington.edu"
    # First signup
    client.post(f"/activities/{activity}/signup?email={email}")
    # Act
    response = client.delete(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    assert f"Unregistered {email} from {activity}" == result["message"]
    # Verify removed from participants
    get_response = client.get("/activities")
    activities = get_response.json()
    assert email not in activities[activity]["participants"]


def test_unregister_not_signed_up():
    """Test unregistering a student not signed up fails"""
    # Arrange
    activity = "Tennis Club"
    email = "notsignedup@mergington.edu"
    # Act
    response = client.delete(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 400
    result = response.json()
    assert result["detail"] == "Student not signed up for this activity"


def test_unregister_invalid_activity():
    """Test unregister from non-existent activity fails"""
    # Arrange
    activity = "Invalid Activity"
    email = "student@mergington.edu"
    # Act
    response = client.delete(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 404
    result = response.json()
    assert result["detail"] == "Activity not found"


def test_activities_data_integrity():
    """Test that activities data structure is correct"""
    # Arrange
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    data = response.json()
    for activity_name, details in data.items():
        assert "description" in details
        assert "schedule" in details
        assert "max_participants" in details
        assert "participants" in details
        assert isinstance(details["max_participants"], int)
        assert isinstance(details["participants"], list)
        assert details["max_participants"] > 0