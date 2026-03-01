from jsonschema import validate
import pytest
import schemas
import api_helpers
from hamcrest import assert_that, is_

def test_pet_schema():
    response = api_helpers.get_api_data("/pets/1")
    assert response.status_code == 200
    validate(instance=response.json(), schema=schemas.pet)


@pytest.mark.parametrize("status", ["available", "pending", "sold"])
def test_find_by_status_200(status):

    response = api_helpers.get_api_data(
        "/pets/findByStatus",
        params={"status": status}
    )

    assert response.status_code == 200

    for pet in response.json():
        assert_that(pet["status"], is_(status))
        validate(instance=pet, schema=schemas.pet)


@pytest.mark.parametrize("pet_id", [999, -1])
def test_get_by_id_404(pet_id):

    response = api_helpers.get_api_data(f"/pets/{pet_id}")
    assert response.status_code == 404
